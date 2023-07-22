import json

from typing import List, Type
from functools import lru_cache

from fastapi import Depends
from pydantic import BaseModel

from app.services.cacheble_base import AbstractCache, get_redis_cache
from app.services.storage_base import AbstractStorage, get_elastic_storage

from app.core.config import settings

from app.api.v1.schemas.films import FilmWorkShort
from app.api.v1.schemas.persons import Person


class PersonService:
    def __init__(
            self,
            cache: AbstractCache,
            storage: AbstractStorage
    ) -> None:
        self.cache = cache
        self.storage = storage

    async def get(self, person_id: str) -> Person:
        person = await self.cache.get(
            key=person_id,
            schema=Person
        )
        if person is None:
            person = await self.storage.get(
                obj_id=film_id,
                index='persons',
                schema=Person
            )
            person_str = json.dumps(film.dict())
            await self.cache.put(key=person_id, value=person_str)
        return person

    async def list(
            self,
            person_id: str | None = None,
            rating_order: str | None = None,
            page: int | None = 1,
            page_size: int | None = settings.default_page_size
    ) -> List[FilmWorkShort] | None:
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
    ) -> List[Person] | None:
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

        return await self._return_persons(
            body=body,
            schema=FilmWorkShort,
            index='movies'
        )

    async def _search_persons(
            self,
            query: str,
            page: int | None = 1,
            page_size: int | None = settings.default_page_size
    ) -> List[Person] | None:
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
        return await self._return_persons(
            body=body,
            schema=Person,
            index='persons'
        )

    async def _return_persons(
            self,
            body: dict,
            index: str,
            schema: Type[BaseModel]
    ) -> Type[BaseModel] | None:
        key = json.dumps(body)
        persons = await self.cache.list(key=key, schema=schema)
        if persons is None:
            persons = await self.storage.list(
                key=key,
                body=body,
                schema=schema,
                insex=index
            )
            persons_str = json.dumps([film.dict() for film in films])
            await self.cache.put(key=key, value=persons_str)
        return persons


@lru_cache()
def get_person_service(
        cache: AbstractCache = Depends(get_redis_cache),
        storage: AbstractStorage = Depends(get_elastic_storage)
):
    return PersonService(cache=cache, storage=storage)