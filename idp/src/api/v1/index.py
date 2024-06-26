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
    return current_user.model_dump()
