from fastapi import APIRouter, Depends


router = APIRouter()


@router.get('/hello_genres')
async def test_func():
    return {'response': 'hello genres!'}
