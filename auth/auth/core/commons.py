from fastapi import Query

from auth.core.config import settings


class PaginateQueryParams:
    """Dependency class to parse pagination query params."""

    def __init__(
        self,
        page: int = Query(
            1,
            title="Page number",
            description="Page number to return",
            ge=1,
        ),
        page_size: int = Query(
            settings.default_page_size,
            title="Size of page.",
            description="The number of records returned per page",
            ge=1,
            le=500,
        ),
    ):
        self.page = page
        self.page_size = page_size