from typing import Optional

from schemas.mixins import TimeStampedMixin, UUIDMixin


class PersonFilmWork(UUIDMixin, TimeStampedMixin):
    title: Optional[str]
    role: Optional[str]
