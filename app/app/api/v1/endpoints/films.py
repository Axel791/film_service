import sys
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from starlette.requests import Request

from app.api.v1.schemas.films import FilmWork, FilmWorkShort
from app.auth.check_authorisation import check_authorisation
from app.auth.jwt_bearer import CheckToken, security_jwt
from app.core.commons import PaginateQueryParams
from app.services.film import FilmWorkService, get_film_service

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
    "/get/{film_id}",
    summary="Getting a movie by id.",
    description="Searches for film by film_id and returns film data if it exists.",
)
async def get_film(
    request: Request,
    film_id: str,
    film_work_service: FilmWorkService = Depends(get_film_service),
    auth_data: str = Depends(security_jwt),
) -> FilmWork:
    check_token: CheckToken = check_authorisation(token=auth_data)
    x_request_id = get_x_request_id(request)
    logger.bind(x_request_id=x_request_id).info("Getting film %s", film_id)
    if not check_token.is_valid:
        logger.error("Invalid token received")
        raise HTTPException(status_code=401, detail=check_token.message)

    logger.info(f"Getting film with ID: {film_id}")
    film_data = await film_work_service.get(film_id=film_id)
    logger.debug(f"Retrieved film data: {film_data}")
    return film_data


@router.get(
    "/list",
    summary="Getting all movies.",
    description="Get all movies filtered by genre and sorted by rating.",
)
async def list_films(
    commons: Annotated[PaginateQueryParams, Depends(PaginateQueryParams)],
    request: Request,
    genres: str | None = None,
    rating_order: str | None = None,
    film_work_service: FilmWorkService = Depends(get_film_service),
    auth_data: str = Depends(security_jwt),
) -> List[FilmWork]:
    x_request_id = get_x_request_id(request)
    logger.bind(x_request_id=x_request_id)
    check_token: CheckToken = check_authorisation(token=auth_data)
    if not check_token.is_valid:
        raise HTTPException(status_code=401, detail=check_token.message)
    return await film_work_service.list(
        genre=genres,
        rating_order=rating_order,
        page=commons.page,
        page_size=commons.page_size,
    )


@router.get("/search")
async def search_films(
    commons: Annotated[PaginateQueryParams, Depends(PaginateQueryParams)],
    request: Request,
    query: str,
    film_work_service: FilmWorkService = Depends(get_film_service),
    auth_data: str = Depends(security_jwt),
) -> List[FilmWorkShort]:
    x_request_id = get_x_request_id(request)
    logger.bind(x_request_id=x_request_id)
    check_token: CheckToken = check_authorisation(token=auth_data)
    if not check_token.is_valid:
        raise HTTPException(status_code=401, detail=check_token.message)
    return await film_work_service.search(
        query=query, page=commons.page, page_size=commons.page_size
    )
