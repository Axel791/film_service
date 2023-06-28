from app.schemas.orjson_dump import BaseOrjson
from pydantic import BaseModel

class FilmWork(BaseOrjson):
    id: str
    title: str
    description: str | None
    imdb_rating: float | None
    genre: list | None
    director: str
    actors_names: str
    writers_names: str
    actors: list | None
    writers: list | None


class FilmWorkShort(BaseOrjson):
    id: str
    title: str
    imdb_rating: float | None
