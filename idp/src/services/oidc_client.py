import json
import urllib.parse
from functools import lru_cache

import aiohttp
import models
import services.errors as errors
from core.settings import KeycloakSettings
from opentelemetry import trace

from .keycloack_endpoints import KeycloakEndpoints

tracer = trace.get_tracer(__name__)


class OIDCClient:
    """
    OpenID Connect interactions class
    """

    JWKS_CACHE: models.JWKSModel | None = None

    _discovery_data: dict | None = None

    def __init__(self, url: str, client_credentials: KeycloakSettings):
        self._base_url = url
        self._client = client_credentials
        self._timeout = aiohttp.ClientTimeout(total=None, sock_connect=5, sock_read=5)

    @property
    def client_id(self) -> str:
        return self._client.client

    async def issuer(self) -> str:
        discovery = await self.get_discovery()
        return discovery["issuer"]

    async def password_flow(self, username: str, password: str) -> models.TokenModel:
        payload = {
            "client_id": self._client.client,
            "client_secret": self._client.secret,
            "scope": "openid roles profile",
            "grant_type": "password",
            "username": username,
            "password": password,
        }
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        discovery = await self.get_discovery()
        url = discovery["token_endpoint"]
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.post(url, data=payload) as response:
                data = await self._ensure_ok_response(response)
                return models.TokenModel.model_validate(data)

    def code_flow_url(self, idp: str, redirect_uri: str) -> str:
        params = {
            "client_id": self._client.client,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid",
            "kc_idp_hint": idp,
        }
        # это хардкод для запуска девелоп окружения (в проде должено быть имя контейнера (у нас его нет))
        return f"http://localhost:32547/realms/master/protocol/openid-connect/auth?{urllib.parse.urlencode(params)}"

    async def code_flow(self, code: str, redirect_uri: str) -> models.TokenModel:
        payload = {
            "client_id": self._client.client,
            "client_secret": self._client.secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        discovery = await self.get_discovery()
        url = discovery["token_endpoint"]
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.post(url, data=payload) as response:
                data = await self._ensure_ok_response(response)
                return models.TokenModel.model_validate(data)

    async def client_credentials_flow(self) -> models.TokenModel:
        discovery = await self.get_discovery()
        url = discovery["token_endpoint"]
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "scope": "openid profile roles",
            "grant_type": "client_credentials",
            "client_id": self._client.client,
            "client_secret": self._client.secret,
        }
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.post(url, data=payload) as response:
                data = await self._ensure_ok_response(response)
                return models.TokenModel.model_validate(data)

    async def introspect(self, token: str) -> bool:
        payload = {
            "client_id": self._client.client,
            "client_secret": self._client.secret,
            "token": token,
        }
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        discovery = await self.get_discovery()
        url = discovery["introspection_endpoint"]
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.post(url, data=payload) as response:
                data = await self._ensure_ok_response(response)
                return data["active"]

    async def logout(self, refresh_token: str) -> None:
        payload = {
            "client_id": self._client.client,
            "client_secret": self._client.secret,
            "refresh_token": refresh_token,
        }
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        discovery = await self.get_discovery()
        url = discovery["end_session_endpoint"]
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.post(url, data=payload) as response:
                await self._ensure_ok_response(response)

    async def refresh(self, refresh_token: str) -> models.TokenModel:
        payload = {
            "client_id": self._client.client,
            "client_secret": self._client.secret,
            "scope": "openid roles profile",
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        discovery = await self.get_discovery()
        url = discovery["token_endpoint"]
        async with aiohttp.ClientSession(timeout=self._timeout, headers=headers) as session:
            async with session.post(url, data=payload) as response:
                # 'error': 'invalid_grant', 'error_description': 'Invalid user credentials'
                data = await self._ensure_ok_response(response)
                return models.TokenModel.model_validate(data)

    async def oidc_jwks(self) -> models.JWKSModel:
        """
        The JSON Web Key Set (JWKS) is a set of keys containing the public keys
        used to verify any JSON Web Token (JWT) issued by the Authorization Server
        and signed using the RS256 signing algorithm.
        """
        if not OIDCClient.JWKS_CACHE:
            discovery = await self.get_discovery()
            url = discovery["jwks_uri"]
            async with aiohttp.ClientSession(timeout=self._timeout) as session:
                async with session.get(url) as response:
                    data = await response.text()
                    OIDCClient.JWKS_CACHE = models.JWKSModel.model_validate_json(data)

        return OIDCClient.JWKS_CACHE

    async def jwks_raw(self) -> dict:
        discovery = await self.get_discovery()
        url = discovery["jwks_uri"]
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            async with session.get(url) as response:
                return await response.json()

    async def get_discovery(self) -> dict:
        if not self._discovery_data:
            url = f"{self._base_url}/.well-known/openid-configuration"
            with tracer.start_as_current_span("oidc-request"):
                async with aiohttp.ClientSession(timeout=self._timeout) as session:
                    async with session.get(url) as response:
                        self._discovery_data = await response.json()
                        if not self._discovery_data:
                            # mostly for type checking
                            raise ValueError("Failed to load discovery")

        return self._discovery_data

    async def _ensure_ok_response(self, response: aiohttp.ClientResponse) -> dict:
        # some endpoints do not return anything
        raw = await response.text()
        if response.ok:
            return json.loads(raw) if raw else {}

        # Possible error response:
        # 'error': 'unauthorized_client'
        # 'error_description': 'Invalid client or Invalid client credentials'

        data = json.loads(raw)
        message = data.get("error_description", "Failed")
        if response.status == 401:
            raise errors.NotAuthorizedError(message)

        raise ValueError("Failed")


@lru_cache()
def get_oidc_service() -> OIDCClient:
    # Maybe not the best way to construct the class
    settings = KeycloakSettings()
    endpoints = KeycloakEndpoints(settings)
    client = OIDCClient(endpoints.base_url, settings)
    return client
