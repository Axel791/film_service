from loguru import logger
from core.config import settings

import logging

from clickhouse_driver import Client

from confluent_kafka import Consumer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KafkaToClickHouseProcessor:
    def __init__(self, kafka_config, clickhouse_config):
        self.kafka_config = kafka_config
        self.clickhouse_config = clickhouse_config
        self.clients = {}

    def initialize_consumers(self, topics):
        for topic in topics:
            consumer = Consumer(self.kafka_config)
            consumer.subscribe([topic])
            self.clients[topic] = consumer

    def initialize_clickhouse_client(self):
        return Client(
            host=self.clickhouse_config['host'],
            port=self.clickhouse_config['port'],
            user=self.clickhouse_config['user'],
            password=self.clickhouse_config['password'],
            database=self.clickhouse_config['database']
        )

    def process_messages(self):
        clickhouse_client = self.initialize_clickhouse_client()

        for topic, consumer in self.clients.items():
            try:
                while True:
                    msg = consumer.poll(1.0)
                    if msg is None:
                        continue
                    if msg.error():
                        logger.error("Kafka error: %s", msg.error())
                    else:
                        value = msg.value()
                        insert_fields = ', '.join(value.keys())
                        insert_values = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) for v in value.values()])
                        query = f"INSERT INTO {topic}_table ({insert_fields}) VALUES ({insert_values})"
                        clickhouse_client.execute(query)
                        logger.info("Inserted into %s_table: %s", topic, value)
            except KeyboardInterrupt:
                pass
            finally:
                consumer.close()


if __name__ == "__main__":
    kafka_config = {
        'bootstrap.servers': settings.kafka_broker_url,
        'group.id': settings.group_id,
        'auto.offset.reset': 'earliest'
    }

    clickhouse_config = {
        'host': settings.ch_host,
        'port': settings.ch_port,
        'user': settings.ch_user,
        'password': settings.ch_password,
        'database': settings.ch_database
    }

    processor = KafkaToClickHouseProcessor(kafka_config, clickhouse_config)
    processor.initialize_consumers(["page-view", "custom-event", "movie-watched-event"])
    processor.process_messages()