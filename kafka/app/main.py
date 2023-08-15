from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware


from app.api.v1 import api

from app.core.config import settings


def create_app():
    fastapi_app = FastAPI(
        root_path='/app',
        title=settings.project_slug,
        openapi_url=f"{settings.api_v1_str}/openai.json"
    )

    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    fastapi_app.include_router(api.api_router, prefix=settings.api_v1_str)
    return fastapi_app


app = create_app()
