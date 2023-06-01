from fastapi import APIRouter, Depends


router = APIRouter()


@router.get('/hello_world')
async def test_func():
    return {'response': 'hello world!'}
