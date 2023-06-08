from typing import Optional, List

from orjson import orjson
from pydantic import BaseModel

from app.schemas.mixins import orjson_dumps


class Filmwork(BaseModel):
    id: str
    title: str
    description: Optional[str]
    imdb_rating: Optional[float]
    genre: List[dict]
    director: List[str]
    actors_names: List[str]
    writers_names: List[str]
    actors: Optional[List[dict]]
    writers: Optional[List[dict]]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
