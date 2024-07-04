import datetime
import json
from functools import lru_cache
from typing import Any, Callable, Literal, cast
from uuid import UUID

import aiohttp
import backoff
import models
import services.errors as errors
from core.settings import KeycloakSettings
from fastapi import Depends
from opentelemetry import trace
from pydantic import TypeAdapter
from services.keycloack_endpoints import KeycloakEndpoints

from .oidc_client import OIDCClient, get_oidc_service

Verb = Literal["POST", "GET", "DELETE", "PUT", "PATCH"]

tracer = trace.get_tracer(__name__)


class KeycloackClient:
    _access_token: models.TokenModel | None = None
    _access_token_issued: datetime.datetime | None = None
    _client_id: str | None = None

    def __init__(self, settings: KeycloakSettings, endpoints: KeycloakEndpoints, oidc: OIDCClient):
        self._oidc = oidc
        self._settings = settings
        self._endpoints = endpoints
        self._timeout = aiohttp.ClientTimeout(total=None, sock_connect=5, sock_read=5)

    async def get_role(self, role_id: UUID) -> models.RoleEntryModel:
        url = self._endpoints.get_role_with_id(role_id)
        data = await self._get(url)
        return models.RoleEntryModel.model_validate(data)

    async def list_roles(self) -> list[models.RoleEntryModel]:
        id = await self._get_client_id()
        url = self._endpoints.roles(id)
        data = await self._get(url)
        ta = TypeAdapter(list[models.RoleEntryModel])
        return ta.validate_python(data)

    async def create_role(self, name: str, description: str | None = None) -> None:
        id = await self._get_client_id()
        url = self._endpoints.roles(id)
        payload = {"name": name, "clientRole": False, "description": description or ""}
        await self._send("POST", url, payload)

    async def delete_role(self, role_id: UUID) -> None:
        url = self._endpoints.single_role(role_id)
        await self._send("DELETE", url)

    async def modify_role(self, role: models.RoleEntryModel) -> None:
        payload = {
            "id": str(role.id),
            "name": role.name,
            "description": role.description,
        }
        url = self._endpoints.single_role(role.id)
        await self._send("PUT", url, payload)

    async def list_users(self) -> list[models.UserEntryModel]:
        """
        Get all users
        """
        url = self._endpoints.list_users()
        data = await self._get(url)
        ta = TypeAdapter(list[models.UserEntryModel])
        return ta.validate_python(data)

    async def get_user_with_email(self, email: str) -> models.UserEntryModel:
        """
        Get user by email
        """
        url = self._endpoints.get_user_with_email(email)
        data = await self._get(url)
        ta = TypeAdapter(list[models.UserEntryModel])
        return ta.validate_python(data)[0]

    async def create_user(self, username: str, email: str, password: str) -> None:
        """
        Creates new user.
        For Keycloak email is optional field but we need it for future communications.
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
        await self._post(url, payload)

    async def list_user_roles(self, user_id: UUID) -> list[models.RoleEntryModel]:
        id = await self._get_client_id()
        url = self._endpoints.set_user_role(user_id, id)
        data = await self._get(url)
        ta = TypeAdapter(list[models.RoleEntryModel])
        return ta.validate_python(data)

    async def list_user_sessions(self, user_id: UUID) -> list[models.UserSessionModel]:
        url = self._endpoints.get_user_sessions(user_id)
        data = await self._get(url)
        ta = TypeAdapter(list[models.UserSessionModel])
        return ta.validate_python(data)

    async def set_user_role(self, user_id: UUID, role: models.RoleEntryModel) -> None:
        id = await self._get_client_id()
        url = self._endpoints.set_user_role(user_id, id)
        payload = [{"id": str(role.id), "name": role.name}]
        await self._post(url, payload)

    async def remove_user_role(self, user_id: UUID, role: models.RoleEntryModel) -> None:
        payload = [{"id": str(role.id), "name": role.name}]
        id = await self._get_client_id()
        url = self._endpoints.set_user_role(user_id, id)
        await self._send("DELETE", url, payload)

    async def reset_password(self, user_id: UUID, password: str) -> None:
        """
        Reset user's password by `user_id`. Don't forget to verify old password beforehand.
        """
        payload = {"temporary": False, "type": "password", "value": password}
        url = self._endpoints.reset_user_password(user_id)
        await self._send("POST", url, payload)

    async def user_logout_all(self, user_id: UUID) -> None:
        url = self._endpoints.delete_user_sessions(user_id)
        await self._send("POST", url)

    @staticmethod
    def _get_func_by_verb(verb: Verb, session: aiohttp.ClientSession) -> Callable:
        match verb:
            case "GET":
                return session.get
            case "POST":
                return session.post
            case "DELETE":
                return session.delete
            case "PUT":
                return session.put
            case "PATCH":
                return session.patch

    @backoff.on_exception(backoff.expo, errors.NotAuthorizedError, max_tries=2)
    async def _send(self, verb: Verb, url: str, payload: Any | None = None) -> Any:
        headers = await self._get_request_headers()
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            func = KeycloackClient._get_func_by_verb(verb, session)
            async with func(url, json=payload) as response:
                return await self._handle_failed_response(response)

    async def _get(self, url: str) -> Any:
        return await self._send("GET", url)

    async def _post(self, url: str, json_payload: Any) -> Any:
        return await self._send("POST", url, json_payload)

    async def _get_request_headers(self) -> dict:
        return {"Authorization": await self._get_auth_header_value(), "Content-Type": "application/json"}

    async def _get_auth_header_value(self, throw_if_empty: bool = False) -> str:
        if self._access_token and self._has_valid_token():
            return f"{self._access_token.token_type} {self._access_token.access_token}"

        if throw_if_empty:
            raise ValueError("Failed")

        await self._auth()
        return await self._get_auth_header_value(True)

    def _has_valid_token(self) -> bool:
        """
        Checks if current token is still valid
        """
        if self._access_token and self._access_token_issued:
            now = datetime.datetime.now()
            past = (now - self._access_token_issued).total_seconds()
            SEC_ALLOW = 2
            return past < self._access_token.expires_in - SEC_ALLOW

        return False

    async def _auth(self) -> None:
        try:
            token = await self._oidc.client_credentials_flow()
            self._access_token_issued = datetime.datetime.now()
            self._access_token = token
        except Exception:
            self._access_token_issued = None
            self._access_token = None
            raise

    async def _get_endpoints(self) -> KeycloakEndpoints:
        return self._endpoints

    async def _get_client_id(self) -> str:
        if self._client_id:
            return self._client_id

        # TODO: Current approach is wrong as it requires too many permissions
        # and returns clients secrets which looks like too much for get client id.
        # Solution - add custom mapper Mapper Type: Hardcoded claim
        # (https://stackoverflow.com/questions/68632386/get-id-not-clientid-from-keycloak-jwt-token)
        headers = await self._get_request_headers()
        url = self._endpoints.client_id(self._settings.client)
        with tracer.start_as_current_span("keycloak-request"):
            async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
                async with session.get(url) as response:
                    data = await response.json()
                    if response.ok:
                        self._client_id = data[0]["id"]
                        return cast(str, self._client_id)

                raise ValueError(data["error"])

    async def _handle_failed_response(self, response: aiohttp.ClientResponse) -> dict:
        raw = await response.text()
        if response.ok:
            # some api calls return empty response
            return json.loads(raw) if raw else {}

        data = json.loads(raw)
        error = self._get_error_message(data)

        if response.status == 401:
            self._access_token = None
            self._access_token_issued = None
            raise errors.NotAuthorizedError(error)

        if response.status == 404:
            raise errors.NotFoundError(error)

        raise errors.ValidationError(error)

    def _get_error_message(self, data: dict) -> str:
        if "errorMessage" in data:
            return data["errorMessage"]

        if "error" in data:
            return data["error"]

        return "Failed"


@lru_cache()
def get_keycloak_service(oidc=Depends(get_oidc_service)) -> KeycloackClient:
    settings = KeycloakSettings()
    endpoints = KeycloakEndpoints(settings)
    client = KeycloackClient(settings, endpoints, oidc)
    return client
