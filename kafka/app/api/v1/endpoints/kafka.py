import sys
from fastapi import APIRouter, Depends

from app.services.kafka import get_kafka_service, KafkaService
from app.api.v1.schemas.message import Message
from app.auth.auth_bearer import security_jwt

from loguru import logger
from starlette.requests import Request

router = APIRouter()

logger.add(
    "/var/log/auth/access-log.json",
    rotation="500 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)
logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")


def get_x_request_id(request: Request):
    return request.headers.get("X-Request-Id", "N/A")


@router.post(
    "/produce/{topic}",
    summary="Producing a message to kafka",
    description="Produces a message to {kafka_topic}",
    dependencies=[Depends(security_jwt)],
)
async def produce(
    request: Request,
    topic: str,
    message: Message,
    kafka_service: KafkaService = Depends(get_kafka_service),
):
    x_request_id = get_x_request_id(request)
    logger.bind(x_request_id=x_request_id).info("Produced message to topic %s", topic)
    return await kafka_service.produce(topic=topic, message=message)
