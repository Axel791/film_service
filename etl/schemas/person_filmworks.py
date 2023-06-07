from typing import Optional
from schemas.mixins import UUIDMixin, TimeStampedMixin


class PersonFilmWork(UUIDMixin, TimeStampedMixin):
    title: Optional[str]
    role: Optional[str]
