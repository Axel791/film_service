import pytest

from tests.conftest import generate_film, generate_persons

CORRECT_PERSON_UUID: str = "5b925eee-894e-4ea6-a06f-3351faa174e1"
WRONG_PERSON_UUID: str = "5b965eee-657e-4ea6-a06f-3351fdd174e1"

CORRECT_FILM_UUID: str = "7c5ca482-2c9c-4f04-8bce-446db6686a3d"


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (CORRECT_PERSON_UUID, {"status": 200, "person_id": CORRECT_PERSON_UUID}),
        (WRONG_PERSON_UUID, {"status": 404, "person_id": WRONG_PERSON_UUID}),
    ],
)
@pytest.mark.asyncio
async def test_one_person(es_write_data, make_get_request, query_data, expected_answer):
    es_data = [generate_persons(person_id=CORRECT_PERSON_UUID)]
    await es_write_data(es_data)
    response: dict = await make_get_request(url=f"/api/v1/persons/get/{query_data}")

    assert response["status"] == expected_answer["status"]
    assert response["body"].get("id") == expected_answer["person_id"]


@pytest.mark.parametrize(
    "person_id, expected_status, expected_film_id",
    [(CORRECT_PERSON_UUID, 200, CORRECT_FILM_UUID), (WRONG_PERSON_UUID, 404, None)],
)
@pytest.mark.asyncio
async def test_get_persons_films_by_id(
    es_write_data, make_get_request, person_id, expected_status, expected_film_id
):
    film = generate_film(film_id=CORRECT_FILM_UUID)
    person = generate_persons(person_id=CORRECT_PERSON_UUID, film=film)
    await es_write_data([person])
    response: dict = await make_get_request(url=f"/api/v1/{person_id}/films")

    assert response["status"] == expected_status
    if expected_status == 200:
        assert response["body"][0].get("id") == expected_film_id
