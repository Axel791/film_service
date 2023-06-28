import asyncio
import json
import uuid
from datetime import datetime
from typing import List

import aiohttp

import pytest
import aiohttp
import asyncio
import pytest_asyncio

from elasticsearch import AsyncElasticsearch

from tests.settings import test_settings


def generate_film(film_id: str | None = None,
                  imdb_rating: float = 8.5,
                  film_genre: List[str] | None = None) -> dict:
    film = {
        'id': str(uuid.uuid4()) if film_id is None else film_id,
        'imdb_rating': imdb_rating,
        'genre': ['Action', 'Sci-Fi'] if film_genre is None else film_genre,
        'title': 'The Star',
        'description': 'New World',
        'director': ['Stan'],
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'actors': [
            {'id': '111', 'name': 'Ann'},
            {'id': '222', 'name': 'Bob'}
        ],
        'writers': [
            {'id': '333', 'name': 'Ben'},
            {'id': '444', 'name': 'Howard'}
        ],
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'film_work_type': 'movie'
    }
    return film


def get_es_bulk_query(es_data: List[dict], es_index: str, es_id_field: str) -> List[str]:
    bulk_query = []
    for row in es_data:
        bulk_query.extend([
            json.dumps({'index': {'_index': es_index, '_id': row[es_id_field]}}),
            json.dumps(row)
        ])
    return bulk_query


@pytest.fixture
def es_write_data():
    async def inner(data: List[dict], index: str):
        bulk_query = []
        for row in data:
            bulk_query.extend([
                json.dumps({'index': {'_index': index, '_id': row['id']}}),
                json.dumps(row)
            ])

        str_query = '\n'.join(bulk_query) + '\n'
        hosts = f'{test_settings.es_schema}://{test_settings.es_host}:{test_settings.es_port}'
        client = AsyncElasticsearch(hosts=hosts)
        response = await client.bulk(operations=str_query, refresh=True)
        await client.close()
        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')
            

@pytest_asyncio.fixture(scope='session')
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=test_settings.es_host,
                                validate_cert=False,
                                use_ssl=False)
    yield client
    await client.close()


@pytest_asyncio.fixture
def force_remove_index(es_client: AsyncElasticsearch):
    async def inner():
        is_index_exists = await es_client.indices.exists(test_settings.es_index)
        if is_index_exists:
            await es_client.indices.delete(index=test_settings.es_index)
    return inner


@pytest_asyncio.fixture(scope='module')
async def remove_index(es_client: AsyncElasticsearch):
    yield
    is_index_exists = await es_client.indices.exists(test_settings.es_index)
    if is_index_exists:
        await es_client.indices.delete(index=test_settings.es_index)


@pytest_asyncio.fixture
def es_write_data(es_client: AsyncElasticsearch, remove_index):
    async def inner(es_data: List[dict]):
        is_index_exists = await es_client.indices.exists(test_settings.es_index)
        if not is_index_exists:
            bulk_query = get_es_bulk_query(es_data,
                                           test_settings.es_index,
                                           test_settings.es_id_field)
            str_query = '\n'.join(bulk_query) + '\n'
            response = await es_client.bulk(str_query, refresh=True)
            if response['errors']:
                raise Exception('Ошибка записи данных в Elasticsearch')
    return inner


@pytest_asyncio.fixture(scope='session')
async def http_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture
def make_get_request(http_session: aiohttp.ClientSession):
    async def inner(url: str, query_data: dict | None = None) -> dict:
        full_url = test_settings.service_url + url
        async with http_session.get(full_url, params=query_data) as response:
            status = response.status
            body = {}
            if status in range(200, 400):
                body = await response.json()
        return {'body': body, 'status': status}
    return inner