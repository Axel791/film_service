from aioredis import Redis, from_url
from typing import AsyncIterator
from loguru import logger

redis_for_rate_limiter: Redis | None = None


async def get_redis_for_rate_limiter() -> Redis:
    return redis_for_rate_limiter


async def init_redis_pool(host: str) -> AsyncIterator[Redis]:
    try:
        logger.info("Connecting to Redis at host: %s", host)
        pool = await from_url(
            url="redis://{host}".format(host=host),
            encoding="utf-8",
            decode_responses=True,
        )
        logger.info("Connected to Redis at host: %s", host)
        yield pool
    finally:
        pool.close()
        await pool.wait_closed()
        logger.info("Closed connection to Redis at host: %s", host)
