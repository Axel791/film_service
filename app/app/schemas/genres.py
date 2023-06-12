from app.schemas.orjson_dump import BaseOrjson


class Genre(BaseOrjson):
    id: str
    name: str
    description: str | None
