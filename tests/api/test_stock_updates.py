import pytest
from app.models.product import Product

@pytest.mark.regression
@pytest.mark.db
def test_cancelling_order_restores_stock(client, db, create_user_and_login):
    auth_data = create_user_and_login("restock@test.com")
    headers = auth_data["headers"]

    product_response = client.post(
        "/products/",
        json={"name": "Monitor", "price": 200.0, "stock": 5}
    )
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]

    order_response = client.post("/orders/", json={}, headers=headers)
    assert order_response.status_code == 200
    order_id = order_response.json()["id"]

    add_item_response = client.post(
        f"/orders/{order_id}/items",
        json={"product_id": product_id, "quantity": 2},
        headers=headers
    )
    assert add_item_response.status_code == 200

    product_before_cancel = db.query(Product).filter(Product.id == product_id).first()
    assert product_before_cancel.stock == 3

    cancel_response = client.post(
        f"/orders/{order_id}/cancel",
        headers=headers
    )
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "CANCELLED"

    product_after_cancel = db.query(Product).filter(Product.id == product_id).first()
    assert product_after_cancel.stock == 5

@pytest.mark.regression
@pytest.mark.db
def test_add_item_fails_when_stock_is_insufficient(client, create_user_and_login):
    auth_data = create_user_and_login("nostock@test.com")
    headers = auth_data["headers"]

    product_response = client.post(
        "/products/",
        json={"name": "Mouse", "price": 25.0, "stock": 1}
    )
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]

    order_response = client.post("/orders/", json={}, headers=headers)
    assert order_response.status_code == 200
    order_id = order_response.json()["id"]

    response = client.post(
        f"/orders/{order_id}/items",
        json={"product_id": product_id, "quantity": 2},
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient stock"