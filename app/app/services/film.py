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
        film: Optional[FilmWork] = await self._get_film_from_cache(key=film_id)
        if film is None:
            film: Optional[FilmWork] = await self._get_film_from_etl(film_id=film_id)
            if film is not None:
                film_str: str = json.dumps(film.dict())
                await self._put_data_to_cache(key=film_id, value=film_str)
        return film

    async def list(
            self,
            genre: Optional[str] = None,
            rating_order: Optional[str] = None
    ) -> Optional[List[FilmWork]]:
        list_films = await self._list_films_and_filter(
            genre=genre,
            rating_order=rating_order
        )
        return list_films

    async def _get_film_from_etl(self, film_id: str) -> Optional[FilmWork]:
        try:
            doc = await self._es.get(index='movies', id=film_id)
        except NotFoundError:
            raise NotFoundFilm
        return FilmWork(**doc['_source'])

    async def _get_film_from_cache(self, key: str) -> Optional[FilmWork]:
        film: Optional[bytes] = await self._redis.get(key)
        if not film:
            return None
        filmwork = FilmWork.parse_raw(film)
        return filmwork

    async def _get_films_from_cache(self, key: str) -> Optional[List[FilmWork]]:
        films: Optional[bytes] = await self._redis.get(key)
        if not films:
            return None
        films_list = [FilmWork(**film) for film in json.loads(films)]
        return films_list

    async def _put_data_to_cache(self, key: str, value: str, time: int = settings.FILM_CACHE_EXPIRE_IN_SECOND):
        await self._redis.setex(
            name=key,
            value=value,
            time=time,
        )

    async def _list_films_and_filter(
            self,
            genre: Optional[str] = None,
            rating_order: Optional[str] = None
    ) -> Optional[List[FilmWork]]:

        body = {
            "query": {
                "match_all": {}
            }
        }

        if genre is not None:
            body["query"] = {
                "match": {"genre": genre}
            }

        if rating_order is not None:
            body["sort"] = [
                {
                    "imdb_rating": {
                        "order": "asc" if rating_order == '-' else 'desc'
                    }
                }
            ]
        key: str = json.dumps(body)
        films: Optional[List[FilmWork]] = await self._get_films_from_cache(key)
        if films is None:
            try:
                response = await self._es.search(index='movies', body=body)
            except NotFoundError:
                raise NotFoundFilm
            films = [FilmWork(**doc['_source']) for doc in response['hits']['hits']]

            films_str: str = json.dumps([film.dict() for film in films])
            await self._put_data_to_cache(key=key, value=films_str)
        return films


@lru_cache()
def film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> FilmWorkService:
    return FilmWorkService(es=elastic, redis=redis)
