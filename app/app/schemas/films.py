from typing import Optional, List

from orjson import orjson
from pydantic import BaseModel

from app.schemas.orjson_dump import orjson_dumps


class FilmWork(BaseModel):
    id: str
    title: str
    description: Optional[str]
    imdb_rating: Optional[float]
    genre: Optional[list]
    director: str
    actors_names: str
    writers_names: str
    actors: Optional[list]
    writers: Optional[list]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
