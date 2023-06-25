from typing import List

from app.schemas.orjson_dump import BaseOrjson


class Person(BaseOrjson):
    id: str
    full_name: str
    films: List[dict] | None

