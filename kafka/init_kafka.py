import json
import logging
from confluent_kafka.admin import AdminClient, NewTopic
from schema_registry.client import SchemaRegistryClient
from app.core.config import settings

kafka_broker = settings.kafka_broker_url
schema_registry_url = settings.schema_registry_url

# kafka_broker = "broker:9092"
# schema_registry_url = "http://schema-registry:8081/"


topics_to_create = ["page-view", "custom-event"]


def topic_exists(admin, topic_name):
    metadata = admin.list_topics()
    for t in iter(metadata.topics.values()):
        if t.topic == topic_name:
            return True
    return False


def create_topic(admin, topic_name):
    new_topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)
    result_dict = admin.create_topics([new_topic])
    for topic, future in result_dict.items():
        try:
            future.result()
            logging.info("Topic %s created", topic)
        except Exception as e:
            logging.error("Failed to create topic %s: %s", topic, e)


def register_schema(subject, schema):
    schema_registry_client = SchemaRegistryClient({"url": schema_registry_url})
    try:
        schema_id = schema_registry_client.register(subject, schema)
        if schema_id is not None:
            logging.info("Schema registered successfully for subject '%s' with ID: %s", subject, schema_id)
        else:
            logging.error("Failed to register schema for subject '%s'", subject)
    except Exception as e:
        logging.error("Error registering schema for subject '%s': %s", subject, e)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    admin = AdminClient({"bootstrap.servers": kafka_broker})
    for topic in topics_to_create:
        if not topic_exists(admin, topic):
            create_topic(admin, topic)
            with open(f'avro_schemas/{topic}-subject.avsc', 'r') as file:
                avro_schema_contents = file.read()
                avro_schema_dict = json.loads(avro_schema_contents)
                avro_schema = json.dumps(avro_schema_dict)
            register_schema(f'{topic}-subject', avro_schema)
