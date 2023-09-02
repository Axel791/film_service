import pytest

from tests.conftest import generate_film


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        ({"query": "The Star"}, {"status": 200, "length": 5}),
        ({"query": "Mashed potato"}, {"status": 200, "length": 0}),
    ],
)
@pytest.mark.asyncio
async def test_search(make_get_request, es_write_data, query_data, expected_answer):
    # 1. Генерируем данные для ES
    es_data = [generate_film() for _ in range(10)]

    # 2. Загружаем данные в ES
    await es_write_data(es_data)

    # 3. Запрашиваем данные из ES по API
    response: dict = await make_get_request(
        url="/api/v1/films/search",
        query_data=query_data,
    )

    # 4. Проверяем ответ
    assert response["status"] == expected_answer["status"]
    assert len(response["body"]) == expected_answer["length"]
