import time
from core.config import settings

from elasticsearch import Elasticsearch

if __name__ == '__main__':
    hosts = f'{settings.es_schema}://{settings.es_host}:{settings.es_port}'
    es_client = Elasticsearch(hosts=hosts, validate_cert=False, use_ssl=False)
    while True:
        if es_client.ping():
            break
        time.sleep(1)