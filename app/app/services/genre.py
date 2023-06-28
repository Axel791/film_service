import json

from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from .base import SearchService
from .cacheble_service import CacheableService, get_cacheable_service

from app.db.init_etl import get_elastic

from app.schemas.genres import Genre


class GenreService(SearchService):

    def __init__(
            self,
            cacheable: CacheableService,
            es: AsyncElasticsearch
    ) -> None:
        super().__init__(cacheable, es)

    async def get(self, genre_id: str):
        genre = self._cacheable.get_obj_from_cache(key=genre_id, schema=Genre)
        if genre is None:
            genre = await self.get_obj_from_etl(
                obj_id=genre_id,
                index='genres',
                schema=Genre
            )
            genre_str = json.dumps(genre.dict())
            await self._cacheable.put_to_cache(
                key=genre_id,
                value=genre_str
            )
        return genre


@lru_cache()
def get_genre_service(
    cacheable: CacheableService = Depends(get_cacheable_service),
    es: AsyncElasticsearch = Depends(get_elastic)
) -> GenreService:
    return GenreService(cacheable=cacheable, es=es)
