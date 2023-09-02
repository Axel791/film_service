from fastapi import Request, status
from fastapi.responses import ORJSONResponse
from starlette.middleware.base import (BaseHTTPMiddleware,
                                       RequestResponseEndpoint)


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        request_id = request.headers.get("X-Request-Id")
        if not request_id:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "X-Request-Id is required"},
            )
        response = await call_next(request)
        return response
