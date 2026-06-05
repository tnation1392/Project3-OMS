import pytest

@pytest.mark.smoke
def test_create_user(client):
    response = client.post(
        "/users/",
        json={"email": "test@test.com", "password": "123456"}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["email"] == "test@test.com"
    assert "id" in data
