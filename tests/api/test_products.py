import pytest
from tests.factories.product_factory import make_product_data


@pytest.mark.smoke
def test_create_product(client):
    payload = make_product_data(name="Laptop", price=1200.99, stock=10)

    response = client.post("/products/", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == payload["name"]
    assert data["price"] == payload["price"]
    assert data["stock"] == payload["stock"]
    assert "id" in data


@pytest.mark.regression
@pytest.mark.parametrize(
    "payload",
    [
        {"name": "", "price": 10.0, "stock": 5},
        {"name": "Phone", "price": -1.0, "stock": 5},
        {"name": "Tablet", "price": 99.99, "stock": -3},
    ],
)
def test_create_product_invalid_input(client, payload):
    response = client.post("/products/", json=payload)

    assert response.status_code == 422


@pytest.mark.regression
def test_create_product_duplicate_name(client):
    payload = make_product_data(name="Monitor", price=250.00, stock=8)

    first_response = client.post("/products/", json=payload)
    second_response = client.post("/products/", json=payload)

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Product already exists"
