import pytest

from tests.factories.product_factory import make_product_data
from tests.factories.order_factory import make_order_item_data


@pytest.mark.workflow
@pytest.mark.regression
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


@pytest.mark.workflow
@pytest.mark.regression
def test_cannot_cancel_shipped_order(client, create_user_and_login, create_admin_and_login):
    user_auth = create_user_and_login("shippedcancel@test.com")
    admin_auth = create_admin_and_login("admincancel@test.com")

    product_payload = make_product_data(name="Dock", price=60.0, stock=4)
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
