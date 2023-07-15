from pydantic import BaseModel


class RegUserIn(BaseModel):
    email: str
    login: str
    password: str


class Token(BaseModel):
    token: str
    token_type: str
