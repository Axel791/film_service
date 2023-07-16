from fastapi import APIRouter
from auth.api.v1.endpoints import auth_endpoint

api_router = APIRouter()

api_router.include_router(auth_endpoint.router, prefix='/auth', tags=['auth'])
