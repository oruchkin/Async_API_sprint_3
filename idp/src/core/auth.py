import logging.config
import uuid
from http import HTTPStatus
from typing import Optional

from core.verification import verify_token
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from services.oidc_client import OIDCClient, get_oidc_service

logger = logging.getLogger(__name__)


class TokenData(BaseModel):
    user_id: uuid.UUID
    username: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    roles: list[str] = []


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
        if user_id := payload.get("sub"):
            roles = _extract_roles(payload, oidc_client.client_id)

            token_data = TokenData(
                user_id=uuid.UUID(user_id),
                username=payload.get("preferred_username"),
                email=payload.get("email"),
                email_verified=payload.get("email_verified"),
                roles=roles,
            )

            return token_data
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
        credentials: HTTPAuthorizationCredentials = Depends(bearer_security),
    ) -> TokenData:
        if not user:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

        if self._is_strict:
            if not await oidc_client.introspect(credentials.credentials):
                raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

        if self._roles:
            has_role = any(role for role in self._roles if role in user.roles)
            if not has_role:
                raise HTTPException(status_code=HTTPStatus.FORBIDDEN)

        return user
