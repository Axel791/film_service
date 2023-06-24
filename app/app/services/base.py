from abc import ABC, abstractmethod

from app.core.config import settings

from .cacheble_service import CacheableService


class SearchService(ABC):
    page: int = 1
    page_size: int = settings.default_page_size

    def __init__(self, cacheable: CacheableService) -> None:
        self._cacheable = cacheable

    @abstractmethod
    async def get(self, obj_id: str):
        raise NotImplementedError

    @abstractmethod
    async def list(
            self,
            genre: str | None = None,
            rating_order: str | None = None,
    ):
        pass

    @abstractmethod
    async def search(self, query: str = ""):
        pass


