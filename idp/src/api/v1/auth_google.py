from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from services.oidc_client import OIDCClient, get_oidc_service

router = APIRouter()

RETURN_URI = "http://localhost:8000/api/v1/auth/google/endpoint"


@router.get("/")
async def start(request: Request, oidc: OIDCClient = Depends(get_oidc_service)):
    global RETURN_URI
    RETURN_URI = f"{request.url}endpoint"
    url = oidc.code_flow_url("google", RETURN_URI)
    return RedirectResponse(url)


@router.get("/endpoint")
async def endpoint(
    session_state: str,
    code: str,
    iss: str,
    oidc: OIDCClient = Depends(get_oidc_service),
):
    return await oidc.code_flow(code, RETURN_URI)
