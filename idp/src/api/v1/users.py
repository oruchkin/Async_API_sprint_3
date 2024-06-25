from uuid import UUID

import api.v1.schemas as schemas
import services.errors as errors
from fastapi import APIRouter, Depends
from services.keycloak_client import KeycloackClient, get_keycloak_service

from .utils import handle_keycloak_error

router = APIRouter()


@router.post(
    "/token",
    summary="Authenticate user",
    description="Returns token by login and password",
)
async def user_token(
    login: schemas.Login,
    keycloak: KeycloackClient = Depends(get_keycloak_service),
) -> schemas.Token:
    token = await keycloak.authenticate(login.login, login.password)
    return schemas.Token.model_validate(token)


@router.post(
    "/introspect",
    summary="Validate user's token",
    description="Flag indicating if token is valid",
)
async def user_introspect_token(
    keycloak: KeycloackClient = Depends(get_keycloak_service),
) -> schemas.TokenIntrospection:
    token = ""  # TODO: token from the header
    is_valid = await keycloak.user_token_introspect(token)
    return schemas.TokenIntrospection(valid=is_valid)


@router.post(
    "/logout",
    summary="Logout user from current session",
    description="Doesn't return anything",
)
async def user_logout(
    token: schemas.RefreshToken,
    keycloak: KeycloackClient = Depends(get_keycloak_service),
) -> None:
    await keycloak.user_logout(token.refresh_token)


@router.post(
    "/logout/{user_id}",
    summary="Logout user from all sessions",
    description="Doesn't return anything",
)
async def user_logout_all(
    user_id: UUID,
    keycloak: KeycloackClient = Depends(get_keycloak_service),
) -> None:
    # TODO: Check if self or admin
    await keycloak.user_logout_all(user_id)


@router.post(
    "/refresh",
    summary="Refresh token",
    description="Returns token by the refresh token",
)
async def user_token_refresh(
    token: schemas.RefreshToken,
    keycloak: KeycloackClient = Depends(get_keycloak_service),
) -> schemas.Token:
    access_token = await keycloak.refresh(token.refresh_token)
    return schemas.Token.model_validate(access_token)


@router.post(
    "/reset",
    summary="Reset password",
    description="Reset user's password",
)
async def reset_password(
    reset: schemas.ResetPassword,
    keycloak: KeycloackClient = Depends(get_keycloak_service),
) -> None:
    raise ValueError("We need user id from token")
    await keycloak.reset_password("user-id", reset.password)


@router.get(
    "/",
    response_model=list[schemas.User],
    summary="List all users",
    description="Returns all users in the system",
)
async def list_users(
    keycloak: KeycloackClient = Depends(get_keycloak_service),
) -> list[schemas.User]:
    users = await keycloak.list_users()
    mapped = [schemas.User.model_validate(user) for user in users]
    return mapped


@router.post("/", summary="Create user", description="Returns created user")
async def create_user(
    user: schemas.CreateUser,
    keycloak: KeycloackClient = Depends(get_keycloak_service),
) -> schemas.User:
    await keycloak.create_user(user.email, user.password, user.username)
    createdUser = await keycloak.get_user_with_email(user.email)
    return schemas.User.model_validate(createdUser)


@router.get(
    "/{user_id}/roles",
    response_model=list[schemas.Role],
    summary="Get user's roles",
    description="Returns user's roles",
)
async def get_user_roles(
    user_id: UUID,
    keycloak: KeycloackClient = Depends(get_keycloak_service),
) -> list[schemas.Role]:
    # TODO: Check if admin
    try:
        roles = await keycloak.list_user_roles(user_id)
        mapped = [schemas.Role.model_validate(role) for role in roles]
        return mapped
    except errors.KeycloakError as e:
        raise handle_keycloak_error(e)


@router.get(
    "/{user_id}/sessions",
    response_model=list[schemas.UserSession],
    summary="Get user's sessions",
    description="Returns user's sessions",
)
async def get_user_sessions(
    user_id: UUID,
    keycloak: KeycloackClient = Depends(get_keycloak_service),
) -> list[schemas.UserSession]:
    # TODO: Check if admin or self
    sessions = await keycloak.list_user_sessions(user_id)
    mapped = [schemas.UserSession.model_validate(session) for session in sessions]
    return mapped
