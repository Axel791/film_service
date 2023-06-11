from loguru import logger

from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError

from fastapi import Depends

from typing import Optional, List
from functools import lru_cache

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
        genre = await self._get_genre_from_etl(genre_id=genre_id)
        return genre

    async def _get_genre_from_etl(self, genre_id: str) -> Optional[Genre]:
        try:
            doc = await self._es.get(index='genres', id=genre_id)
        except NotFoundError:
            raise NotFoundGenre
        return Genre(**doc['_source'])

@lru_cache()
def genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> GenreService:
    return GenreService(es=elastic, redis=redis)
