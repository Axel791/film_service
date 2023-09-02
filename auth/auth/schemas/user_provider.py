from datetime import datetime

from pydantic import BaseModel


class UserProvider(BaseModel):
    timestamp: datetime
