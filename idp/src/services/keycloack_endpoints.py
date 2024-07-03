from uuid import UUID

from core.settings import KeycloakSettings


class KeycloakEndpoints:
    """
    Keycloak specific endpoints
    """

    def __init__(self, settings: KeycloakSettings):
        self._settings = settings
        self._realm = "master"

    @property
    def base_url(self) -> str:
        return f"{self._settings.url}/realms/{self._realm}"

    def client_id(self, clientId: str) -> str:
        return f"{self._settings.url}/admin/realms/{self._realm}/clients?clientId={clientId}"

    def list_users(self) -> str:
        return f"{self._settings.url}/admin/realms/{self._realm}/users"

    def get_user_with_email(self, email: str) -> str:
        return f"{self.list_users()}?email={email}&exact=true"

    def create_user(self) -> str:
        """
        https://www.keycloak.org/docs-api/25.0.0/rest-api/index.html#_users
        """
        return f"{self._settings.url}/admin/realms/{self._realm}/users"

    def reset_user_password(self, user_id: UUID) -> str:
        return f"{self._settings.url}/admin/realms/{self._realm}/users/{user_id}/reset-password"

    def get_user_sessions(self, user_id: UUID) -> str:
        return f"{self._settings.url}/admin/realms/{self._realm}/users/{user_id}/sessions"

    def delete_user_sessions(self, user_id: UUID) -> str:
        return f"{self._settings.url}/admin/realms/{self._realm}/users/{user_id}/logout"

    def single_role(self, role_id: UUID) -> str:
        return f"{self._settings.url}/admin/realms/{self._realm}/roles-by-id/{role_id}"

    def get_role_with_id(self, role_id: UUID) -> str:
        return f"{self._settings.url}/admin/realms/{self._realm}/roles-by-id/{role_id}"

    def roles(self, id: str) -> str:
        """
        id of the client (UUID, not client_id)
        """
        return f"{self._settings.url}/admin/realms/{self._realm}/clients/{id}/roles"

    def set_user_role(self, user_id: UUID, client_id: str) -> str:
        """
        id of the client (UUID, not client_id)
        """
        return f"{self._settings.url}/admin/realms/{self._realm}/users/{user_id}/role-mappings/clients/{client_id}"
