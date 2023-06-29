import json

from abc import ABC, abstractmethod
from typing import Type, List
from functools import lru_cache

from pydantic import BaseModel
from redis.asyncio import Redis
from fastapi import Depends

from app.db.init_redis import get_redis
from app.core.config import settings


class AbstractCache(ABC):

    @abstractmethod
    async def get(self, *args, **kwargs):
        pass

    @abstractmethod
    async def list(self, *args, **kwargs):
        pass

    @abstractmethod
    async def put(self, *args, **kwargs):
        pass


class RedisCache(AbstractCache):

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def get(
            self,
            key: str,
            schema: Type[BaseModel],
            *args, **kwargs
    ) -> BaseModel | None:
        obj = await self._redis.get(key)
        if not obj:
            return None
        return schema.parse_raw(obj)

    async def list(
            self,
            key: str,
            schema: Type[BaseModel],
            *args, **kwargs
    ) -> List[BaseModel] | None:
        objects = await self._redis.get(key)
        if not objects:
            return None
        return [schema.parse_raw(obj) for obj in json.loads(objects)]

    async def put(
            self,
            key: str,
            value: str,
            time: int = settings.film_cache_expire_in_second,
            *args, **kwargs
    ) -> None:
        await self._redis.setex(
            name=key,
            value=value,
            time=time
        )


@lru_cache()
def get_redis_cache(redis: Redis = Depends(get_redis)) -> RedisCache:
    return RedisCache(redis=redis)
