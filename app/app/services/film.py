from loguru import logger

from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError

from fastapi import Depends

from typing import Optional, List
from functools import lru_cache

from app.db.init_redis import get_redis
from app.db.init_etl import get_elastic

from app.schemas.films import FilmWork

from app.exceptions.film_exception import NotFoundFilm


class FilmWorkService:

    def __init__(
            self,
            redis: Redis,
            es: AsyncElasticsearch
    ) -> None:
        self._redis = redis
        self._es = es

    async def get(self, film_id: str) -> Optional[FilmWork]:
        film = await self._get_film_from_etl(film_id=film_id)
        return film

    async def list(self) -> Optional[List[FilmWork]]:
        pass

    async def _get_film_from_etl(self, film_id: str) -> Optional[FilmWork]:
        try:
            doc = await self._es.get(index='movies', id=film_id)
        except NotFoundError:
            raise NotFoundFilm
        return FilmWork(**doc['_source'])

    async def _list_films_and_filter(self, filter_params) -> Optional[List[FilmWork]]:
        pass


@lru_cache()
def film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> FilmWorkService:
    return FilmWorkService(es=elastic, redis=redis)
