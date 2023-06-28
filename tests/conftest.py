import json
from typing import List

import pytest
import asyncio

from elasticsearch import AsyncElasticsearch

from settings import test_settings


@pytest.fixture
def es_write_data():
    async def inner(data: List[dict]):
        hosts = f'{test_settings.es_schema}://{test_settings.es_host}:{test_settings.es_port}'
        bulk_query = []
        for row in data:
            bulk_query.extend([
                json.dumps({'index': {'_index': 'movies', '_id': row['id']}}),
                json.dumps(row)
            ])

        str_query = '\n'.join(bulk_query) + '\n'

        es_client = AsyncElasticsearch(hosts=hosts)
        response = await es_client.bulk(operations=str_query, refresh=True)
        await es_client.close()
        if response['errors']:
            print(response['errors'])
            raise Exception('Ошибка записи данных в Elasticsearch')

    return inner
