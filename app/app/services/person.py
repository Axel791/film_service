import json


from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from typing import Optional
from typing import List
from functools import lru_cache

from app.core.config import settings
from app.db.init_es import get_elastic


from app.schemas.persons import Person
from app.schemas.films import FilmWorkShort, FilmWork

from .base import SearchService
from .cacheble_service import CacheableService, get_cacheable_service


class PersonService(SearchService):

    def __init__(
            self,
            cacheable: CacheableService,
            es: AsyncElasticsearch
    ) -> None:
        super().__init__(cacheable, es)

    async def get(self, person_id: str) -> Person:
        person = await self._cacheable.get_obj_from_cache(key=person_id, schema=Person)
        if person is None:
            person = await self.get_obj_from_etl(
                obj_id=person_id,
                index='persons',
                schema=Person
            )
            person_str = json.dumps(person.dict())
            await self._cacheable.put_to_cache(key=person_id, value=person_str)
        return person

    async def list(
            self,
            person_id: str | None = None,
            rating_order: str | None = None,
            page: int | None = 1,
            page_size: int | None = settings.default_page_size
    ):
        return await self._get_films_by_person_id(
            person_id=person_id,
            rating_order=rating_order,
            page=page,
            page_size=page_size
        )

    async def search(
            self,
            query: str = "",
            page: int | None = 1,
            page_size: int | None = settings.default_page_size
    ):
        return await self._search_persons(
            query=query,
            page=page,
            page_size=page_size
        )

    async def _get_films_by_person_id(
            self,
            person_id: str,
            rating_order: str | None = None,
            page: int | None = 1,
            page_size: int | None = settings.default_page_size
    ) -> List[FilmWorkShort] | None:
        start = (page - 1) * page_size
        person = await self.get(person_id=person_id)
        film_ids = []
        for film in person.films:
            film_ids.append(film['id'])

        body = {
            "query": {
                "terms": {"id": film_ids}
            },
            "from": start,
            "size": page_size
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
        films = await self._cacheable.get_obj_from_cache(key=key, schema=FilmWorkShort)

        if films is None:
            films = await self.get_objects_from_etl(
                key=key,
                body=body,
                index='movies',
                schema=FilmWorkShort,
            )
        return films

    async def _search_persons(
            self,
            query: str,
            page: int | None = 1,
            page_size: int | None = settings.default_page_size
    ):
        start = (page - 1) * page_size
        body = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"full_name": query}}
                    ]
                }
            },
            "from": start,
            "size": page_size
        }
        key = json.dumps(body)
        persons = await self._cacheable.get_list_from_cache(key=key, schema=Person)
        if persons is None:
            persons = await self.get_objects_from_etl(
                body=body,
                key=key,
                index='persons',
                schema=Person
            )
        return persons


@lru_cache()
def get_person_service(
        cacheable: CacheableService = Depends(get_cacheable_service),
        es: AsyncElasticsearch = Depends(get_elastic)
) -> PersonService:
    return PersonService(cacheable=cacheable, es=es)
