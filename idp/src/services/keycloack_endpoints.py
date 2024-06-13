from core.settings import KeycloakSettings

class KeycloakEndpoints:
    _oidc_endpoints: dict[str, str] | None = None

    def __init__(self, settings: KeycloakSettings):
        self._settings = settings
        self._realm = "master"

    def oidc_discovery(self) -> str:
        return f"{self._settings.url}/realms/{self._realm}/.well-known/openid-configuration"

    def oidc_has_discovery(self) -> bool:
        return self._oidc_endpoints is not None

    def oidc_set_discovery(self, response: dict[str, str]) -> None:
        self._oidc_endpoints = response

    def oidc_token(self) -> str:
        if self._oidc_endpoints:
            return self._oidc_endpoints["token_endpoint"]
        
        raise ValueError("Run discovery first")
    
    def create_user(self) -> str:
        """
        https://www.keycloak.org/docs-api/25.0.0/rest-api/index.html#_users
        """
        return f"{self._settings.url}/admin/realms/{self._realm}/users"