from fastapi import APIRouter

from auth.api.v1.endpoints import auth, role

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(role.router, prefix="/role", tags=["role"])
