import datetime

from core.auth import User
from redis.asyncio import Redis

REQUEST_LIMIT_PER_MINUTE = 20


class ThrottlingService:
    def __init__(self, redis: Redis):
        self._redis = redis

    async def is_allowed(self, user: User) -> bool:
        pipeline = self._redis.pipeline()
        now = datetime.datetime.now(datetime.UTC)
        key = f"{user.id}:{now.minute}"
        pipeline.incr(key, 1)
        pipeline.expire(key, 59)
        result = await pipeline.execute()
        request_number = result[0]
        return request_number < REQUEST_LIMIT_PER_MINUTE
