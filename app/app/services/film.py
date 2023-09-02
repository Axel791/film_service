import json
from functools import lru_cache
from typing import List, Type

from fastapi import Depends
from pydantic import BaseModel

from app.api.v1.schemas.films import FilmWork, FilmWorkShort
from app.core.config import settings
from app.services.cacheble_base import AbstractCache, get_redis_cache
from app.services.storage_base import AbstractStorage, get_elastic_storage


class FilmWorkService:
    def __init__(self, cache: AbstractCache, storage: AbstractStorage) -> None:
        self.cache = cache
        self.storage = storage

    async def get(self, film_id: str) -> FilmWork | None:
        film = await self.cache.get(key=film_id, schema=FilmWork)
        if film is None:
            film = await self.storage.get(
                obj_id=film_id, index="movies", schema=FilmWork
            )
            film_str = json.dumps(film.dict())
            await self.cache.put(key=film_id, value=film_str)
        return film

    async def list(
        self,
        genre: str | None = None,
        rating_order: str | None = None,
        page: int | None = 1,
        page_size: int | None = settings.default_page_size,
    ) -> List[FilmWork] | None:
        return await self._list_films_and_filter(
            genre=genre, rating_order=rating_order, page=page, page_size=page_size
        )

    async def search(
        self,
        query: str = "",
        page: int | None = 1,
        page_size: int | None = settings.default_page_size,
    ) -> List[FilmWorkShort] | None:
        return await self._search_films(query=query, page=page, page_size=page_size)

    async def _search_films(
        self,
        query: str,
        page: int | None = 1,
        page_size: int | None = settings.default_page_size,
    ) -> List[FilmWorkShort] | None:
        start = (page - 1) * page_size
        body = {
            "query": {"bool": {"must": [{"match": {"title": query}}]}},
            "from": start,
            "size": page_size,
        }
        return await self._return_films(body=body, schema=FilmWorkShort)

    async def _return_films(
        self, body: dict, schema: Type[BaseModel]
    ) -> Type[BaseModel] | None:
        key = json.dumps(body)
        films = await self.cache.list(key=key, schema=schema)
        if films is None:
            films = await self.storage.list(
                key=key, body=body, schema=schema, insex="movies"
            )
            films_srt = json.dumps([film.dict() for film in films])
            await self.cache.put(key=key, value=films_srt)
        return films

    async def _list_films_and_filter(
        self,
        genre: str | None = None,
        rating_order: str | None = None,
        page: int | None = 1,
        page_size: int | None = settings.default_page_size,
    ) -> List[FilmWork] | None:
        start = (page - 1) * page_size
        body = {"query": {"match_all": {}}, "from": start, "size": page_size}

        if genre is not None:
            body["query"] = {"match": {"genre": genre}}

        if rating_order is not None:
            body["sort"] = [
                {"imdb_rating": {"order": "asc" if rating_order == "-" else "desc"}}
            ]
        return await self._return_films(body=body, schema=FilmWork)


@lru_cache()
def get_film_service(
    cache: AbstractCache = Depends(get_redis_cache),
    storage: AbstractStorage = Depends(get_elastic_storage),
):
    return FilmWorkService(cache=cache, storage=storage)
