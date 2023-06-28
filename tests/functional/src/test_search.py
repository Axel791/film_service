import datetime
import uuid
import json

import aiohttp
import pytest

from elasticsearch import AsyncElasticsearch

from tests.functional.settings import test_settings


#  Название теста должно начинаться со слова `test_`
#  Любой тест с асинхронными вызовами нужно оборачивать декоратором `pytest.mark.asyncio`, который следит за запуском и работой цикла событий.

@pytest.mark.asyncio
async def test_search():
    # 1. Генерируем данные для ES

    es_data = [{
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genre': ['Action', 'Sci-Fi'],
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
        'created_at': datetime.datetime.now().isoformat(),
        'updated_at': datetime.datetime.now().isoformat(),
        'film_work_type': 'movie'
    } for _ in range(60)]

    bulk_query = []
    for row in es_data:
        bulk_query.extend([
            json.dumps({'index': {'_index': 'movies', '_id': row['id']}}),
            json.dumps(row)
        ])

    str_query = '\n'.join(bulk_query) + '\n'


    es_client = AsyncElasticsearch(hosts=test_settings.es_host,
                                   validate_cert=False,
                                   use_ssl=False)
    response = await es_client.bulk(str_query, refresh=True)
    await es_client.close()
    if response['errors']:
        raise Exception('Ошибка записи данных в Elasticsearch')


    session = aiohttp.ClientSession()
    url = test_settings.service_url + '/api/v1/search'
    query_data = {'search': 'The Star'}
    async with session.get(url, params=query_data) as response:
        body = await response.json()
        headers = response.headers
        status = response.status
    await session.close()


    assert status == 200
    assert len(response.body) == 50


# import pytest
# from elasticsearch import NotFoundError
# from your_module import YourClass, Person, NotFoundPerson
#
# @pytest.fixture
# def mock_elasticsearch(mocker):
#     es_mock = mocker.MagicMock()
#     es_mock.search.return_value = {
#         'hits': {
#             'hits': [
#                 {'_source': {'id': '1', 'full_name': 'John Doe', 'films': [{'title': 'Film 1'}, {'title': 'Film 2'}]}},
#                 {'_source': {'id': '2', 'full_name': 'Jane Smith', 'films': [{'title': 'Film 3'}, {'title': 'Film 4'}]}}
#             ]
#         }
#     }
#     return es_mock
#
# @pytest.fixture
# def your_class_instance(mock_elasticsearch):
#     return YourClass(es=mock_elasticsearch)
#
# @pytest.mark.asyncio
# async def test_search_persons_found(your_class_instance, mocker):
#     query = 'John'
#     page = 1
#     page_size = 10
#
#     persons = await your_class_instance._search_persons(query, page, page_size)
#
#     assert len(persons) == 2
#     assert isinstance(persons[0], Person)
#     assert isinstance(persons[1], Person)
#     assert persons[0].id == '1'
#     assert persons[0].full_name == 'John Doe'
#     assert persons[0].films == [{'title': 'Film 1'}, {'title': 'Film 2'}]
#     assert persons[1].id == '2'
#     assert persons[1].full_name == 'Jane Smith'
#     assert persons[1].films == [{'title': 'Film 3'}, {'title': 'Film 4'}]
#     your_class_instance._es.search.assert_called_once_with(index='persons', body={
#         'query': {'bool': {'must': [{'match': {'full_name': query}}]}},
#         'from': 0,
#         'size': page_size
#     })
#     your_class_instance._put_data_to_cache.assert_called_once()
#
# @pytest.mark.asyncio
# async def test_search_persons_not_found(your_class_instance, mocker):
#     query = 'Invalid'
#     page = 1
#     page_size = 10
#
#     your_class_instance._es.search.side_effect = NotFoundError()
#
#     with pytest.raises(NotFoundPerson):
#         await your_class_instance._search_persons(query, page, page_size)
#
#     your_class_instance._es.search.assert_called_once_with(index='persons', body={
#         'query': {'bool': {'must': [{'match': {'full_name': query}}]}},
#         'from': 0,
#         'size': page_size
#     })
