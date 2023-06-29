from abc import ABC, abstractmethod
from typing import Type, List
from functools import lru_cache

from fastapi import Depends
from pydantic import BaseModel
from elasticsearch import AsyncElasticsearch, NotFoundError

from app.db.init_es import get_elastic
from app.exceptions.base import BaseNotFound


class AbstractStorage(ABC):

    @abstractmethod
    async def get(self, *args, **kwargs):
        pass

    @abstractmethod
    async def list(self, *args, **kwargs):
        pass


class ElasticStorage(AbstractStorage):

    def __init__(self, es: AsyncElasticsearch) -> None:
        self._es = es

    async def get(
            self,
            index: str,
            obj_id: str,
            schema: Type[BaseModel],
            *args, **kwargs
    ) -> BaseModel:
        try:
            response = await self._es.get(index=index, id=obj_id)
        except NotFoundError:
            raise BaseNotFound
        return schema(**response['_source'])

    async def list(
            self,
            key: str,
            body: dict,
            index: str,
            schema: Type[BaseModel],
            *args, **kwargs
    ) -> List[BaseModel]:
        try:
            response = await self._es.search(index=index, body=body)
        except NotFoundError:
            raise BaseNotFound
        return [schema(**doc['_source']) for doc in response['hits']['hits']]


@lru_cache()
def get_elastic_storage(
        es: AsyncElasticsearch = Depends(get_elastic)
) -> ElasticStorage:
    return ElasticStorage(es=es)
