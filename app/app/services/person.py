import json

from loguru import logger

from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError

from fastapi import Depends

from typing import List
from functools import lru_cache

from app.core.config import settings
from app.db.init_redis import get_redis
from app.db.init_etl import get_elastic

from app.schemas.persons import Person
from app.schemas.films import FilmWork, FilmWorkShort

from app.exceptions.person_exception import NotFoundPerson
from app.exceptions.film_exception import NotFoundFilm


class PersonService:

    def __init__(
            self,
            redis: Redis,
            es: AsyncElasticsearch
    ) -> None:
        self._redis = redis
        self._es = es

    async def get(self, person_id: str) -> Person | None:
        person: Person | None = await self._get_person_from_cache(key=person_id)
        if person is None:
            person = await self._get_person_from_etl(person_id=person_id)
            person_str: str = json.dumps(person.dict())
            await self._put_data_to_cache(key=person_id, value=person_str)
        return person

    async def list(
            self,
            person_id: str,
            rating_order: str | None = None,
            page: int | None = 1,
            page_size: int | None = settings.default_page_size
    ) -> List[FilmWork] | None:
        list_films = await self._get_films_by_person_id(
            person_id=person_id,
            rating_order=rating_order,
            page=page,
            page_size=page_size
        )
        return list_films

    async def search(
            self,
            query: str = "",
            page: int = 1,
            page_size: int = settings.default_page_size
    ) -> Optional[List[Person]]:
        list_persons = await self._search_persons(
            query=query,
            page=page,
            page_size=page_size
        )
        return list_persons

    async def _get_person_from_etl(self, person_id: str) -> Person | None:
        try:
            doc = await self._es.get(index='persons', id=person_id)
        except NotFoundError:
            raise NotFoundPerson
        return Person(**doc['_source'])

    async def _get_person_from_cache(self, key: str) -> Person | None:
        person: bytes | None = await self._redis.get(key)
        if not person:
            return None
        person_obj = Person.parse_raw(person)
        return person_obj

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
        key: str = json.dumps(body)
        films: List[FilmWorkShort] | None = await self._get_films_from_cache(key)
        if films is None:
            try:
                response = await self._es.search(index='movies', body=body)
            except NotFoundError:
                raise NotFoundFilm
            films = [FilmWorkShort(**doc['_source']) for doc in response['hits']['hits']]

            films_str: str = json.dumps([film.dict() for film in films])
            await self._put_data_to_cache(key=key, value=films_str)
        return films

    async def _get_films_from_cache(self, key: str) -> List[FilmWorkShort] | None:
        films: bytes | None = await self._redis.get(key)
        if not films:
            return None
        films_list = [FilmWorkShort(**film) for film in json.loads(films)]
        return films_list

    async def _get_persons_from_cache(self, key: str) -> List[Person] | None:
        persons: Optional[bytes] = await self._redis.get(key)
        if not persons:
            return None
        persons_list = [Person(**person) for person in json.loads(persons)]
        return persons_list

    async def _put_data_to_cache(self, key: str, value: str, time: int = settings.FILM_CACHE_EXPIRE_IN_SECOND):
        await self._redis.setex(
            name=key,
            value=value,
            time=time,
        )

    async def _search_persons(
            self,
            query: str,
            page: int,
            page_size: int
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
        key: str = json.dumps(body)
        persons: Optional[List[Person]] = await self._get_persons_from_cache(key)
        if persons is None:
            try:
                response = await self._es.search(index='persons', body=body)
            except NotFoundError:
                raise NotFoundPerson
            persons = [Person(**doc['_source']) for doc in response['hits']['hits']]

            persons_str: str = json.dumps([person.dict() for person in persons])
            await self._put_data_to_cache(key=key, value=persons_str)
        return persons


@lru_cache()
def person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> PersonService:
    return PersonService(es=elastic, redis=redis)
