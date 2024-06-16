from typing import Literal

import api.v1.schemas as schemas
from fastapi import APIRouter, Depends
from services.keycloak_client import KeycloackClient, get_keycloak_service

router = APIRouter()


SORT_OPTION = Literal["imdb_rating", "-imdb_rating"]


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


@router.post("/", summary="Create user", description="Creates new user")
async def create_user(
    user: schemas.CreateUser,
    keycloak: KeycloackClient = Depends(get_keycloak_service),
) -> schemas.User:
    await keycloak.create_user(user.email, user.password, user.username)
    user = await keycloak.get_user_with_email(user.email)
    return schemas.User.model_validate(user)
