from fastapi import APIRouter

from app.api.v1.endpoints import films

api_router = APIRouter()


api_router.include_router(films.router, prefix='/films', tags=['films'])
