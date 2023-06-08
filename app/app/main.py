from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch

from app.api.v1 import api

from app.core.config import settings

from app.db import init_etl
from app.db import init_redis


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


@app.on_event('startup')
async def startup():
    init_redis.redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT
    )
    init_etl.es = AsyncElasticsearch(
        hosts=[f'{settings.ETL_HOST}:{settings.ETL_PORT}']
    )


@app.on_event('shutdown')
async def shutdown():
    await init_etl.es.close()
    await init_redis.redis.close()
