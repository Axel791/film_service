from abc import ABC, abstractmethod
from typing import Type

from elasticsearch import AsyncElasticsearch, NotFoundError
from pydantic import BaseModel

from app.core.config import settings

from .cacheble_service import CacheableService

from app.exceptions.base import BaseNotFound


class SearchService(ABC):
    page: int = 1
    page_size: int = settings.default_page_size

    def __init__(
            self,
            cacheable: CacheableService,
            es: AsyncElasticsearch
    ) -> None:
        self._cacheable = cacheable
        self._es = es

    @abstractmethod
    async def get(self, obj_id: str):
        raise NotImplementedError

    async def list(
            self,
            obj: str | None = None,
            rating_order: str | None = None,
    ):
        pass

    async def search(self, query: str = ""):
        pass

    async def get_objects_from_etl(
            self,
            body: dict,
            key: str,
            index: str,
            schema: Type[BaseModel]
    ):
        try:
            response = await self._es.search(index=index, body=body)
        except NotFoundError:
            raise BaseNotFound
        objects = [schema(**doc['_source']) for doc in response['hits']['hits']]
        obj_str: str = json.dumps([obj.dict() for obj in objects])
        await self._cacheable.put_to_cache(key=key, value=obj_str)
        return objects

    async def get_obj_from_etl(self, obj_id: str, index: str, schema: Type[BaseModel]):
        try:
            doc = await self._es.get(index=index, id=obj_id)
        except NotFoundError:
            raise BaseNotFound
        return schema(**doc['_source'])

