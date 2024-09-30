import os
from functools import lru_cache

import aiohttp
from opentelemetry import trace
from src.core.settings import KeycloakSettings

tracer = trace.get_tracer(__name__)

JWKS_CACHE: dict | None = None


class OIDCClient:
    """
    OpenID Connect interactions class
    """

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
        return str(discovery["issuer"])

    async def jwks_raw(self) -> dict:
        global JWKS_CACHE
        if JWKS_CACHE:
            return JWKS_CACHE

        discovery = await self.get_discovery()
        url = discovery["jwks_uri"]
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            async with session.get(url) as response:
                JWKS_CACHE = dict(await response.json())

        return JWKS_CACHE

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


@lru_cache()
def get_oidc_service() -> OIDCClient:
    # Maybe not the best way to construct the class
    keycloak_url = f"{os.environ['IDP_KEYCLOAK_URL']}/realms/master"
    settings = KeycloakSettings()
    client = OIDCClient(keycloak_url, settings)
    return client
