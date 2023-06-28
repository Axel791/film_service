import time
from settings import test_settings


from elasticsearch import Elasticsearch

if __name__ == '__main__':
    hosts = f'{test_settings.es_schema}://{test_settings.es_host}:{test_settings.es_port}'
    es_client = Elasticsearch(hosts=hosts, validate_cert=False, use_ssl=False)
    while True:
        if es_client.ping():
            break
        time.sleep(1)

