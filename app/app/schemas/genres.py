from typing import Optional

import orjson
from pydantic import BaseModel

from app.schemas.orjson_dump import orjson_dumps


class Genre(BaseModel):
    id: str
    name: str
    description: Optional[str]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
