from typing import Any

import aiohttp
from core.settings import KeycloakSettings
from models.token_model import TokenModel
from services.keycloack_endpoints import KeycloakEndpoints


class KeycloackClient:
    _access_token: dict[str, Any] | None = None

    def __init__(self, settings: KeycloakSettings):
        self._settings = settings
        self._endpoints = KeycloakEndpoints(settings)
        self._timeout = aiohttp.ClientTimeout(total=None, sock_connect=5, sock_read=5)

    async def create_role(self, name: str) -> None:
        payload = {
            "name": name,
            "clientRole": False
        }
        headers = await self._get_request_headers()
        url = self._endpoints.roles(self._settings.client)
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.post(url, json=payload) as client:
                response = await client.json()
                print(response)

    async def get_id(self) -> str:
        # That's wrong!!!
        headers = await self._get_request_headers()
        url = self._endpoints.client_id(self._settings.client)
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.get(url) as client:
                response = await client.json()
                print(response)

    async def list_users(self) -> list[dict]:
        """
        Get all users
        """
        url = self._endpoints.list_users()
        headers = await self._get_request_headers()
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.get(url) as client:
                return await client.json()

    async def create_user(self, email: str, password: str, username: str | None = None) -> None:
        """
        Creates new user
        """
        # username is required
        payload = {
            "username": username or email,
            "email": email,
            "emailVerified": False,
            "enabled": True,
            "groups": [],
            "requiredActions": [],
            "credentials": [{"type": "password", "value": password, "temporary": False}]
        }
        url = self._endpoints.create_user()
        headers = await self._get_request_headers()
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.post(url, json=payload) as client:
                if not client.ok:
                    json_body = await client.json()
                    raise ValueError(json_body)
                
    async def reset_password(self, user_id: str, password: str) -> None:
        """
        Reset user's password by `user_id`. Don't forget to verify old password beforehand.
        """
        payload = {"temporary": False, "type": "password", "value": password}
        url = self._endpoints.reset_user_password(user_id)
        headers = await self._get_request_headers()
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.post(url, json=payload) as client:
                if not client.ok:
                    json_body = await client.json()
                    raise ValueError(json_body)
                
    async def authenticate(self, username: str, password: str) -> TokenModel:
        payload = {
            "client_id": self._settings.client,
            "client_secret": self._settings.secret,
            "scope": "openid roles profile",

            "grant_type": "password",
            "username": username,
            "password": password,
        }
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        url = (await self._get_endpoints()).oidc_token()
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.post(url, data=payload) as client:
                # 'error': 'invalid_grant', 'error_description': 'Invalid user credentials'
                if not client.ok:
                    json_body: dict = await client.json()
                    raise ValueError(json_body["error"])

                raw = await client.text()
                return TokenModel.model_validate_json(raw)

    async def refresh(self, refresh_token: str) -> TokenModel:
        payload = {
            "client_id": self._settings.client,
            "client_secret": self._settings.secret,
            "scope": "openid roles profile",
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        url = self._endpoints.oidc_token()
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.post(url, data=payload) as client:
                # 'error': 'invalid_grant', 'error_description': 'Invalid user credentials'
                if not client.ok:
                    json_body: dict = await client.json()
                    raise ValueError(json_body["error"])

                raw = await client.text()
                return TokenModel.model_validate_json(raw)

    async def _get_request_headers(self) -> dict:
        return {
            "Authorization": await self._get_auth_header_value(),
            "Content-Type": "application/json"
        }

    async def _get_auth_header_value(self, throw_if_empty: bool = False) -> str:
        if self._access_token:
            return f"{self._access_token['token_type']} {self._access_token['access_token']}"

        if throw_if_empty:
            raise ValueError("Failed")

        await self._auth()
        return await self._get_auth_header_value(True)

    async def discovery(self) -> None:
        url = self._endpoints.oidc_discovery()
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            async with session.get(url) as client:
                json_body = await client.json()
                self._endpoints.oidc_set_discovery(json_body)

    async def _auth(self) -> None:
        if not self._endpoints.oidc_has_discovery():
            await self.discovery()

        url = self._endpoints.oidc_token()
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "grant_type": "client_credentials",
            "client_id": self._settings.client,
            "client_secret": self._settings.secret
        }
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.post(url, data=payload) as client:
                self._access_token = await client.json()

    async def _get_endpoints(self) -> KeycloakEndpoints:
        if not self._endpoints.oidc_has_discovery():
            await self.discovery()
        
        return self._endpoints
