import json

from pydantic import BaseModel

from elasticsearch import AsyncElasticsearch

from .base import SearchService
from .cacheble_service import CacheableService

from typing import List, Type

from app.schemas.films import FilmWork, FilmWorkShort

from app.exceptions.film_exception import NotFoundFilm


class FilmWorkService(SearchService):

    def __init__(
            self,
            cacheable: CacheableService,
            es: AsyncElasticsearch
    ) -> None:
        self._es = es
        super().__init__(cacheable)

    async def get(self, film_id: str) -> FilmWork | None:
        film: FilmWork | None = await self._cacheable.get_from_cache(key=film_id, schema=FilmWork)
        if film is None:
            film = await self._get_film_form_etl(film_id=film_id)
            film_str = json.dumps(film.dict())
            await self._cacheable.put_to_cache(key=film_id, value=film_str)
        return film

    async def list(self, genre: str | None = None, rating_order: str | None = None):
        return await self._list_films_and_filter(
            genre=genre,
            rating_order=rating_order
        )

    async def search(self, query: str = ""):
        pass

    async def _get_film_form_etl(self, film_id: str) -> FilmWork | None:
        try:
            doc = await self._es.get(index='movies', id=film_id)
        except NotFoundError:
            raise NotFoundFilm
        return FilmWork(**doc['_source'])

    async def _list_films_and_filter(
            self,
            genre: str | None = None,
            rating_order: str | None = None
    ) -> List[FilmWork] | None:
        start = (self.page - 1) * self.page_size
        body = {
            "query": {
                "match_all": {}
            },
            "from": start,
            "size": self.page_size
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
        films = await self._cacheable.get_from_cache(key=key, schema=FilmWork)
        if films is None:
            films = await self._get_response(key=key, body=body, schema=FilmWork)
        return films

    async def _search_films(
            self,
            query: str,
            page: int,
            page_size: int
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
        films = await self._cacheable.get_from_cache(key=key, schema=FilmWorkShort)
        if films is None:
            films = await self._get_response(key=key, body=body, schema=FilmWorkShort)
        return films

    async def _get_response(self, body: dict, key: str, schema: Type[BaseModel]):
        try:
            response = await self._es.search(index='movies', body=body)
        except NotFoundError:
            raise NotFoundFilm
        films = [schema(**doc['_source']) for doc in response['hits']['hits']]
        films_str: str = json.dumps([film.dict() for film in films])
        await self._cacheable.put_to_cache(key=key, value=films_str)
        return films
