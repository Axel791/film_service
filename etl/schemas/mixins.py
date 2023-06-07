from uuid import UUID
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class UUIDMixin(BaseModel):
    id: Optional[UUID]


class TimeStampedMixin(BaseModel):
    created: Optional[datetime]
    modified: Optional[datetime]
