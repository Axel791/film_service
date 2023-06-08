from typing import Optional, List

import orjson
from pydantic import BaseModel

from app.schemas.orjson_dump import orjson_dumps


class Person(BaseModel):
    id: str
    full_name: str
    films: Optional[List[dict]]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
