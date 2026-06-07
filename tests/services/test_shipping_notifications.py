import pytest
from unittest.mock import patch
from tests.factories.product_factory import make_product_data
from tests.helpers.order_helpers import (
    create_order_for_authenticated_user,
    add_item_to_order_for_user,
    pay_order_for_user,
)


@pytest.mark.regression
def test_shipping_calls_notification_service(client, create_user_and_login, create_admin_and_login):
    user_auth = create_user_and_login("notifyuser@test.com")
    admin_auth = create_admin_and_login("notifyadmin@test.com")

    product_payload = make_product_data(name="Tripod", price=55.0, stock=5)
    product_response = client.post("/products/", json=product_payload)
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]

    order = create_order_for_authenticated_user(client, user_auth["headers"])

    add_item_to_order_for_user(
        client,
        user_auth["headers"],
        order["id"],
        product_id,
        quantity=1,
    )

    pay_order_for_user(client, user_auth["headers"], order["id"])

    with patch("app.services.order_service.send_shipping_notification") as mock_notify:
        ship_response = client.post(
            f"/orders/{order['id']}/ship",
            headers=admin_auth["headers"],
        )

    assert ship_response.status_code == 200
    assert ship_response.json()["status"] == "SHIPPED"

    mock_notify.assert_called_once_with(order["id"], user_auth["user"]["email"])


@pytest.mark.regression
def test_shipping_still_succeeds_if_notification_service_fails(client, create_user_and_login, create_admin_and_login):
    user_auth = create_user_and_login("notifyfailuser@test.com")
    admin_auth = create_admin_and_login("notifyfailadmin@test.com")

    product_payload = make_product_data(name="DockingStation", price=120.0, stock=5)
    product_response = client.post("/products/", json=product_payload)
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]

    order = create_order_for_authenticated_user(client, user_auth["headers"])

    add_item_to_order_for_user(
        client,
        user_auth["headers"],
        order["id"],
        product_id,
        quantity=1,
    )

    pay_order_for_user(client, user_auth["headers"], order["id"])

    with patch(
        "app.services.order_service.send_shipping_notification",
        side_effect=Exception("notification failure"),
    ):
        ship_response = client.post(
            f"/orders/{order['id']}/ship",
            headers=admin_auth["headers"],
        )

    assert ship_response.status_code == 200
    shipped_order = ship_response.json()
    assert shipped_order["status"] == "SHIPPED"

    detail_response = client.get(
        f"/orders/{order['id']}",
        headers=user_auth["headers"],
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["status"] == "SHIPPED"
