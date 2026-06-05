import pytest


@pytest.fixture
def create_user_and_login(client):
    def _create_user_and_login(email: str, password: str = "123456"):
        create_response = client.post(
            "/users/", json={"email": email, "password": password}
        )
        assert create_response.status_code == 200

        login_response = client.post(
            "/auth/login", json={"email": email, "password": password}
        )
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        return {
            "user": create_response.json(),
            "token": token,
            "headers": {"Authorization": f"Bearer {token}"},
        }

    return _create_user_and_login


@pytest.fixture
def create_admin_and_login(client, db):
    from app.models.user import User
    from app.core.security import hash_password

    def _create_admin_and_login(email: str, password: str = "123456"):
        admin = User(email=email, password_hash=hash_password(password), role="admin")
        db.add(admin)
        db.commit()
        db.refresh(admin)

        login_response = client.post(
            "/auth/login", json={"email": email, "password": password}
        )
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        return {
            "user": {"id": admin.id, "email": admin.email, "role": admin.role},
            "token": token,
            "headers": {"Authorization": f"Bearer {token}"},
        }

    return _create_admin_and_login
