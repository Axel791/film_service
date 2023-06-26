import json
from typing import List

import pytest
import aiohttp

from elasticsearch import AsyncElasticsearch

from settings import test_settings


@pytest.fixture(scope='session')
async def es_client():
    hosts = f'{test_settings.es_schema}://{test_settings.es_host}:{test_settings.es_port}'
    client = AsyncElasticsearch(hosts=hosts)
    yield client
    await client.close()


@pytest.fixture
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(data: List[dict], index: str):
        bulk_query = []
        for row in data:
            bulk_query.extend([
                json.dumps({'index': {'_index': index, '_id': row['id']}}),
                json.dumps(row)
            ])

        str_query = '\n'.join(bulk_query) + '\n'

        response = await es_client.bulk(operations=str_query, refresh=True)
        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')

    return inner


@pytest.fixture
async def make_get_request():
    async def inner(url: str, params: dict):
        session = aiohttp.ClientSession()

        try:
            async with session.get(url, params=params) as response:
                data = await response.json()
                status = response.status
        finally:
            await session.close()

        return data, status

    return inner
