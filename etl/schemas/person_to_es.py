from typing import List, Optional

from schemas.mixins import UUIDMixin


class PersonES(UUIDMixin):
    full_name: str
    films: Optional[List[dict]] = []
