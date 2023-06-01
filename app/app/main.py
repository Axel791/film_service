from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api
from app.core.config import settings


def create_app():
    fastapi_app = FastAPI(
        title=settings.PROJECT_SLUG,
        openapi_url=f"{settings.API_V1_STR}/openai.json"
    )

    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    fastapi_app.include_router(api.api_router, prefix=settings.API_V1_STR)
    return fastapi_app


app = create_app()