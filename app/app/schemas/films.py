from app.schemas.orjson_dump import BaseOrjson


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


class FilmWorkShort(BaseModel):
    id: str
    title: str
    imdb_rating: float | None
