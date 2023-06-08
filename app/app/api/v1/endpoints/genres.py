from fastapi import APIRouter, Depends


router = APIRouter()


@router.get('/hello_genres')
async def test_func():
    return {'response': 'hello genres!'}

from fastapi import APIRouter, Depends

from typing import List, Optional

from app.schemas.genres import Genre
from app.services.genre import genre_service, GenreService

router = APIRouter()


@router.get('/get/{genre_id}')
async def get_genre(
        genre_id: str,
        genre_service: GenreService = Depends(genre_service)
) -> Genre:
    return await genre_service.get(genre_id=genre_id)
