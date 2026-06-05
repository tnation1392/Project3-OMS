import pytest

from tests.factories.product_factory import make_product_data
from tests.factories.order_factory import make_order_item_data


@pytest.mark.workflow
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


@pytest.mark.workflow
@pytest.mark.smoke
def test_user_can_create_order_add_item_and_pay(client, create_user_and_login):
    auth_data = create_user_and_login("workflowuser@test.com")
    headers = auth_data["headers"]

    product_payload = make_product_data(name="Headset", price=75.0, stock=5)
    product_response = client.post("/products/", json=product_payload)
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]

    order_response = client.post("/orders/", json={}, headers=headers)
    assert order_response.status_code == 200
    order_id = order_response.json()["id"]

    item_payload = make_order_item_data(product_id=product_id, quantity=2)
    add_item_response = client.post(
        f"/orders/{order_id}/items",
        json=item_payload,
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


@pytest.mark.workflow
@pytest.mark.regression
def test_admin_can_ship_paid_order(client, create_user_and_login, create_admin_and_login):
    user_auth = create_user_and_login("paiduser@test.com")
    admin_auth = create_admin_and_login("adminship@test.com")

    product_payload = make_product_data(name="Webcam", price=80.0, stock=3)
    product_response = client.post("/products/", json=product_payload)
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]

    order_response = client.post("/orders/", json={}, headers=user_auth["headers"])
    assert order_response.status_code == 200
    order_id = order_response.json()["id"]

    item_payload = make_order_item_data(product_id=product_id, quantity=1)
    add_item_response = client.post(
        f"/orders/{order_id}/items",
        json=item_payload,
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