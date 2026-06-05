import pytest
from tests.factories.product_factory import make_product_data


@pytest.fixture
def create_product(client):
    def _create_product(**overrides):
        payload = make_product_data(**overrides)
        response = client.post("/products/", json=payload)
        assert response.status_code == 200
        return response.json()

    return _create_product
