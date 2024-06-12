from http import HTTPStatus

from fastapi import APIRouter
from urllib3 import HTTPResponse

router = APIRouter()


@router.get("/")
def stub():
    HTTPResponse("", status=HTTPStatus.OK)
