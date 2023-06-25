from fastapi import APIRouter, Depends

from typing import List

from app.core.config import settings
from app.schemas.persons import Person
from app.schemas.films import FilmWorkShort
from app.services.person import person_service, PersonService

router = APIRouter()


@router.get('/get/{person_id}',
            summary='Getting a person by id.',
            description='Searches for a person by person_id and returns data about the person, '
                        'including films in which the person was involved.',
            )
async def get_person(
        person_id: str,
        person_service: PersonService = Depends(person_service)
) -> Person:
    return await person_service.get(person_id=person_id)


@router.get('/{person_id}/films',
            summary='Receiving films in which the person was involved.',
            description='Searches for a person by id and returns truncated information '
                        'about films in which the person was involved.',
            )
async def list_films(
        person_id: str,
        rating_order: str | None = None,
        page: Optional[int] = 1,
        page_size: Optional[int] = settings.DEFAULT_PAGE_SIZE,
        person_service: PersonService = Depends(person_service)
) -> List[FilmWorkShort] | None:

    return await person_service.list(person_id=person_id, rating_order=rating_order,
                                     page=page, page_size=page_size)


@router.get('/search')
async def list_persons(
        query: str,
        page: Optional[int] = 1,
        page_size: Optional[int] = settings.DEFAULT_PAGE_SIZE,
        person_service: PersonService = Depends(person_service)
) -> List[Person]:
    return await person_service.search(query=query, page=page, page_size=page_size)
