from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_")
    host: str = "127.0.0.1"
    port: int = 6379


class KeycloakSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="IDP_KEYCLOAK_")
    url: str = ""
    client: str = ""
    secret: str = ""
