import time

from elasticsearch import Elasticsearch
from settings import test_settings

es = Elasticsearch(
    [
        {
            "host": test_settings.es_host,
            "port": test_settings.es_port,
            "scheme": test_settings.es_schema
        }
    ]
)

while True:
    print('HERE')
    # print(test_settings.es_host)
    # response = es.cluster.health()
    # print(response)
    time.sleep(20)