from uuid import UUID

from core.auth import AuthorizationProvider, TokenData, bearer_security
from core.verification import verify_token
from fastapi import APIRouter, Depends, Form
from fastapi.security import HTTPAuthorizationCredentials
from services.keycloak_client import KeycloackClient, get_keycloak_service
from services.oidc_client import OIDCClient, get_oidc_service

import api.v1.schemas as schemas

router = APIRouter()


@router.get("/me")
async def protected_route(user: TokenData = Depends(AuthorizationProvider(is_strict=True))):
    return user.model_dump()


@router.post("/login", summary="Old school login")
async def login(
    login: str = Form(...),
    password: str = Form(...),
    oidc: OIDCClient = Depends(get_oidc_service),
) -> TokenData:
    token = await oidc.password_flow(login, password)
    payload = await verify_token(oidc, token.access_token)
    return TokenData.from_token(payload, oidc.client_id)


@router.post(
    "/token",
    summary="Authenticate user",
    description="Returns token by login and password",
)
async def user_token(
    login: str = Form(...),
    password: str = Form(...),
    oidc: OIDCClient = Depends(get_oidc_service),
) -> schemas.Token:
    token = await oidc.password_flow(login, password)
    return schemas.Token.model_validate(token)


@router.post(
    "/introspect",
    summary="Validate user's token",
    description="Flag indicating if token is valid",
)
async def user_introspect_token(
    oidc: OIDCClient = Depends(get_oidc_service),
    bearer: HTTPAuthorizationCredentials = Depends(bearer_security),
) -> schemas.TokenIntrospection:
    is_valid = await oidc.introspect(bearer.credentials)
    return schemas.TokenIntrospection(valid=is_valid)


@router.post(
    "/logout",
    summary="Logout user from the current session",
    description="Doesn't return anything",
)
async def user_logout(
    token: schemas.RefreshToken,
    oidc: OIDCClient = Depends(get_oidc_service),
    _=Depends(AuthorizationProvider()),
) -> None:
    await oidc.logout(token.refresh_token)


@router.post(
    "/logout/all",
    summary="Logout user from all sessions",
    description="Doesn't return anything",
)
async def user_logout_me_all(
    keycloak: KeycloackClient = Depends(get_keycloak_service),
    user: TokenData = Depends(AuthorizationProvider()),
) -> None:
    await keycloak.user_logout_all(user.user_id)


@router.post(
    "/logout/{user_id}",
    summary="Logout user from all sessions",
    description="Doesn't return anything",
)
async def user_logout_all(
    user_id: UUID,
    keycloak: KeycloackClient = Depends(get_keycloak_service),
    _=Depends(AuthorizationProvider(roles=["admin"])),
) -> None:
    await keycloak.user_logout_all(user_id)


@router.post(
    "/refresh",
    summary="Refresh token",
    description="Returns token by the refresh token",
)
async def user_token_refresh(
    token: schemas.RefreshToken,
    oidc: OIDCClient = Depends(get_oidc_service),
) -> schemas.Token:
    access_token = await oidc.refresh(token.refresh_token)
    return schemas.Token.model_validate(access_token)


@router.post(
    "/reset",
    summary="Reset password",
    description="Reset user's password",
)
async def reset_password(
    reset: schemas.ResetPassword,
    keycloak: KeycloackClient = Depends(get_keycloak_service),
    user: TokenData = Depends(AuthorizationProvider()),
) -> None:
    await keycloak.reset_password(user.user_id, reset.password)


@router.get(
    "/",
    response_model=list[schemas.User],
    summary="List all users",
    description="Returns all users in the system",
)
async def list_users(
    keycloak: KeycloackClient = Depends(get_keycloak_service),
    _=Depends(AuthorizationProvider(roles=["admin"])),
) -> list[schemas.User]:
    users = await keycloak.list_users()
    mapped = [schemas.User.model_validate(user) for user in users]
    return mapped


@router.post("/", summary="Create user", description="Returns created user")
async def create_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    keycloak: KeycloackClient = Depends(get_keycloak_service),
) -> schemas.User:
    await keycloak.create_user(username, email, password)
    created_user = await keycloak.get_user_with_email(email)
    return schemas.User.model_validate(created_user)


@router.get("/{user_id}", response_model=schemas.User, summary="Get user info")
async def get_user(
    user_id: UUID,
    keycloak: KeycloackClient = Depends(get_keycloak_service),
) -> schemas.User:
    user = await keycloak.get_user(user_id)
    return schemas.User.model_validate(user)


@router.get(
    "/{user_id}/roles",
    response_model=list[schemas.Role],
    summary="Get user's roles",
    description="Returns user's roles",
)
async def get_user_roles(
    user_id: UUID,
    keycloak: KeycloackClient = Depends(get_keycloak_service),
    _=Depends(AuthorizationProvider(roles=["admin"])),
) -> list[schemas.Role]:
    roles = await keycloak.list_user_roles(user_id)
    mapped = [schemas.Role.model_validate(role) for role in roles]
    return mapped


@router.get(
    "/sessions",
    response_model=list[schemas.UserSession],
    summary="Get user's own sessions",
    description="Returns collection of sessions",
)
async def get_user_my_sessions(
    keycloak: KeycloackClient = Depends(get_keycloak_service),
    user: TokenData = Depends(AuthorizationProvider()),
) -> list[schemas.UserSession]:
    sessions = await keycloak.list_user_sessions(user.user_id)
    mapped = [schemas.UserSession.model_validate(session) for session in sessions]
    return mapped


@router.get(
    "/{user_id}/sessions",
    response_model=list[schemas.UserSession],
    summary="Get sessions of the user by user id",
    description="Returns collection of sessions",
)
async def get_user_sessions(
    user_id: UUID,
    keycloak: KeycloackClient = Depends(get_keycloak_service),
    _=Depends(AuthorizationProvider(roles=["admin"])),
) -> list[schemas.UserSession]:
    sessions = await keycloak.list_user_sessions(user_id)
    mapped = [schemas.UserSession.model_validate(session) for session in sessions]
    return mapped
