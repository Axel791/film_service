import datetime

from aioredis import Redis

from auth.core.config import settings


class RateLimiter:
    def __init__(
        self,
        redis_connection: Redis,
        limit_per_min: int = settings.requests_limit_per_min,
    ):
        self.redis_conn = redis_connection
        self.limit_per_min = limit_per_min

    async def check_rate_limit(self, user_id: str) -> bool:
        now = datetime.datetime.now()
        key = f"{user_id}:{now.minute}"
        await self.redis_conn.incr(key, 1)
        await self.redis_conn.expire(key, 59)
        request_number = int(await self.redis_conn.get(key))
        if request_number > self.limit_per_min:
            return False
        return True
