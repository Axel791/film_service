import uuid

import pytest


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'query': 'Mat Lucas'},
            {'status': 200, 'length': 50}
        ),
        (
            {'query': 'Star Wars: Clone Wars'},
            {'status': 200, 'length': 1}
        ),
        (
            {'query': 'Star Wars'},
            {'status': 200, 'length': 2}
        ),
        (
            {'query': 'Non-existent'},
            {'status': 200, 'length': 0}
        )
    ]
)
@pytest.mark.asyncio
async def test_search_persons(make_get_request, es_write_data, query_data: dict, expected_answer: dict):
    es_data = [
        {
            "id": str(uuid.uuid4()),
            "full_name": "Mat Lucas",
            "films": [
                {
                    "id": "fdfc8266-5ece-4d85-b614-3cfe9be97b71",
                    "title": "Star Wars: Clone Wars",
                    "roles": "actor"
                },
                {
                    "id": "044beafe-fe25-4edc-95f4-adbb8979c35b",
                    "title": "Star Wars: The Clone Wars",
                    "roles": "actor"
                }
            ]
        }
        for _ in range(50)
    ]
    await es_write_data(es_data, 'persons')
    url = 'http://movies_app_api/api/v1/persons/search'
    data, status = await make_get_request(url, query_data)
    assert status == expected_answer['status']
    assert len(data) == expected_answer['length']
