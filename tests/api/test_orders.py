import pytest


@pytest.mark.smoke
def test_authenticated_user_can_create_order(client, create_user_and_login):
    auth_data = create_user_and_login("orderowner@test.com")
    headers = auth_data["headers"]

    response = client.post("/orders/", json={}, headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["user_id"] == auth_data["user"]["id"]
    assert data["status"] == "CREATED"
    assert data["total_price"] == 0.0
    assert "id" in data


@pytest.mark.smoke
def test_user_can_create_order_add_item_and_pay(client, create_user_and_login):
    auth_data = create_user_and_login("workflowuser@test.com")
    headers = auth_data["headers"]

    product_response = client.post(
        "/products/",
        json={"name": "Headset", "price": 75.0, "stock": 5}
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

    pay_response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )
    assert pay_response.status_code == 200

    paid_order = pay_response.json()
    assert paid_order["status"] == "PAID"
    assert paid_order["total_price"] == 150.0


@pytest.mark.regression
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