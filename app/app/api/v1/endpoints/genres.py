import sys

from fastapi import APIRouter, Depends
from loguru import logger
from starlette.requests import Request

from app.api.v1.schemas.genres import Genre
from app.services.genre import GenreService, get_genre_service

router = APIRouter()

logger.add(
    "/var/log/api/access-log.json",
    rotation="500 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)
logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")


def get_x_request_id(request: Request):
    return request.headers.get("X-Request-Id", "N/A")


@router.get(
    "/get/{genre_id}",
    summary="Getting a genre by id.",
    description="Searches for genre by genre_id and returns genre data if it exists.",
)
async def get_genre(
    request: Request,
    genre_id: str,
    genre_service: GenreService = Depends(get_genre_service),
) -> Genre:
    x_request_id = get_x_request_id(request)
    logger.bind(x_request_id=x_request_id).info("Getting genre %s", genre_id)
    return await genre_service.get(genre_id=genre_id)
