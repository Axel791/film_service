from contextlib import asynccontextmanager

import sentry_sdk
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from app.api.v1 import api
from app.core.config import settings
from app.db import init_es, init_redis
from app.exceptions.base import BaseNotFound

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    integrations=[SentryAsgiMiddleware],
)


def create_app(lifespan):
    fastapi_app = FastAPI(
        root_path="/app",
        title=settings.project_slug,
        openapi_url=f"{settings.api_v1_str}/openai.json",
        lifespan=lifespan,
    )

    fastapi_app.add_middleware(
        CORSMiddleware,
        SentryAsgiMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    fastapi_app.include_router(api.api_router, prefix=settings.api_v1_str)
    return fastapi_app


@asynccontextmanager
async def lifespan():
    init_redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)

    init_es.es = AsyncElasticsearch(
        hosts=f"{settings.etl_schema}://{settings.etl_host}:{settings.etl_port}"
    )

    yield

    await init_es.es.close()
    await init_redis.redis.close()


app = create_app(lifespan=lifespan)


@app.exception_handler(BaseNotFound)
async def custom_http_exception_handler(request, exc):
    return Response(status_code=404, content="Not found")
