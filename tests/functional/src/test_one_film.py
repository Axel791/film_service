import pytest

from tests.functional.conftest import generate_film

CORRECT_FILM_UUID: str = '5b965eee-657e-4ea6-a06f-3351fdd174e0'
WRONG_FILM_UUID: str = '5b965eee-657e-4ea6-a06f-3351fdd174e1'


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                CORRECT_FILM_UUID,
                {'status': 200, 'film_id': CORRECT_FILM_UUID}
        ),
        (
                WRONG_FILM_UUID,
                {'status': 404, 'film_id': None}
        )
    ]
)
@pytest.mark.asyncio
async def test_one_film(es_write_data, make_get_request, query_data, expected_answer):
    # 1. Генерируем данные для ES
    es_data = [generate_film(film_id=CORRECT_FILM_UUID)]

    # 2. Загружаем данные в ES
    await es_write_data(es_data)

    # 3. Запрашиваем данные из ES по API
    response: dict = await make_get_request(
        url=f'/api/v1/films/get/{query_data}')

    # 4. Проверяем ответ
    assert response['status'] == expected_answer['status']
    assert response['body'].get('id') == expected_answer['film_id']
