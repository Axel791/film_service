from random import randint

import pytest

from tests.conftest import generate_film

ALL_FILMS_COUNT: int = 25
DEFAULT_PAGE_SIZE: int = 5
GENRE: str = 'Comedy'


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'page_size': ALL_FILMS_COUNT},
                {'status': 200, 'length': ALL_FILMS_COUNT}
        ),
        (
                {'page_size': DEFAULT_PAGE_SIZE, 'genres': GENRE},
                {'status': 200, 'length': 1}
        ),
    ]
)
@pytest.mark.asyncio
async def test_search(make_get_request, es_write_data, query_data, expected_answer):
    # 1. Генерируем данные для ES
    es_data = [generate_film() for _ in range(ALL_FILMS_COUNT)]
    random_index = randint(0, ALL_FILMS_COUNT)
    es_data[random_index] = generate_film(film_genre=[GENRE], imdb_rating=9.9)

    # 2. Загружаем данные в ES
    await es_write_data(es_data)

    # 3. Запрашиваем данные из ES по API
    response: dict = await make_get_request(
        url='/api/v1/films/list',
        query_data=query_data,
    )

    # 4. Проверяем ответ
    assert response['status'] == expected_answer['status']
    assert len(response['body']) == expected_answer['length']
    assert response['body'][0]['imdb_rating'] == 9.9
    if 'genres' in query_data.keys():
        assert GENRE in response['body'][0]['genre']
