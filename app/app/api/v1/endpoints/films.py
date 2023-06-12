from fastapi import APIRouter, Depends

from typing import List

from app.schemas.films import FilmWork
from app.services.film import film_service, FilmWorkService

router = APIRouter()


@router.get('/get/{film_id}',
            summary='Getting a movie by id.',
            description='Searches for film by film_id and returns film data if it exists.',
            )
async def get_film(
        film_id: str,
        film_work_service: FilmWorkService = Depends(film_service)
) -> FilmWork:
    return await film_work_service.get(film_id=film_id)


@router.get('/list',
            summary='Getting all movies.',
            description='Get all movies filtered by genre and sorted by rating.',
            )
async def list_films(
        genres: str | None = None,
        rating_order: str | None = None,
        film_work_service: FilmWorkService = Depends(film_service)
) -> List[FilmWork]:
    return await film_work_service.list(genre=genres, rating_order=rating_order)
