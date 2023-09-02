from datetime import datetime
from typing import Optional
from uuid import UUID

from schemas.mixins import TimeStampedMixin, UUIDMixin


class Genre(UUIDMixin, TimeStampedMixin):
    name: Optional[str]
    description: Optional[str]


class GenreFilmWork(UUIDMixin):
    created: Optional[datetime]

    genre_id: Optional[UUID]
    film_work_id: Optional[UUID]
