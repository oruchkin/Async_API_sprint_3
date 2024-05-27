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
    model_config = SettingsConfigDict(env_prefix="DJANGO_")
    s3_bucket: str = ""
