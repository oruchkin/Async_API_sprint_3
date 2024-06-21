import api.v1.schemas as schemas
from fastapi import APIRouter, Depends
from services.keycloak_client import KeycloackClient, get_keycloak_service

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
