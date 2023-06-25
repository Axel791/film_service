import json

from typing import List

from elasticsearch import AsyncElasticsearch

from .base import SearchService
from .cacheble_service import CacheableService

from app.schemas.films import FilmWork, FilmWorkShort


class FilmWorkService(SearchService):

    def __init__(
            self,
            cacheable: CacheableService,
            es: AsyncElasticsearch
    ) -> None:
        self._es = es
        super().__init__(cacheable, es)

    async def get(self, film_id: str) -> FilmWork | None:
        film = await self._cacheable.get_obj_from_cache(key=film_id, schema=FilmWork)
        if film is None:
            film = await self.get_obj_from_etl(obj_id=film_id, index='movies', schema=FilmWork)
            film_str = json.dumps(film.dict())
            await self._cacheable.put_to_cache(key=film_id, value=film_str)
        return film

    async def list(self, genre: str | None = None, rating_order: str | None = None):
        return await self._list_films_and_filter(
            genre=genre,
            rating_order=rating_order
        )

    async def search(self, query: str = "") -> List[FilmWorkShort] | None:
        return await self._search_films(query=query)

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

    async def _search_films(self, query: str) -> List[FilmWorkShort] | None:
        start = (self.page - 1) * self.page_size
        body = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"title": query}}
                    ]
                }
            },
            "from": start,
            "size": self.page_size
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
