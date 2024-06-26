from uuid import UUID

import api.v1.schemas as schemas
from fastapi import APIRouter, Depends
from services.keycloak_client import KeycloackClient, get_keycloak_service

from .utils import convert_to_http_error

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
    try:
        await keycloak.create_role(model.name, model.description)
        roles = await keycloak.list_roles()
        role = next(r for r in roles if r.name == model.name)
        return schemas.Role.model_validate(role)
    except Exception as e:
        raise convert_to_http_error(e)


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
    try:
        await keycloak.delete_role(role_id)
    except Exception as e:
        raise convert_to_http_error(e)


@router.put(
    "/{role_id}",
    response_model=None,
    summary="Modify role by id",
    description="Returns modified role",
)
async def modify_role(
    role_id: UUID,
    model: schemas.RoleModify,
    keycloak: KeycloackClient = Depends(get_keycloak_service),
) -> schemas.Role:
    try:
        role = await keycloak.get_role(role_id)
        role.description = model.description
        await keycloak.modify_role(role)
        return schemas.Role.model_validate(role)
    except Exception as e:
        raise convert_to_http_error(e)


@router.post(
    "/{role_id}/users",
    summary="Assign role to users by id",
    description="Do not return anything",
)
async def assign_role_to_users(
    role_id: UUID,
    assign_model: schemas.RoleAssign,
    keycloak: KeycloackClient = Depends(get_keycloak_service),
) -> None:
    role = await keycloak.get_role(role_id)
    for user in assign_model.users:
        await keycloak.set_user_role(user, role)


@router.delete(
    "/{role_id}/users/{user_id}",
    summary="remove role from user",
    description="Do not return anything",
)
async def delete_role_for_user(
    role_id: UUID,
    user_id: UUID,
    keycloak: KeycloackClient = Depends(get_keycloak_service),
) -> None:
    try:
        role = await keycloak.get_role(role_id)
        await keycloak.remove_user_role(user_id, role)
    except Exception as e:
        raise convert_to_http_error(e)
