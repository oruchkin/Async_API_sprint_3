from pydantic_settings import BaseSettings, SettingsConfigDict

class KeycloakSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="IDP_KEYCLOAK_")
    url: str = ""
    client: str = ""
    secret: str = ""
