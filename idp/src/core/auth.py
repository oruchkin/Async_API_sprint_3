from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional, Dict, Any
from services.keycloak_client import KeycloackClient, get_keycloak_service
from core.verification import verify_token
from services.oidc_client import OIDCClient, get_oidc_service


class TokenData(BaseModel):
    uuid: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    roles: Optional[list[str]] = None


security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                           oidc_client: OIDCClient = Depends(get_oidc_service),
                           keycloak: KeycloackClient = Depends(get_keycloak_service)) -> TokenData:
    payload = await verify_token(oidc_client, credentials.credentials)

    #TODO: добавть еще сюда входящие переменную роли и что-то делать если ролей на пользователей нет

    user_id = payload.get("sub")
    roles_response = await keycloak.list_user_roles(user_id)
    roles = [role.name for role in roles_response]

    token_data = TokenData(
        uuid=user_id,
        username=payload.get("preferred_username"),
        email=payload.get("email"),
        email_verified=payload.get("email_verified"),
        roles=roles
    )

    return token_data
