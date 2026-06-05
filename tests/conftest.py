import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.deps import get_db
from app.db.base import Base
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def create_user_and_login(client):
    def _create_user_and_login(email: str, password: str = "123456"):
        create_response = client.post(
            "/users/",
            json={"email": email, "password": password}
        )
        assert create_response.status_code == 200

        login_response = client.post(
            "/auth/login",
            json={"email": email, "password": password}
        )
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        return {
            "user": create_response.json(),
            "token": token,
            "headers": {
                "Authorization": f"Bearer {token}"
            }
        }

    return _create_user_and_login

@pytest.fixture
def create_admin_and_login(client, db):
    from app.models.user import User
    from app.core.security import hash_password

    def _create_admin_and_login(email: str, password: str = "123456"):
        admin = User(
            email=email,
            password_hash=hash_password(password),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        login_response = client.post(
            "/auth/login",
            json={"email": email, "password": password}
        )
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        return {
            "user": {
                "id": admin.id,
                "email": admin.email,
                "role": admin.role
            },
            "token": token,
            "headers": {
                "Authorization": f"Bearer {token}"
            }
        }

    return _create_admin_and_login