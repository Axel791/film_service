from uuid import UUID
import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    login: str
    password: str
    email: str



class UserInDB(BaseModel):
    id: UUID
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    token: str
    expiry: datetime.datetime
