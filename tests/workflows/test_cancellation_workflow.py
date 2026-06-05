import pytest

from tests.factories.product_factory import make_product_data
from tests.helpers.order_helpers import (
    create_order_for_authenticated_user,
    add_item_to_order_for_user,
    pay_order_for_user,
    cancel_order_for_user,
    ship_order_as_admin,
)
from tests.assertions.order_assertions import (
    assert_order_cancelled,
    assert_order_shipped,
)


@pytest.mark.workflow
@pytest.mark.regression
def test_user_can_cancel_created_order(client, create_user_and_login):
    auth_data = create_user_and_login("cancelcreated@test.com")
    headers = auth_data["headers"]

    order = create_order_for_authenticated_user(client, headers)
    cancelled_order = cancel_order_for_user(client, headers, order["id"])

    assert_order_cancelled(cancelled_order)


@pytest.mark.workflow
@pytest.mark.regression
def test_cannot_cancel_shipped_order(client, create_user_and_login, create_admin_and_login):
    user_auth = create_user_and_login("shippedcancel@test.com")
    admin_auth = create_admin_and_login("admincancel@test.com")

    product_payload = make_product_data(name="Dock", price=60.0, stock=4)
    product_response = client.post("/products/", json=product_payload)
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]

    order = create_order_for_authenticated_user(client, user_auth["headers"])

    add_item_to_order_for_user(
        client,
        user_auth["headers"],
        order["id"],
        product_id,
        quantity=1
    )

    pay_order_for_user(client, user_auth["headers"], order["id"])

    shipped_order = ship_order_as_admin(client, admin_auth["headers"], order["id"])
    assert_order_shipped(shipped_order)

    cancel_response = client.post(
        f"/orders/{order['id']}/cancel",
        headers=user_auth["headers"]
    )

    assert cancel_response.status_code == 400
    assert cancel_response.json()["detail"] == "Only CREATED or PAID orders can be cancelled"