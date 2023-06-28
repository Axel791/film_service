import json
import uuid

import pytest


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'query': 'The Star', 'page_size': 100},
                {'status': 200, 'length': 50}
        ),
        (
                {'query': ''},
                {'status': 200, 'length': 0}
        ),
        (
                {'query': 'Action', 'page_size': 10},
                {'status': 200, 'length': 10}
        ),
        (
                {'query': 'Sci-Fi', 'page_size': 20},
                {'status': 200, 'length': 20}
        ),
        (
                {'query': 'Non-existent', 'page_size': 100},
                {'status': 200, 'length': 0}
        )
    ]
)
@pytest.mark.asyncio
async def test_search_films(make_get_request, es_write_data, query_data: dict, expected_answer: dict):
    es_data = [
        {
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
            ]
        }
        for _ in range(50)
    ]
    await es_write_data(es_data, 'movies')
    url = 'http://movies_app_api/api/v1/films/search'
    data, status = await make_get_request(url, query_data)
    assert status == expected_answer['status']
    assert len(data) == expected_answer['length']
