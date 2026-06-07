import pytest

from tests.factories.product_factory import make_product_data
from tests.factories.order_factory import make_order_item_data
from tests.helpers.order_helpers import (
    pay_order_for_user,
    create_order_for_authenticated_user,
    add_item_to_order_for_user,
    ship_order_as_admin,
)


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
        f"/orders/{order_id}/items", json=item_payload, headers=headers
    )
    assert add_item_response.status_code == 200

    pay_response = client.post(f"/orders/{order_id}/pay", headers=headers)
    assert pay_response.status_code == 200

    paid_order = pay_response.json()
    assert paid_order["status"] == "PAID"
    assert paid_order["total_price"] == 150.0


@pytest.mark.workflow
@pytest.mark.regression
def test_admin_can_ship_paid_order(
    client, create_user_and_login, create_admin_and_login
):
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
        f"/orders/{order_id}/items", json=item_payload, headers=user_auth["headers"]
    )
    assert add_item_response.status_code == 200

    pay_response = client.post(f"/orders/{order_id}/pay", headers=user_auth["headers"])
    assert pay_response.status_code == 200
    assert pay_response.json()["status"] == "PAID"

    ship_response = client.post(
        f"/orders/{order_id}/ship", headers=admin_auth["headers"]
    )

    assert ship_response.status_code == 200
    assert ship_response.json()["status"] == "SHIPPED"


@pytest.mark.workflow
@pytest.mark.regression
def test_cannot_deliver_order_twice(
    client, create_user_and_login, create_admin_and_login
):
    user_auth = create_user_and_login("deliveronce@test.com")
    admin_auth = create_admin_and_login("deliveradmin@test.com")

    product_payload = make_product_data(name="LaptopStand", price=40.0, stock=5)
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
    ship_order_as_admin(client, admin_auth["headers"], order["id"])

    deliver_response = client.post(
        f"/orders/{order['id']}/deliver",
        headers=admin_auth["headers"],
    )
    assert deliver_response.status_code == 200
    assert deliver_response.json()["status"] == "DELIVERED"

    second_deliver_response = client.post(
        f"/orders/{order['id']}/deliver",
        headers=admin_auth["headers"],
    )

    assert second_deliver_response.status_code == 400
    assert (
        second_deliver_response.json()["detail"]
        == "Only SHIPPED orders can be delivered"
    )


@pytest.mark.workflow
@pytest.mark.regression
def test_cannot_cancel_delivered_order(
    client, create_user_and_login, create_admin_and_login
):
    user_auth = create_user_and_login("deliveredcancel@test.com")
    admin_auth = create_admin_and_login("deliveredcanceladmin@test.com")

    product_payload = make_product_data(name="MonitorArm", price=90.0, stock=5)
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
    ship_order_as_admin(client, admin_auth["headers"], order["id"])

    deliver_response = client.post(
        f"/orders/{order['id']}/deliver",
        headers=admin_auth["headers"],
    )
    assert deliver_response.status_code == 200
    assert deliver_response.json()["status"] == "DELIVERED"

    cancel_response = client.post(
        f"/orders/{order['id']}/cancel",
        headers=user_auth["headers"],
    )

    assert cancel_response.status_code == 400
    assert (
        cancel_response.json()["detail"]
        == "Only CREATED or PAID orders can be cancelled"
    )


@pytest.mark.workflow
@pytest.mark.regression
def test_cannot_add_items_to_delivered_order(
    client, create_user_and_login, create_admin_and_login
):
    user_auth = create_user_and_login("delivereditems@test.com")
    admin_auth = create_admin_and_login("delivereditemsadmin@test.com")

    product_payload = make_product_data(name="USBHub", price=25.0, stock=5)
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
    ship_order_as_admin(client, admin_auth["headers"], order["id"])

    deliver_response = client.post(
        f"/orders/{order['id']}/deliver",
        headers=admin_auth["headers"],
    )
    assert deliver_response.status_code == 200
    assert deliver_response.json()["status"] == "DELIVERED"

    item_payload = make_order_item_data(product_id=product_id, quantity=1)
    add_after_delivery_response = client.post(
        f"/orders/{order['id']}/items",
        json=item_payload,
        headers=user_auth["headers"],
    )

    assert add_after_delivery_response.status_code == 400
    assert (
        add_after_delivery_response.json()["detail"]
        == "Items can only be added to CREATED orders"
    )


@pytest.mark.workflow
@pytest.mark.regression
def test_cannot_pay_delivered_order(
    client, create_user_and_login, create_admin_and_login
):
    user_auth = create_user_and_login("deliveredpay@test.com")
    admin_auth = create_admin_and_login("deliveredpayadmin@test.com")

    product_payload = make_product_data(name="WebcamMount", price=45.0, stock=5)
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
    ship_order_as_admin(client, admin_auth["headers"], order["id"])

    deliver_response = client.post(
        f"/orders/{order['id']}/deliver",
        headers=admin_auth["headers"],
    )
    assert deliver_response.status_code == 200
    assert deliver_response.json()["status"] == "DELIVERED"

    pay_again_response = client.post(
        f"/orders/{order['id']}/pay",
        headers=user_auth["headers"],
    )

    assert pay_again_response.status_code == 400
    assert pay_again_response.json()["detail"] == "Only CREATED orders can be paid"


@pytest.mark.workflow
@pytest.mark.regression
def test_adding_same_product_twice_merges_quantity_and_updates_total(
    client, create_user_and_login
):
    auth_data = create_user_and_login("mergeitems@test.com")
    headers = auth_data["headers"]

    product_payload = make_product_data(name="Keyboard", price=50.0, stock=10)
    product_response = client.post("/products/", json=product_payload)
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]

    order = create_order_for_authenticated_user(client, headers)

    first_add = add_item_to_order_for_user(
        client,
        headers,
        order["id"],
        product_id,
        quantity=2,
    )

    second_add = add_item_to_order_for_user(
        client,
        headers,
        order["id"],
        product_id,
        quantity=1,
    )

    assert first_add["product_id"] == product_id
    assert second_add["product_id"] == product_id
    assert second_add["quantity"] == 3
    assert second_add["price_at_purchase"] == 50.0

    order_detail_response = client.get(f"/orders/{order['id']}", headers=headers)
    assert order_detail_response.status_code == 200
    order_detail = order_detail_response.json()

    assert order_detail["total_price"] == 150.0
    assert len(order_detail["items"]) == 1
    assert order_detail["items"][0]["quantity"] == 3
