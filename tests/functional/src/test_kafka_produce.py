import pytest


@pytest.mark.asyncio
async def test_kafka(make_post_request):
    response = await make_post_request(
        url="http://movies_app_kafka/app/api/v1/kafka/produce/",
        query_data={
            "topic": "page_view",
            "message": {
                "userId": "user124",
                "pageURL": "https://example.com/page1",
                "timestamp": 1678400000000,
            },
        },
    )
    assert response.status == 200
    assert response.body == "Message is sent"
