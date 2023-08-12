from fastapi import APIRouter

from app.api.v1.endpoints import kafka

api_router = APIRouter()

api_router.include_router(kafka.router, prefix='/kafka', tags=['kafka'])
