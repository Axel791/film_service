from typing import Optional, List

import orjson
from pydantic import BaseModel

from app.schemas.mixins import orjson_dumps


class Genre(BaseModel):
    id: str
    name: str
    description: Optional[List[dict]]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
