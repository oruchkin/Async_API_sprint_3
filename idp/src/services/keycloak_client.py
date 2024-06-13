from typing import Any
from core.settings import KeycloakSettings
import aiohttp

from services.keycloack_endpoints import KeycloakEndpoints

class KeycloackClient:
    _access_token: dict[str, Any] | None = None

    def __init__(self, settings: KeycloakSettings):
        self._settings = settings
        self._endpoints = KeycloakEndpoints(settings)
        self._timeout = aiohttp.ClientTimeout(total=None, sock_connect=5, sock_read=5)

    async def create_user(self, email: str) -> None:
        payload = {
            "email": "testuser@gmail.com",
            "emailVerified": False,
            "enabled": False
        }
        headers = {
            "Authorization": await self._get_auth_header(),
            "Content-Type": "application/json"
        }

        url = self._endpoints.create_user()
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.post(url, data=payload) as client:
                json_body = await client.json()
                print(json_body)

    async def _get_auth_header(self, throw_if_empty: bool = False) -> str:
        if self._access_token:
            return f"{self._access_token['token_type']} {self._access_token['access_token']}"
        
        if throw_if_empty:
            raise ValueError("Failed")

        await self.auth()
        return await self._get_auth_header(True)

    async def discovery(self) -> None:
        url = self._endpoints.oidc_discovery()
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            async with session.get(url) as client:
                json_body = await client.json()
                self._endpoints.oidc_set_discovery(json_body)

    async def auth(self) -> None:
        if not self._endpoints.oidc_has_discovery():
            await self.discovery()

        url = self._endpoints.oidc_token()
        headers = { "Content-Type": "application/x-www-form-urlencoded" }
        payload = {
            "grant_type": "client_credentials",
            "client_id": self._settings.client,
            "client_secret": self._settings.secret
        }
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.post(url, data=payload) as client:
                self._access_token = await client.json()
