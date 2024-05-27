from pydantic_settings import BaseSettings, SettingsConfigDict
from redis import Redis


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_")
    host: str = "127.0.0.1"
    port: int = 6379


def connect() -> Redis:
    settings = RedisSettings()
    client = Redis(host=settings.host, port=settings.port, decode_responses=True)
    return client
