import http

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Request
from pydantic import BaseModel


class CheckToken(BaseModel):
    is_valid: bool
    message: str
    user_id: str | None = None
    exp: int | None = None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> str:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN,
                                detail='Invalid authorization code.')
        if not credentials.scheme == 'Bearer':
            raise HTTPException(status_code=http.HTTPStatus.UNAUTHORIZED,
                                detail='Only Bearer token might be accepted')
        token = f'{credentials.scheme} {credentials.credentials}'
        return token


security_jwt = JWTBearer()
