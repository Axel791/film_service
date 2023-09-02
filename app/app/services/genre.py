import json
from functools import lru_cache

from fastapi import Depends

from app.api.v1.schemas.genres import Genre
from app.services.cacheble_base import AbstractCache, get_redis_cache
from app.services.storage_base import AbstractStorage, get_elastic_storage


class GenreService:
    def __init__(self, cache: AbstractCache, storage: AbstractStorage) -> None:
        self.cache = cache
        self.storage = storage

    async def get(self, genre_id: str) -> Genre:
        genre = await self.cache.get(key=genre_id, schema=Genre)
        if genre is None:
            genre = await self.storage.get(
                obj_id=genre_id, index="genres", schema=Genre
            )
            genre_str = json.dumps(genre.dict())
            await self.cache.put(key=genre_id, value=genre_str)
        return genre


@lru_cache()
def get_genre_service(
    cache: AbstractCache = Depends(get_redis_cache),
    storage: AbstractStorage = Depends(get_elastic_storage),
):
    return GenreService(cache=cache, storage=storage)
