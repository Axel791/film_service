import sys

import sentry_sdk
from clickhouse_driver import Client
from confluent_kafka import Consumer
from loguru import logger

import backoff
from core.config import settings

logger.add(
    "/var/log/kafka_ch_etl/access-log.json",
    rotation="500 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)
logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")

sentry_sdk.init(dsn=settings.sentry_dsn)


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
            host=self.clickhouse_config["host"],
            port=self.clickhouse_config["port"],
            user=self.clickhouse_config["user"],
            password=self.clickhouse_config["password"],
            database=self.clickhouse_config["database"],
        )

    @staticmethod
    def insert_batch(clickhouse_client, topic, batch):
        insert_fields = ", ".join(batch[0].keys())
        insert_values = ", ".join(
            [
                f"'{v}'" if isinstance(v, str) else str(v)
                for record in batch
                for v in record.values()
            ]
        )
        query = f"INSERT INTO {topic}_table ({insert_fields}) VALUES {insert_values}"
        clickhouse_client.execute(query)
        logger.info("Inserted %d records into %s_table", len(batch), topic)

    @backoff.on_exception(
        backoff.expo, Exception, max_time=settings.max_backoff_time_seconds
    )
    def process_messages(self):
        clickhouse_client = self.initialize_clickhouse_client()

        for topic, consumer in self.clients.items():
            try:
                batch = []
                while True:
                    msg = consumer.poll(1.0)
                    if msg is None:
                        continue
                    if msg.error():
                        logger.error("Kafka error: %s", msg.error())
                    else:
                        value = msg.value()
                        batch.append(value)
                        if len(batch) >= 1000:
                            self.insert_batch(clickhouse_client, topic, batch)
                            batch = []
                            consumer.commit(msg)

            except KeyboardInterrupt:
                pass
            finally:
                consumer.close()


if __name__ == "__main__":
    kafka_config = {
        "bootstrap.servers": settings.kafka_broker_url,
        "group.id": settings.group_id,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    }

    clickhouse_config = {
        "host": settings.ch_host,
        "port": settings.ch_port,
        "user": settings.ch_user,
        "password": settings.ch_password,
        "database": settings.ch_database,
    }

    processor = KafkaToClickHouseProcessor(kafka_config, clickhouse_config)
    processor.initialize_consumers(["page-view", "custom-event", "movie-watched-event"])
    processor.process_messages()
