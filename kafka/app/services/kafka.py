import asyncio
from typing import Dict
from functools import lru_cache
import json

from aiokafka import AIOKafkaProducer

from app.core.config import settings
from app.api.v1.schemas.message import Message


class KafkaService:
    def __init__(self, broker_url: str, schema_registry_url: str, group_id: str):
        self.broker_url = broker_url
        self.schema_registry_url = schema_registry_url
        self.group_id = group_id

    async def produce(self, topic: str, message: Message):
        producer = AIOKafkaProducer(bootstrap_servers=self.broker_url)
        await producer.start()
        json_message = json.dumps(message.message)
        try:
            await producer.send_and_wait(topic, json_message.encode('utf-8'))
            return "Message is sent"
        except Exception as e:
            return {"error": str(e)}
        finally:
            await producer.stop()


@lru_cache()
def get_kafka_service() -> KafkaService:
    return KafkaService(
        broker_url=settings.kafka_broker_url,
        schema_registry_url=settings.schema_registry_url,
        group_id='test'
    )
