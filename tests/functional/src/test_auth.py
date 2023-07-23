import pytest

@pytest.mark.asyncio
async def test_login(make_post_request):
    response = await make_post_request(url="auth/api/v1/login", query_data={"username": "testuser", "password": "testpass"})
    assert response.status == 200
    assert response.body == {"access_token": "dummy_access_token", "token_type": "bearer"}


@pytest.mark.asyncio
async def test_registration(make_post_request):
    user_data = {"login": "testuser", "email": "test@example.com", "password": "testpass"}
    response = await make_post_request("auth/api/v1/registration", query_data=user_data)
    assert response.status == 200
    assert response.body == user_data


@pytest.mark.asyncio
async def test_refresh(make_post_request):
    response = await make_post_request("/refresh", data={"access_token": "dummy_access_token"})
    assert response.status == 200
    assert response.body == {"access_token": "new_dummy_access_token", "token_type": "bearer"}
