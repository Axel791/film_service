from pydantic import BaseModel


class RegUserIn(BaseModel):
    email: str
    login: str
    password: str

