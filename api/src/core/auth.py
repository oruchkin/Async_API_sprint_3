import logging.config
import uuid
from http import HTTPStatus
from typing import Optional

from core.verification import verify_token
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from services.oidc_client import OIDCClient, get_oidc_service
from src.services.idp_client import IDPClientService, get_idp_client_service
from starlette.authentication import AuthCredentials, AuthenticationBackend, SimpleUser

logger = logging.getLogger(__name__)


class TokenData(BaseModel):
    user_id: uuid.UUID
    username: str
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    roles: list[str] = []

    @staticmethod
    def from_token(token: dict, client_id: str) -> "TokenData":
        roles = _extract_roles(token, client_id)
        return TokenData(
            user_id=uuid.UUID(token["sub"]),
            username=token["preferred_username"],
            email=token.get("email"),
            email_verified=token.get("email_verified"),
            roles=roles,
        )


class User(SimpleUser):
    def __init__(self, token_data: TokenData) -> None:
        super().__init__(token_data.username)

        self.token = token_data

    @property
    def id(self) -> uuid.UUID:
        return self.token.user_id


bearer_security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_security),
    oidc_client: OIDCClient = Depends(get_oidc_service),
) -> TokenData | None:
    """
    Supposed to be used when user is optional
    """

    try:
        payload = await verify_token(oidc_client, credentials.credentials)
        if payload.get("sub"):
            return TokenData.from_token(payload, oidc_client.client_id)
    except Exception as ex:
        logger.info(ex)

    return None


def _extract_roles(payload: dict, client_id: str) -> list[str]:
    return payload.get("resource_access", {}).get(client_id, {}).get("roles") or []


class AuthorizationProvider:
    def __init__(self, roles: list[str] = [], is_strict=False):
        self._roles = roles
        self._is_strict = is_strict

    async def __call__(
        self,
        user: TokenData | None = Depends(get_current_user),
        oidc_client: OIDCClient = Depends(get_oidc_service),
        idp_client: IDPClientService = Depends(get_idp_client_service),
        credentials: HTTPAuthorizationCredentials = Depends(bearer_security),
    ) -> TokenData:
        if not user:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

        if self._is_strict:
            if not await idp_client.introspect(credentials.credentials):
                raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

        if self._roles:
            has_role = any(role for role in self._roles if role in user.roles)
            if not has_role:
                raise HTTPException(status_code=HTTPStatus.FORBIDDEN)

        return user


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        if auth := conn.headers.get("Authorization"):
            try:
                scheme, credentials = auth.split()
                if scheme.lower() != "bearer":
                    return

                oidc_client = get_oidc_service()
                payload = await verify_token(oidc_client, credentials)
                token = TokenData.from_token(payload, oidc_client.client_id)
                return AuthCredentials(["authenticated"]), User(token)

            except (ValueError, UnicodeDecodeError) as ex:
                logger.error(ex)

        return None
