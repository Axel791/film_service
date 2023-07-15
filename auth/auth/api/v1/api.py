from fastapi import APIRouter
from app.api.v1.endpoints import auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix='/register', tags=['registration'])
api_router.include_router(auth.router, prefix='/login', tags=['login'])
api_router.include_router(auth.router, prefix='/refresh-token', tags=['refresh'])
