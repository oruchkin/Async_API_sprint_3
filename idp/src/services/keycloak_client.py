import datetime
from functools import lru_cache
from typing import cast

import aiohttp
import models
from core.settings import KeycloakSettings
from pydantic import TypeAdapter
from services.keycloack_endpoints import KeycloakEndpoints


class KeycloackClient:
    # TODO: Verify token expiration
    # (dt2 - dt1).total_seconds()
    _access_token: models.TokenModel | None = None
    _access_token_issued: datetime.datetime | None = None
    _client_id: str | None = None

    def __init__(self, settings: KeycloakSettings):
        self._settings = settings
        self._endpoints = KeycloakEndpoints(settings)
        self._timeout = aiohttp.ClientTimeout(total=None, sock_connect=5, sock_read=5)

    async def list_roles(self) -> list[models.RoleEntryModel]:
        headers = await self._get_request_headers()
        id = await self._get_client_id()
        url = self._endpoints.roles(id)
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.get(url) as response:
                data = await response.text()
                if response.ok:
                    ta = TypeAdapter(list[models.RoleEntryModel])
                    return ta.validate_json(data)

                error = models.ErrorModel.model_validate_json(data)
                raise ValueError(error.error)

    async def create_role(self, name: str, description: str | None = None) -> None:
        payload = {"name": name, "clientRole": False, "description": description or ""}
        headers = await self._get_request_headers()
        id = await self._get_client_id()
        url = self._endpoints.roles(id)
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.post(url, json=payload) as response:
                if not response.ok:
                    response = await response.json()
                    raise ValueError(response["error"])

    async def delete_role(self, role_id: str) -> None:
        headers = await self._get_request_headers()
        url = self._endpoints.single_role(role_id)
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.delete(url) as response:
                if not response.ok:
                    response = await response.json()
                    raise ValueError(response["error"])

    async def list_users(self) -> list[models.UserEntryModel]:
        """
        Get all users
        """
        url = self._endpoints.list_users()
        headers = await self._get_request_headers()
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.get(url) as response:
                data = await response.text()
                if response.ok:
                    ta = TypeAdapter(list[models.UserEntryModel])
                    return ta.validate_json(data)

                error = models.ErrorModel.model_validate_json(data)
                raise ValueError(error.error)

    async def get_user_with_email(self, email: str) -> models.UserEntryModel:
        """
        Get all users
        """
        url = self._endpoints.get_user_with_email(email)
        headers = await self._get_request_headers()
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.get(url) as response:
                data = await response.text()
                if response.ok:
                    ta = TypeAdapter(list[models.UserEntryModel])
                    return ta.validate_json(data)[0]

                error = models.ErrorModel.model_validate_json(data)
                raise ValueError(error.error)

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
            "credentials": [{"type": "password", "value": password, "temporary": False}],
        }
        url = self._endpoints.create_user()
        headers = await self._get_request_headers()
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.post(url, json=payload) as response:
                data = await response.text()
                if not response.ok:
                    error = models.ErrorModel.model_validate_json(data)
                    raise ValueError(error.error)

    async def list_user_roles(self, user_id: str) -> list[models.RoleEntryModel]:
        headers = await self._get_request_headers()
        id = await self._get_client_id()
        url = self._endpoints.set_user_role(user_id, id)
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.get(url) as response:
                data = await response.text()
                if response.ok:
                    ta = TypeAdapter(list[models.RoleEntryModel])
                    return ta.validate_json(data)

                error = models.ErrorModel.model_validate_json(data)
                raise ValueError(error.error)

    async def set_user_role(self, user_id: str, role: models.RoleEntryModel) -> None:
        headers = await self._get_request_headers()
        id = await self._get_client_id()
        url = self._endpoints.set_user_role(user_id, id)
        # TODO: Payload here is just `id` and `name`
        payload = [role.model_dump()]
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.post(url, json=payload) as response:
                if not response.ok:
                    data = await response.text()
                    error = models.ErrorModel.model_validate_json(data)
                    raise ValueError(error.error)

    async def remove_user_role(self, user_id: str, role: models.RoleEntryModel) -> None:
        headers = await self._get_request_headers()
        id = await self._get_client_id()
        url = self._endpoints.set_user_role(user_id, id)
        # TODO: Payload here is just `id` and `name`
        payload = [role.model_dump()]
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.delete(url, json=payload) as response:
                if not response.ok:
                    data = await response.text()
                    error = models.ErrorModel.model_validate_json(data)
                    raise ValueError(error.error)

    async def reset_password(self, user_id: str, password: str) -> None:
        """
        Reset user's password by `user_id`. Don't forget to verify old password beforehand.
        """
        payload = {"temporary": False, "type": "password", "value": password}
        url = self._endpoints.reset_user_password(user_id)
        headers = await self._get_request_headers()
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.post(url, json=payload) as response:
                if not response.ok:
                    json_body = await response.json()
                    raise ValueError(json_body)

    async def authenticate(self, username: str, password: str) -> models.TokenModel:
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
            async with session.post(url, data=payload) as response:
                # 'error': 'invalid_grant', 'error_description': 'Invalid user credentials'
                if not response.ok:
                    json_body: dict = await response.json()
                    raise ValueError(json_body["error"])

                raw = await response.text()
                return models.TokenModel.model_validate_json(raw)

    async def refresh(self, refresh_token: str) -> models.TokenModel:
        payload = {
            "client_id": self._settings.client,
            "client_secret": self._settings.secret,
            "scope": "openid roles profile",
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        url = (await self._get_endpoints()).oidc_token()
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.post(url, data=payload) as response:
                # 'error': 'invalid_grant', 'error_description': 'Invalid user credentials'
                if not response.ok:
                    json_body: dict = await response.json()
                    raise ValueError(json_body["error"])

                raw = await response.text()
                return models.TokenModel.model_validate_json(raw)

    async def _get_request_headers(self) -> dict:
        return {"Authorization": await self._get_auth_header_value(), "Content-Type": "application/json"}

    async def _get_auth_header_value(self, throw_if_empty: bool = False) -> str:
        if self._access_token:
            return f"{self._access_token.token_type} {self._access_token.access_token}"

        if throw_if_empty:
            raise ValueError("Failed")

        await self._auth()
        return await self._get_auth_header_value(True)

    async def discovery(self) -> None:
        url = self._endpoints.oidc_discovery()
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            async with session.get(url) as response:
                json_body = await response.json()
                self._endpoints.oidc_set_discovery(json_body)

    async def _auth(self) -> None:
        if not self._endpoints.oidc_has_discovery():
            await self.discovery()

        url = self._endpoints.oidc_token()
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "scope": "openid profile roles",
            "grant_type": "client_credentials",
            "client_id": self._settings.client,
            "client_secret": self._settings.secret,
        }
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.post(url, data=payload) as response:
                data = await response.text()
                if response.ok:
                    self._access_token_issued = datetime.datetime.now()
                    self._access_token = models.TokenModel.model_validate_json(data)

                self._access_token_issued = None
                error = models.ErrorModel.model_validate_json(data)
                raise ValueError(error.error)

    async def _get_endpoints(self) -> KeycloakEndpoints:
        if not self._endpoints.oidc_has_discovery():
            await self.discovery()

        return self._endpoints

    async def _get_client_id(self) -> str:
        if self._client_id:
            return self._client_id

        # TODO: Current approach is wrong as it requires too many permissions
        # and returns clients secrets which looks like too much for get client id.
        # Solution - add custom mapper Mapper Type: Hardcoded claim (https://stackoverflow.com/questions/68632386/get-id-not-clientid-from-keycloak-jwt-token)
        headers = await self._get_request_headers()
        url = self._endpoints.client_id(self._settings.client)
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.get(url) as response:
                data = await response.json()
                if response.ok:
                    self._client_id = data[0]["id"]
                    return cast(str, self._client_id)

                raise ValueError(data["error"])


@lru_cache()
def get_keycloak_service() -> KeycloackClient:
    settings = KeycloakSettings()
    client = KeycloackClient(settings)
    return client
