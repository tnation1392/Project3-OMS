import pytest


@pytest.mark.smoke
def test_user_can_login_and_receive_token(client):
    create_response = client.post(
        "/users/",
        json={"email": "login@test.com", "password": "123456"}
    )
    assert create_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={"email": "login@test.com", "password": "123456"}
    )

    assert login_response.status_code == 200
    data = login_response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.regression
def test_login_fails_with_wrong_password(client):
    create_response = client.post(
        "/users/",
        json={"email": "wrongpw@test.com", "password": "123456"}
    )
    assert create_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={"email": "wrongpw@test.com", "password": "wrongpass"}
    )

    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Invalid credentials"