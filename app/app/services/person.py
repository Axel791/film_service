from loguru import logger

from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError

from fastapi import Depends

from typing import Optional, List
from functools import lru_cache

from app.db.init_redis import get_redis
from app.db.init_etl import get_elastic

from app.schemas.persons import Person

from app.exceptions.person_exception import NotFoundPerson


class PersonService:

    def __init__(
            self,
            redis: Redis,
            es: AsyncElasticsearch
    ) -> None:
        self._redis = redis
        self._es = es

    async def get(self, person_id: str) -> Optional[Person]:
        person = await self._get_person_from_etl(person_id=person_id)
        return person

    async def _get_person_from_etl(self, person_id: str) -> Optional[Person]:
        try:
            doc = await self._es.get(index='persons', id=person_id)
        except NotFoundError:
            raise NotFoundPerson
        return Person(**doc['_source'])

@lru_cache()
def person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> PersonService:
    return PersonService(es=elastic, redis=redis)
