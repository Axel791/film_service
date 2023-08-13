from typing import Dict
from functools import lru_cache
import json


from confluent_kafka import Producer, Consumer, KafkaError

from app.core.config import settings
from app.api.v1.schemas.message import Message


class KafkaService:
    def __init__(self, broker_url: str, schema_registry_url: str, group_id: str):
        self.broker_url = broker_url
        self.schema_registry_url = schema_registry_url
        self.group_id = group_id

    def _create_producer(self) -> Producer:
        producer_config = {
            "bootstrap.servers": self.broker_url,
            "client.id": "fastapi-producer"
        }
        return Producer(producer_config)

    async def produce(self, topic: str, message: Message) -> Dict[str, str]:
        producer = self._create_producer()
        json_message = json.dumps(message.message)
        try:
            await self._produce_message(producer, topic, json_message)
            await self._flush_and_close(producer)
        except Exception as e:
            return {"error": str(e)}

    async def _produce_message(self, producer: Producer, topic: str, message: str) -> None:
        await producer.produce(topic, message.encode('utf-8'))
        await producer.poll(10000)

    async def _flush_and_close(self, producer: Producer) -> None:
        await producer.flush()


@lru_cache()
def get_kafka_service() -> KafkaService:
    return KafkaService(
        broker_url=settings.kafka_broker_url,
        schema_registry_url=settings.schema_registry_url,
        group_id='test'
    )
