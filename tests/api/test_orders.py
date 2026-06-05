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

@pytest.mark.regression
def test_protected_order_endpoint_requires_token(client):
    response = client.post("/orders/", json={})

    assert response.status_code == 401

@pytest.mark.regression
def test_user_cannot_modify_another_users_order(client, create_user_and_login):
    owner_auth = create_user_and_login("owner@test.com")
    other_auth = create_user_and_login("other@test.com")

    product_response = client.post(
        "/products/",
        json={"name": "Speaker", "price": 90.0, "stock": 10}
    )
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]

    order_response = client.post("/orders/", json={}, headers=owner_auth["headers"])
    assert order_response.status_code == 200
    order_id = order_response.json()["id"]

    response = client.post(
        f"/orders/{order_id}/items",
        json={"product_id": product_id, "quantity": 1},
        headers=other_auth["headers"]
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized for this order"

@pytest.mark.regression
def test_cannot_pay_empty_order(client, create_user_and_login):
    auth_data = create_user_and_login("emptyorder@test.com")
    headers = auth_data["headers"]

    order_response = client.post("/orders/", json={}, headers=headers)
    assert order_response.status_code == 200
    order_id = order_response.json()["id"]

    response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot pay for an empty order"

@pytest.mark.regression
def test_cannot_ship_order_that_is_not_paid(client, create_user_and_login, create_admin_and_login):
    user_auth = create_user_and_login("regularuser@test.com")
    admin_auth = create_admin_and_login("admin@test.com")

    order_response = client.post("/orders/", json={}, headers=user_auth["headers"])
    assert order_response.status_code == 200
    order_id = order_response.json()["id"]

    response = client.post(f"/orders/{order_id}/ship",headers=admin_auth["headers"])

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PAID orders can be shipped"

@pytest.mark.regression
def test_admin_can_ship_paid_order(client, create_user_and_login, create_admin_and_login):
    user_auth = create_user_and_login("paiduser@test.com")
    admin_auth = create_admin_and_login("adminship@test.com")

    product_response = client.post(
        "/products/",
        json={"name": "Webcam", "price": 80.0, "stock": 3}
    )
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]

    order_response = client.post("/orders/", json={}, headers=user_auth["headers"])
    assert order_response.status_code == 200
    order_id = order_response.json()["id"]

    add_item_response = client.post(
        f"/orders/{order_id}/items",
        json={"product_id": product_id, "quantity": 1},
        headers=user_auth["headers"]
    )
    assert add_item_response.status_code == 200

    pay_response = client.post(
        f"/orders/{order_id}/pay",
        headers=user_auth["headers"]
    )
    assert pay_response.status_code == 200
    assert pay_response.json()["status"] == "PAID"

    ship_response = client.post(
        f"/orders/{order_id}/ship",
        headers=admin_auth["headers"]
    )

    assert ship_response.status_code == 200
    assert ship_response.json()["status"] == "SHIPPED"