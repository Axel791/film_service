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
from app.schemas.films import FilmWork, FilmWorkPerson

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
            page: Optional[int] = 1,
            page_size: Optional[int] = settings.DEFAULT_PAGE_SIZE
    ) -> List[FilmWork] | None
        list_films = await self._get_films_by_person_id(
            person_id=person_id,
            rating_order=rating_order,
            page=page,
            page_size=page_size
        )
        return list_films

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

    async def _get_films_by_person_id(self, person_id: str,
                                      rating_order: str | None = None,
                                      page: Optional[int] = 1,
                                      page_size: Optional[int] = settings.DEFAULT_PAGE_SIZE) -> List[FilmWorkPerson] | None:

                                    
        start = (page - 1) * page_size
        person = await self.get(person_id=person_id)
        film_ids = []
        for film in person.films:
            film_ids.append(film['id'])
        print(film_ids)

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
        films: List[FilmWorkPerson] | None = await self._get_films_from_cache(key)
        if films is None:
            try:
                response = await self._es.search(index='movies', body=body)
            except NotFoundError:
                raise NotFoundFilm
            films = [FilmWorkPerson(**doc['_source']) for doc in response['hits']['hits']]

            films_str: str = json.dumps([film.dict() for film in films])
            await self._put_data_to_cache(key=key, value=films_str)
        return films

    async def _get_films_from_cache(self, key: str) -> List[FilmWorkPerson] | None:
        films: bytes | None = await self._redis.get(key)
        if not films:
            return None
        films_list = [FilmWorkPerson(**film) for film in json.loads(films)]
        return films_list

    async def _put_data_to_cache(self, key: str, value: str, time: int = settings.film_cache_expire_in_second):
        await self._redis.setex(
            name=key,
            value=value,
            time=time,
        )


@lru_cache()
def person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> PersonService:
    return PersonService(es=elastic, redis=redis)
