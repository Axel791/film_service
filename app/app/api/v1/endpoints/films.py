from fastapi import APIRouter, Depends

from typing import List

from app.schemas.films import FilmWork
from app.services.film import film_service, FilmWorkService

router = APIRouter()


@router.get('/get/{film_id}')
async def get_film(
        film_id: str,
        film_work_service: FilmWorkService = Depends(film_service)
) -> FilmWork:
    return await film_work_service.get(film_id=film_id)


@router.get('/list')
async def list_films() -> List[FilmWork]:
    pass
