import sys
from typing import Annotated, List

from fastapi import APIRouter, Depends
from loguru import logger
from starlette.requests import Request

from app.api.v1.schemas.films import FilmWorkShort
from app.api.v1.schemas.persons import Person
from app.core.commons import PaginateQueryParams
from app.services.person import PersonService, get_person_service

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
    "/get/{person_id}",
    summary="Getting a person by id.",
    description="Searches for a person by person_id and returns data about the person, "
    "including films in which the person was involved.",
)
async def get_person(
    request: Request,
    person_id: str,
    person_service: PersonService = Depends(get_person_service),
) -> Person:
    x_request_id = get_x_request_id(request)
    logger.bind(x_request_id=x_request_id).info("Getting person by %s", person_id)
    return await person_service.get(person_id=person_id)


@router.get(
    "/{person_id}/films",
    summary="Receiving films in which the person was involved.",
    description="Searches for a person by id and returns truncated information "
    "about films in which the person was involved.",
)
async def get_persons_films_by_id(
    commons: Annotated[PaginateQueryParams, Depends(PaginateQueryParams)],
    request: Request,
    person_id: str,
    rating_order: str | None = None,
    person_service: PersonService = Depends(get_person_service),
) -> List[FilmWorkShort] | None:
    x_request_id = get_x_request_id(request)
    logger.bind(x_request_id=x_request_id).info("List films by person %s", person_id)
    return await person_service.list(
        person_id=person_id,
        rating_order=rating_order,
        page=commons.page,
        page_size=commons.page_size,
    )


@router.get("/search")
async def search_persons(
    commons: Annotated[PaginateQueryParams, Depends(PaginateQueryParams)],
    request: Request,
    query: str,
    person_service: PersonService = Depends(get_person_service),
) -> List[Person]:
    x_request_id = get_x_request_id(request)
    logger.bind(x_request_id=x_request_id).info("Search films by query %s", query)
    return await person_service.search(
        query=query, page=commons.page, page_size=commons.page_size
    )
