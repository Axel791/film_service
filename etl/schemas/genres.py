from datetime import datetime
from uuid import UUID
from typing import Optional
from schemas.mixins import UUIDMixin, TimeStampedMixin


class Genre(UUIDMixin, TimeStampedMixin):
    name: Optional[str]
    description: Optional[str]


class GenreFilmWork(UUIDMixin):
    created: Optional[datetime]

    genre_id: Optional[UUID]
    film_work_id: Optional[UUID]
