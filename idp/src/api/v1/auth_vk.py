from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from services.keycloak_client import KeycloackClient, get_keycloak_service
from services.vk_client import VKClient, get_vk_client

router = APIRouter()


@router.get("/")
async def start(client: VKClient = Depends(get_vk_client)):
    url = await client.get_auth_url()
    return RedirectResponse(url)


@router.get("/endpoint")
async def endpoint(
    code: str,
    expires_in: int,
    device_id: str,
    state: str,
    type: str,
    client: VKClient = Depends(get_vk_client),
    keycloak: KeycloackClient = Depends(get_keycloak_service),
):
    if type != "code_v2":
        raise ValueError("Unsupported code type")

    token = await client.exchange(state, code, device_id)
    user = await keycloak.find_user_by_idp("vk", str(token.user_id))
    if not user:
        username = f"vk_{token.user_id}"
        await keycloak.create_user(username)
        user = await keycloak.get_user_with_username(username)
        if not user:
            raise ValueError("Failed to create a user")
        await keycloak.federate_idp(user.id, "vk", str(token.user_id), username)

    return await keycloak.token_exchange_direct_naked_impersonation(user.id)
