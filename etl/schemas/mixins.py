from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UUIDMixin(BaseModel):
    id: Optional[UUID]


class TimeStampedMixin(BaseModel):
    created: Optional[datetime]
    modified: Optional[datetime]
