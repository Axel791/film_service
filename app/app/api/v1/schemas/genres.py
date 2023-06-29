from app.api.v1.schemas.orjson_dump import BaseOrjson


class Genre(BaseOrjson):
    id: str
    name: str
    description: str | None
