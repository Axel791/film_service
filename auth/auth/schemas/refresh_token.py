import datetime

from pydantic import BaseModel


class TokenCreate(BaseModel):
    token: str
    expiry: datetime.datetime


