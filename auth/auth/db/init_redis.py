# db/redis_db.py
from typing import Optional
from redis.asyncio import Redis

redis: Optional[Redis] = None


async def get_redis() -> Redis:
    return redis
