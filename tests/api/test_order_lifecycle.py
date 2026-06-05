import pytest
from app.models.product import Product

@pytest.mark.regression
@pytest.mark.workflow
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

@pytest.mark.smoke
@pytest.mark.workflow
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
@pytest.mark.workflow
def test_user_can_cancel_created_order(client, create_user_and_login):
    auth_data = create_user_and_login("cancelcreated@test.com")
    headers = auth_data["headers"]

    order_response = client.post("/orders/", json={}, headers=headers)
    assert order_response.status_code == 200
    order_id = order_response.json()["id"]

    cancel_response = client.post(
        f"/orders/{order_id}/cancel",
        headers=headers
    )

    assert cancel_response.status_code == 200
    data = cancel_response.json()
    assert data["status"] == "CANCELLED"


@pytest.mark.regression
@pytest.mark.workflow
def test_cannot_cancel_shipped_order(client, create_user_and_login, create_admin_and_login):
    user_auth = create_user_and_login("shippedcancel@test.com")
    admin_auth = create_admin_and_login("admincancel@test.com")

    product_response = client.post(
        "/products/",
        json={"name": "Dock", "price": 60.0, "stock": 4}
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

    ship_response = client.post(
        f"/orders/{order_id}/ship",
        headers=admin_auth["headers"]
    )
    assert ship_response.status_code == 200
    assert ship_response.json()["status"] == "SHIPPED"

    cancel_response = client.post(
        f"/orders/{order_id}/cancel",
        headers=user_auth["headers"]
    )

    assert cancel_response.status_code == 400
    assert cancel_response.json()["detail"] == "Only CREATED or PAID orders can be cancelled"

@pytest.mark.regression
@pytest.mark.workflow
def test_cannot_pay_cancelled_order(client, create_user_and_login):
    auth_data = create_user_and_login("cancelpay@test.com")
    headers = auth_data["headers"]

    product_response = client.post(
        "/products/",
        json={"name": "Charger", "price": 30.0, "stock": 5}
    )
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]

    order_response = client.post("/orders/", json={}, headers=headers)
    assert order_response.status_code == 200
    order_id = order_response.json()["id"]

    add_item_response = client.post(
        f"/orders/{order_id}/items",
        json={"product_id": product_id, "quantity": 1},
        headers=headers
    )
    assert add_item_response.status_code == 200

    cancel_response = client.post(
        f"/orders/{order_id}/cancel",
        headers=headers
    )
    assert cancel_response.status_code == 200

    pay_response = client.post(
        f"/orders/{order_id}/pay",
        headers=headers
    )

    assert pay_response.status_code == 400
    assert pay_response.json()["detail"] == "Only CREATED orders can be paid"
