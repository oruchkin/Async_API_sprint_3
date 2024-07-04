from typing import Any

from opentelemetry import trace
from redis.asyncio import Redis

from .storage import ICache

tracer = trace.get_tracer(__name__)


class RedisCache(ICache):
    def __init__(self, client: Redis):
        self._client = client

    async def set(self, key: str, value: Any, timeout_sec: int) -> None:
        with tracer.start_as_current_span("redis-request"):
            await self._client.set(key, value, timeout_sec)

    async def get(self, key: str) -> Any:
        with tracer.start_as_current_span("redis-request"):
            return await self._client.get(key)
