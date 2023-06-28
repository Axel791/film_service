import json

from typing import List
from functools import lru_cache

from fastapi import Depends
from elasticsearch import AsyncElasticsearch

from .base import SearchService
from .cacheble_service import CacheableService, get_cacheable_service

from app.core.config import settings
from app.db.init_es import get_elastic

from app.db.init_etl import get_elastic
from app.schemas.films import FilmWork, FilmWorkShort


class FilmWorkService(SearchService):

    def __init__(
            self,
            cacheable: CacheableService,
            es: AsyncElasticsearch
    ) -> None:
        super().__init__(cacheable, es)

    async def get(self, film_id: str) -> FilmWork | None:
        film = await self._cacheable.get_obj_from_cache(key=film_id, schema=FilmWork)
        if film is None:
            film = await self.get_obj_from_etl(obj_id=film_id, index='movies', schema=FilmWork)
            film_str = json.dumps(film.dict())
            await self._cacheable.put_to_cache(key=film_id, value=film_str)
        return film

    async def list(
            self,
            genre: str | None = None,
            rating_order: str | None = None,
            page: int | None = 1,
            page_size: int | None = settings.default_page_size
    ):
        return await self._list_films_and_filter(
            genre=genre,
            rating_order=rating_order,
            page=page,
            page_size=page_size
        )

    async def search(
            self,
            query: str = "",
            page: int | None = 1,
            page_size: int | None = settings.default_page_size
    ) -> List[FilmWorkShort] | None:
        return await self._search_films(
            query=query,
            page=page,
            page_size=page_size
        )

    async def _list_films_and_filter(
            self,
            genre: str | None = None,
            rating_order: str | None = None,
            page: int | None = 1,
            page_size: int | None = settings.default_page_size
    ) -> List[FilmWork] | None:
        start = (page - 1) * page_size
        body = {
            "query": {
                "match_all": {}
            },
            "from": start,
            "size": page_size
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
        key = json.dumps(body)
        films = await self._cacheable.get_list_from_cache(key=key, schema=FilmWork)
        if films is None:
            films = await self.get_objects_from_etl(
                key=key,
                body=body,
                schema=FilmWork,
                index='movies'
            )
        return films

    async def _search_films(
            self,
            query: str,
            page: int | None = 1,
            page_size: int | None = settings.default_page_size
    ) -> List[FilmWorkShort] | None:
        start = (page - 1) * page_size
        body = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"title": query}}
                    ]
                }
            },
            "from": start,
            "size": page_size
        }
        key: str = json.dumps(body)
        films = await self._cacheable.get_list_from_cache(key=key, schema=FilmWorkShort)
        if films is None:
            films = await self.get_objects_from_etl(
                key=key,
                body=body,
                schema=FilmWorkShort,
                index='movies'
            )
        return films


@lru_cache()
def get_film_service(
        cacheable: CacheableService = Depends(get_cacheable_service),
        es: AsyncElasticsearch = Depends(get_elastic)
) -> FilmWorkService:
    return FilmWorkService(cacheable=cacheable, es=es)
