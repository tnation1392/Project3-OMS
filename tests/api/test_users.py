import pytest
from tests.factories.user_factory import make_user_data


@pytest.mark.smoke
def test_create_user(client):
    payload = make_user_data(email="test@test.com")

    response = client.post("/users/", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["email"] == payload["email"]
    assert "id" in data
