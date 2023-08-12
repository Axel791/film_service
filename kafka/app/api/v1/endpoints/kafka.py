from typing import Dict
from fastapi import APIRouter, Depends

from app.services.kafka import get_kafka_service, KafkaService
from app.api.v1.schemas.message import Message


router = APIRouter()


@router.post('/produce/{topic}',
            summary='Producing a message to kafka',
            description='Produces a message to {kafka_topic}',
            )
async def produce(
        topic: str,
        message: Message,
        kafka_service: KafkaService = Depends(get_kafka_service)
) -> Dict[str, Message]:
    return await kafka_service.produce(topic=topic, message=message)
