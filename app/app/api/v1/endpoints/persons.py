from fastapi import APIRouter, Depends

from typing import List, Optional

from app.schemas.persons import Person
from app.schemas.films import FilmWork, FilmWorkPerson
from app.services.person import person_service, PersonService

router = APIRouter()


@router.get('/get/{person_id}')
async def get_person(
        person_id: str,
        person_service: PersonService = Depends(person_service)
) -> Person:
    return await person_service.get(person_id=person_id)


@router.get('/{person_id}/films')
async def list_films(
        person_id: str,
        rating_order: Optional[str] = None,
        person_service: PersonService = Depends(person_service)
) -> List[FilmWorkPerson]:
    return await person_service.list(person_id=person_id, rating_order=rating_order)
