from fastapi import APIRouter, Depends

from typing import List

from app.core.commons import PaginateQueryParams
from app.core.config import settings
from app.schemas.persons import Person
from app.schemas.films import FilmWorkShort
from app.services.person import get_person_service, PersonService


router = APIRouter()


@router.get('/get/{person_id}',
            summary='Getting a person by id.',
            description='Searches for a person by person_id and returns data about the person, '
                        'including films in which the person was involved.',
            )
async def get_person(
        person_id: str,
        person_service: PersonService = Depends(get_person_service)
) -> Person:
    return await person_service.get(person_id=person_id)


@router.get('/{person_id}/films',
            summary='Receiving films in which the person was involved.',
            description='Searches for a person by id and returns truncated information '
                        'about films in which the person was involved.',
            )
async def get_persons_films_by_id(commons: Annotated[PaginateQueryParams, Depends(PaginateQueryParams)],
        person_id: str,
        rating_order: str | None = None,
        person_service: PersonService = Depends(get_person_service)
) -> List[FilmWorkShort] | None:

    return await person_service.list(
        person_id=person_id,
        rating_order=rating_order,
        page=commons.page,
        page_size=commons.page_size
    )


@router.get('/search')
async def search_persons(commons: Annotated[PaginateQueryParams, Depends(PaginateQueryParams)],
        query: str,
        person_service: PersonService = Depends(get_person_service)
) -> List[Person]:
    return await person_service.search(
        query=query,
        page=commons.page,
        page_size=commons.page_size
    )
