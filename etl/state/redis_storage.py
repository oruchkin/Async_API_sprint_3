import json
from typing import Any, cast

from redis import Redis

from .state_storage import BaseStorage

REDIS_STORAGE_KEY = "data"


class RedisStorage(BaseStorage):
    def __init__(self, redis_adapter: Redis):
        self.redis_adapter = redis_adapter

    def save_state(self, state: dict[str, Any]) -> None:
        value = json.dumps(state)
        self.redis_adapter.set(REDIS_STORAGE_KEY, value)

    def retrieve_state(self) -> dict[str, Any]:
        value = self.redis_adapter.get(REDIS_STORAGE_KEY)
        return cast(dict[str, Any], json.loads(str(value))) if value else {}
