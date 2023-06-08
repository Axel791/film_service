from fastapi import APIRouter, Depends


router = APIRouter()


@router.get('/hello_persons')
async def test_func():
    return {'response': 'hello persons!'}
