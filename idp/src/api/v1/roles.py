from uuid import UUID

import api.v1.schemas as schemas
from fastapi import APIRouter, Depends
from services.keycloak_client import KeycloackClient, get_keycloak_service

router = APIRouter()


@router.get(
    "/",
    response_model=list[schemas.Role],
    summary="List all roles",
    description="Returns all roles in the system",
)
async def list_roles(
    keycloak: KeycloackClient = Depends(get_keycloak_service),
) -> list[schemas.Role]:
    roles = await keycloak.list_roles()
    mapped = [schemas.Role.model_validate(role) for role in roles]
    return mapped


@router.post(
    "/",
    response_model=schemas.Role,
    summary="Create new role",
    description="Returns created role",
)
async def create_role(
    model: schemas.CreateRole,
    keycloak: KeycloackClient = Depends(get_keycloak_service),
) -> schemas.Role:
    await keycloak.create_role(model.name, model.description)
    roles = await keycloak.list_roles()
    role = next(r for r in roles if r.name == model.name)
    return schemas.Role.model_validate(role)


@router.delete(
    "/{role_id}",
    response_model=None,
    summary="Delete role by id",
    description="Do not return anything",
)
async def delete_role(
    role_id: UUID,
    keycloak: KeycloackClient = Depends(get_keycloak_service),
) -> None:
    await keycloak.delete_role(role_id)
