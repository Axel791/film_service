from jose import jwt, exceptions
from pydantic import BaseModel

from auth.core.config import settings


class CheckToken(BaseModel):
    is_valid: bool
    message: str
    user_id: str | None = None
    exp: int | None = None


def check_token(secret: str, token: str) -> CheckToken:
    try:
        token_data = jwt.decode(token, secret, algorithms=settings.AlGORITHM)
        check_data = CheckToken(
            is_valid=True,
            message="Token is valid",
            user_id=token_data.get("login"),
            exp=token_data.get("exp"),
        )
    except exceptions.ExpiredSignatureError:
        check_data = CheckToken(is_valid=False, message="Token has expired")
    except exceptions.JWTError:
        check_data = CheckToken(is_valid=False, message="Token is invalid")
    return check_data
