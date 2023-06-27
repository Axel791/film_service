from fastapi import APIRouter, Depends

from typing import List

from app.core.config import settings
from app.schemas.films import FilmWork, FilmWorkShort
from app.services.film import get_film_service, FilmWorkService

router = APIRouter()


@router.get('/get/{film_id}',
            summary='Getting a movie by id.',
            description='Searches for film by film_id and returns film data if it exists.',
            )
async def get_film(
        film_id: str,
        film_work_service: FilmWorkService = Depends(get_film_service)
) -> FilmWork:
    return await film_work_service.get(film_id=film_id)


@router.get('/list',
            summary='Getting all movies.',
            description='Get all movies filtered by genre and sorted by rating.',
            )
async def list_films(
        genres: str | None = None,
        rating_order: str | None = None,
        page: int | None = 1,
        page_size: int | None = settings.default_page_size,
        film_work_service: FilmWorkService = Depends(get_film_service)
) -> List[FilmWork]:
    return await film_work_service.list(genre=genres, rating_order=rating_order)


@router.get('/search')
async def list_films(
        query: str,
        page: int | None = 1,
        page_size: int | None = settings.default_page_size,
        film_work_service: FilmWorkService = Depends(get_film_service)
) -> List[FilmWorkShort]:
    return await film_work_service.search(query=query)
