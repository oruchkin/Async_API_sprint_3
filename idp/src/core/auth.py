from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional, Dict, Any
from services.keycloak_client import KeycloackClient, get_keycloak_service


class TokenData(BaseModel):
    uuid: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    exp: Optional[int] = None
    iat: Optional[int] = None
    token_details: Optional[Dict[str, Any]] = None
    roles: Optional[list[str]] = None


security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                           keycloak: KeycloackClient = Depends(get_keycloak_service)) -> TokenData:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:

        public_key = await keycloak.get_realm_public_key()

        payload = jwt.decode(token, public_key, algorithms=["RS256"])
        #TODO за 123 вызвать метод verify_token
        # payload = 123
        uuid: str = payload.get("sub")
        username: str = payload.get("preferred_username")
        email: str = payload.get("email")
        email_verified: bool = payload.get("email_verified")
        exp: int = payload.get("exp")
        iat: int = payload.get("iat")

        if username is None:
            raise credentials_exception

        token_data = TokenData(
            uuid=uuid,
            username=username,
            email=email,
            email_verified=email_verified,
            exp=exp,
            iat=iat,
            token_details=payload
        )
    except JWTError:
        raise credentials_exception
    return token_data
