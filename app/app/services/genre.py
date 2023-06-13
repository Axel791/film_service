import json

from loguru import logger

from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError

from fastapi import Depends

from typing import Optional, List
from functools import lru_cache

from app.core.config import settings
from app.db.init_redis import get_redis
from app.db.init_etl import get_elastic

from app.schemas.genres import Genre

from app.exceptions.genre_exception import NotFoundGenre


class GenreService:

    def __init__(
            self,
            redis: Redis,
            es: AsyncElasticsearch
    ) -> None:
        self._redis = redis
        self._es = es

    async def get(self, genre_id: str) -> Optional[Genre]:
        genre: Optional[Genre] = await self._get_genre_from_cache(genre_id)
        if genre is None:
            genre = await self._get_genre_from_etl(genre_id=genre_id)
            genre_str: str = json.dumps(genre.dict())
            await self._put_data_to_cache(key=genre_id, value=genre_str)
        return genre

    async def _get_genre_from_etl(self, genre_id: str) -> Optional[Genre]:
        try:
            doc = await self._es.get(index='genres', id=genre_id)
        except NotFoundError:
            raise NotFoundGenre
        return Genre(**doc['_source'])

    async def _get_genre_from_cache(self, key: str) -> Optional[Genre]:
        genre: Optional[bytes] = await self._redis.get(key)
        if not genre:
            return None
        genre_obj = Genre.parse_raw(genre)
        return genre_obj

    async def _put_data_to_cache(self, key: str, value: str, time: int = settings.film_cache_expire_in_second):
        await self._redis.setex(
            name=key,
            value=value,
            time=time,
        )


@lru_cache()
def genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> GenreService:
    return GenreService(es=elastic, redis=redis)
