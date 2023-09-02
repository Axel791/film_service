from datetime import datetime
from typing import Optional
from uuid import UUID

from schemas.mixins import TimeStampedMixin, UUIDMixin


class Person(UUIDMixin, TimeStampedMixin):
    full_name: Optional[str]
    role: Optional[str]


class PersonFilmWork(UUIDMixin):
    role: Optional[str]
    created: Optional[datetime]

    person_id: Optional[UUID]
    film_work_id: Optional[UUID]
