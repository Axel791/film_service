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

    def produce_message(self, topic: str, message: Message) -> Dict[str, str]:
        producer = self._create_producer()

        try:
            producer.produce(topic, message.message.encode('utf-8'))
            producer.flush()
            return {"message": message}
        except Exception as e:
            return {"error": str(e)}
        finally:
            producer.close()

    def create_consumer(self) -> Consumer:
        consumer_config = {
            "bootstrap.servers": self.broker_url,
            "group.id": self.group_id,
            "auto.offset.reset": "earliest"
        }
        return Consumer(consumer_config)

    def consume_messages(self, topic: str) -> Dict[str, Message]:
        consumer = self._create_consumer()
        consumer.subscribe([topic])
        messages = []

        try:
            while True:
                msg = consumer.poll(1.0)  # Poll for messages every 1 second
                msg_data = json.loads(msg.value)
                msg = Message(**msg_data)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        break
                    else:
                        raise KafkaError(msg.error())
                messages.append(msg.decode('utf-8'))
        except KeyboardInterrupt:
            pass
        except KafkaError as e:
            return {"error": str(e)}
        finally:
            consumer.unsubscribe()
            consumer.close()

        return {"messages": messages}


@lru_cache()
def get_kafka_service() -> KafkaService:
    return KafkaService(
        broker_url=settings.kafka_broker_url,
        schema_registry_url=settings.schema_registry_url,
        group_id='test'
    )
