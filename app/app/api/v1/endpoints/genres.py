from fastapi import APIRouter, Depends

from app.schemas.genres import Genre
from app.services.genre import genre_service, GenreService

router = APIRouter()


@router.get('/get/{genre_id}',
            summary='Getting a genre by id.',
            description='Searches for genre by genre_id and returns genre data if it exists.',
            )
async def get_genre(
        genre_id: str,
        genre_service: GenreService = Depends(genre_service)
) -> Genre:
    return await genre_service.get(genre_id=genre_id)
