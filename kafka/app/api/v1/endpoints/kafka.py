from typing import Dict
from fastapi import APIRouter, Depends

from app.services.kafka import get_kafka_service, KafkaService
from app.api.v1.schemas.message import Message
from app.auth.auth_bearer import security_jwt


router = APIRouter()


@router.post('/produce/{topic}',
            summary='Producing a message to kafka',
            description='Produces a message to {kafka_topic}',
            dependencies=[Depends(security_jwt)]
            )
async def produce(
        topic: str,
        message: Message,
        kafka_service: KafkaService = Depends(get_kafka_service),

):
    return await kafka_service.produce(topic=topic, message=message)
