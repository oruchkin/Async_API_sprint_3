from http import HTTPStatus

from fastapi import APIRouter, Depends
from urllib3 import HTTPResponse
from core.auth import get_current_user, TokenData

router = APIRouter()


@router.get("/")
def stub():
    HTTPResponse("", status=HTTPStatus.OK)


@router.get("/auth_user")
async def protected_route(current_user: TokenData = Depends(get_current_user)):
    payload = {
        "uuid": current_user.uuid,
        "username": current_user.username,
        "email": current_user.email,
        "email_verified": current_user.email_verified,
        "exp": current_user.exp,
        "iat": current_user.iat,
        "token_details": current_user.token_details,
    }
    return payload
