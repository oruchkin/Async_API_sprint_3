from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_")
    host: str = "127.0.0.1"
    port: int = 6379


class ElasticsearchSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ELASTIC_")
    url: str = ""


class FileapiSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FILEAPI_")
    url: str = ""


class DjangoSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ADMIN_")
    s3_bucket: str = ""


class JaegerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="JAEGER_")
    host: str
    port: int


class IDPSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="IDP_")
    url: str = ""


class KeycloakSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="IDP_KEYCLOAK_")
    url: str = ""
    client: str = ""
