from schemas.mixins import UUIDMixin

from typing import Optional, List


class PersonES(UUIDMixin):
    full_name: str
    films: Optional[List[dict]] = []

