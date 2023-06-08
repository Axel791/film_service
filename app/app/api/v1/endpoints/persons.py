from fastapi import APIRouter, Depends

from typing import List, Optional

from app.schemas.persons import Person
from app.services.person import person_service, PersonService

router = APIRouter()


@router.get('/get/{person_id}')
async def get_person(
        person_id: str,
        person_service: PersonService = Depends(person_service)
) -> Person:
    return await person_service.get(person_id=person_id)
