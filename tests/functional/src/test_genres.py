import pytest

from tests.conftest import generate_genres

CORRECT_GENRE_UUID: str = "5b965eee-311e-4ea6-a06f-3351asd174e0"
WRONG_GENRE_UUID: str = "5b965eee-657e-4ea6-a06f-3351fdd1327631"


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (CORRECT_GENRE_UUID, {"status": 200, "genre_id": CORRECT_GENRE_UUID}),
        (WRONG_GENRE_UUID, {"status": 404, "genre_id": None}),
    ],
)
@pytest.mark.asyncio
async def test_genre(es_write_data, make_get_request, query_data, expected_answer):
    es_data = [generate_genres(genre_id=CORRECT_GENRE_UUID)]
    await es_write_data(es_data)
    response: dict = await make_get_request(url=f"/api/v1/genres/get/{query_data}")

    assert response["status"] == expected_answer["status"]
    assert response["body"].get("id") == expected_answer["genre_id"]
