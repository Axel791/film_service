from fastapi import Request
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from auth.db import init_redis
from auth.core.config import settings
from auth.utils.check_jwt_token import check_token
from auth.utils.rate_limiter import RateLimiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # если запрос не авторизованный берем в качестве идентификатора ip-адрес юзера
        user_id = str(request.client.host)
        # если запрос авторизованный берем user_id из токена если он валидный
        bearer_token = request.headers.get("authorization")
        if bearer_token is not None:
            token = bearer_token.split()[-1]
            token_data = check_token(secret=settings.JWT_SECRET_KEY, token=token)
            if token_data.is_valid and token_data.user_id is not None:
                user_id = token_data.user_id
        rate_limiter = RateLimiter(init_redis.redis_for_rate_limiter)
        if not await rate_limiter.check_rate_limit(user_id):
            return JSONResponse(
                status_code=429, content={"warning": "Too many requests per minute"}
            )
        response = await call_next(request)
        return response
