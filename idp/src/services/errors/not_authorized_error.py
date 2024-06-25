from .keycloak_error import KeycloakError


class NotAuthorizedError(KeycloakError):
    def __init__(self, message: str):
        super().__init__(message)
