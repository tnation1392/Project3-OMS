import pytest
from tests.factories.product_factory import make_product_data
from tests.factories.order_factory import make_order_item_data


@pytest.mark.regression
def test_protected_order_endpoint_requires_token(client):
    response = client.post("/orders/", json={})

    assert response.status_code == 401


@pytest.mark.regression
def test_user_cannot_modify_another_users_order(client, create_user_and_login):
    owner_auth = create_user_and_login("owner@test.com")
    other_auth = create_user_and_login("other@test.com")

    product_payload = make_product_data(name="Speaker", price=90.0, stock=10)
    product_response = client.post("/products/", json=product_payload)
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]

    order_response = client.post("/orders/", json={}, headers=owner_auth["headers"])
    assert order_response.status_code == 200
    order_id = order_response.json()["id"]

    item_payload = make_order_item_data(product_id=product_id, quantity=1)
    response = client.post(
        f"/orders/{order_id}/items",
        json=item_payload,
        headers=other_auth["headers"]
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized for this order"


@pytest.mark.regression
def test_add_item_fails_when_stock_is_insufficient(client, create_user_and_login):
    auth_data = create_user_and_login("nostock@test.com")
    headers = auth_data["headers"]

    product_payload = make_product_data(name="Mouse", price=25.0, stock=1)
    product_response = client.post("/products/", json=product_payload)
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]

    order_response = client.post("/orders/", json={}, headers=headers)
    assert order_response.status_code == 200
    order_id = order_response.json()["id"]

    item_payload = make_order_item_data(product_id=product_id, quantity=2)
    response = client.post(
        f"/orders/{order_id}/items",
        json=item_payload,
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient stock"


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

    response = client.post(
        f"/orders/{order_id}/ship",
        headers=admin_auth["headers"]
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PAID orders can be shipped"


@pytest.mark.regression
def test_user_cannot_cancel_another_users_order(client, create_user_and_login):
    owner_auth = create_user_and_login("ownercancel@test.com")


