import json

from pydantic import BaseModel
from fastapi import Depends
from redis.asyncio import Redis

from functools import lru_cache
from typing import Type, List

from app.core.config import settings
from app.db.init_redis import get_redis


class CacheableService:

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def get_from_cache(self, key: str, schema: Type[BaseModel]) -> List | None:
        objects: bytes | None = await self._redis.get(key)
        if not objects:
            return None
        objects_list = [schema.parse_obj(obj) for obj in json.loads(objects)]
        return objects_list

    async def put_to_cache(
            self,
            key: str,
            value: str,
            time: int = settings.film_cache_expire_in_second
    ) -> None:
        await self._redis.setex(
            name=key,
            value=value,
            time=time
        )


@lru_cache()
def get_cacheable_service(redis: Redis = Depends(get_redis)) -> CacheableService:
    return CacheableService(redis=redis)
