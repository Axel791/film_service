from typing import List, Optional

from schemas.mixins import UUIDMixin


class FilmWorkES(UUIDMixin):
    title: str
    imdb_rating: Optional[float]
    description: Optional[str]
    creation_date: Optional[str]
    type: str
    genres: Optional[List[dict]]
    persons: Optional[List[dict]]
    director: Optional[List[str]]
    actors_names: Optional[List[str]] = []
    writers_names: Optional[List[str]] = []
    actors: Optional[List[dict]] = []
    writers: Optional[List[dict]] = []
