from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional


class TokenData(BaseModel):
    username: Optional[str] = None


SECRET_KEY = ""
ALGORITHM = "RS256"

PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApJ6YGuqSEHCt25NGmdY5M4eJ41zGlL8MVY15Iq76RT+MgJIhegHlYRgulp28J7fs5ZlkjhrJrkylFU4DdCkQprSNO0fQMQgROdtxFr04Y8tiE8NmP8XabwZJ0buHcOs0hxNTS9yEWySeF+NsHyNHqsfcjJJntik1744TLi4Tu/W1iq2QF4pzk2ygP13K1zbvLK6YZjQaejXgAM8G3zPiIPBHvEl1EjYmpBDFntSQYcR6Up2kF0Flwyq0mzHiRytXP3dKDI5uDVSIBv91AHfzJfqpaL32FetRTbd4H6odXfyK1u9DJ2q+20F2Q+j/iDifsEwLdp+6qxt2WHJhTrnRMQIDAQAB
-----END PUBLIC KEY-----
"""


security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    token = credentials.credentials
    print("token")
    print(token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("preferred_username")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return token_data
