import datetime
from pydantic import BaseModel


class LoginEvent(BaseModel):
    timestamp: datetime
