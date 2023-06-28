import pytest

from tests.conftest import generate_film

ALL_FILMS_COUNT: int = 10


@pytest.mark.parametrize(
    'query_data, do_write_data, expected_answer',
    [
        (
                {'page_size': ALL_FILMS_COUNT},
                True,
                {'status': 200, 'length': ALL_FILMS_COUNT}
        ),
        (
                {'page_size': ALL_FILMS_COUNT},
                False,
                {'status': 200, 'length': ALL_FILMS_COUNT}
        ),
    ]
)
@pytest.mark.asyncio
async def test_film_cache(force_remove_index, make_get_request, es_write_data,
                          do_write_data, query_data, expected_answer):
    # 1. Генерируем данные для ES
    es_data = [generate_film() for _ in range(ALL_FILMS_COUNT)]

    # 2. Загружаем данные в ES
    if do_write_data:
        await es_write_data(es_data)

    # 3. Запрашиваем данные из ES по API
    response: dict = await make_get_request(
        url='/api/v1/films/list',
        query_data=query_data,
    )

    # 4. Удаляем данные из ES
    await force_remove_index()

    # 5. Проверяем ответ
    assert response['status'] == expected_answer['status']
    assert len(response['body']) == expected_answer['length']
