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
        f"/orders/{order_id}/items", json=item_payload, headers=other_auth["headers"]
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
        f"/orders/{order_id}/items", json=item_payload, headers=headers
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

    response = client.post(f"/orders/{order_id}/pay", headers=headers)

    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot pay for an empty order"


@pytest.mark.regression
def test_cannot_ship_order_that_is_not_paid(
    client, create_user_and_login, create_admin_and_login
):
    user_auth = create_user_and_login("regularuser@test.com")
    admin_auth = create_admin_and_login("admin@test.com")

    order_response = client.post("/orders/", json={}, headers=user_auth["headers"])
    assert order_response.status_code == 200
    order_id = order_response.json()["id"]

    response = client.post(f"/orders/{order_id}/ship", headers=admin_auth["headers"])

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PAID orders can be shipped"


@pytest.mark.regression
def test_user_cannot_cancel_another_users_order(client, create_user_and_login):
    owner_auth = create_user_and_login("ownercancel@test.com")


@pytest.mark.regression
def test_user_can_list_only_their_own_orders(client, create_user_and_login):
    user_one = create_user_and_login("orders1@test.com")
    user_two = create_user_and_login("orders2@test.com")

    response_one = client.post("/orders/", json={}, headers=user_one["headers"])
    assert response_one.status_code == 200

    response_two = client.post("/orders/", json={}, headers=user_two["headers"])
    assert response_two.status_code == 200

    my_orders_response = client.get("/orders/me", headers=user_one["headers"])
    assert my_orders_response.status_code == 200

    my_orders = my_orders_response.json()
    assert len(my_orders) == 1
    assert my_orders[0]["user_id"] == user_one["user"]["id"]


@pytest.mark.regression
def test_order_detail_includes_items(client, create_user_and_login):
    auth_data = create_user_and_login("detailuser@test.com")
    headers = auth_data["headers"]

    product_payload = make_product_data(name="DeskLamp", price=35.0, stock=4)
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
        headers=headers,
    )
    assert add_item_response.status_code == 200

    detail_response = client.get(f"/orders/{order_id}", headers=headers)
    assert detail_response.status_code == 200

    detail = detail_response.json()
    assert detail["id"] == order_id
    assert detail["status"] == "CREATED"
    assert detail["total_price"] == 70.0
    assert len(detail["items"]) == 1
    assert detail["items"][0]["product_id"] == product_id
    assert detail["items"][0]["quantity"] == 2


@pytest.mark.regression
def test_user_can_filter_orders_by_status(client, create_user_and_login):
    auth_data = create_user_and_login("filteruser@test.com")
    headers = auth_data["headers"]

    product_payload = make_product_data(name="MousePad", price=20.0, stock=5)
    product_response = client.post("/products/", json=product_payload)
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]

    # Order 1 stays CREATED
    created_order_response = client.post("/orders/", json={}, headers=headers)
    assert created_order_response.status_code == 200

    # Order 2 becomes PAID
    paid_order_response = client.post("/orders/", json={}, headers=headers)
    assert paid_order_response.status_code == 200
    paid_order_id = paid_order_response.json()["id"]

    item_payload = make_order_item_data(product_id=product_id, quantity=1)
    add_item_response = client.post(
        f"/orders/{paid_order_id}/items",
        json=item_payload,
        headers=headers,
    )
    assert add_item_response.status_code == 200

    pay_response = client.post(
        f"/orders/{paid_order_id}/pay",
        headers=headers,
    )
    assert pay_response.status_code == 200

    filtered_response = client.get("/orders/me?status=PAID", headers=headers)
    assert filtered_response.status_code == 200

    filtered_orders = filtered_response.json()
    assert len(filtered_orders) == 1
    assert filtered_orders[0]["status"] == "PAID"


@pytest.mark.regression
def test_delivered_order_can_still_be_retrieved(
    client, create_user_and_login, create_admin_and_login
):
    user_auth = create_user_and_login("delivereddetail@test.com")
    admin_auth = create_admin_and_login("delivereddetailadmin@test.com")

    product_payload = make_product_data(name="DeskShelf", price=55.0, stock=5)
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
        headers=user_auth["headers"],
    )
    assert add_item_response.status_code == 200

    pay_response = client.post(
        f"/orders/{order_id}/pay",
        headers=user_auth["headers"],
    )
    assert pay_response.status_code == 200

    ship_response = client.post(
        f"/orders/{order_id}/ship",
        headers=admin_auth["headers"],
    )
    assert ship_response.status_code == 200

    deliver_response = client.post(
        f"/orders/{order_id}/deliver",
        headers=admin_auth["headers"],
    )
    assert deliver_response.status_code == 200
    assert deliver_response.json()["status"] == "DELIVERED"

    detail_response = client.get(f"/orders/{order_id}", headers=user_auth["headers"])
    assert detail_response.status_code == 200

    detail = detail_response.json()
    assert detail["status"] == "DELIVERED"
    assert detail["id"] == order_id


@pytest.mark.regression
def test_order_detail_shows_single_line_item_after_duplicate_adds(
    client, create_user_and_login
):
    auth_data = create_user_and_login("detailmerge@test.com")
    headers = auth_data["headers"]

    product_payload = make_product_data(name="Webcam", price=80.0, stock=10)
    product_response = client.post("/products/", json=product_payload)
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]

    order_response = client.post("/orders/", json={}, headers=headers)
    assert order_response.status_code == 200
    order_id = order_response.json()["id"]

    first_item_payload = make_order_item_data(product_id=product_id, quantity=1)
    second_item_payload = make_order_item_data(product_id=product_id, quantity=2)

    first_add_response = client.post(
        f"/orders/{order_id}/items",
        json=first_item_payload,
        headers=headers,
    )
    assert first_add_response.status_code == 200

    second_add_response = client.post(
        f"/orders/{order_id}/items",
        json=second_item_payload,
        headers=headers,
    )
    assert second_add_response.status_code == 200

    detail_response = client.get(f"/orders/{order_id}", headers=headers)
    assert detail_response.status_code == 200

    detail = detail_response.json()
    assert len(detail["items"]) == 1
    assert detail["items"][0]["product_id"] == product_id
    assert detail["items"][0]["quantity"] == 3
    assert detail["total_price"] == 240.0


@pytest.mark.regression
def test_user_with_no_orders_gets_empty_order_history(client, create_user_and_login):
    auth_data = create_user_and_login("emptyhistory@test.com")
    response = client.get("/orders/me", headers=auth_data["headers"])

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.regression
def test_user_can_filter_orders_by_status(client, create_user_and_login):
    auth_data = create_user_and_login("filteruser@test.com")
    headers = auth_data["headers"]

    product_payload = make_product_data(name="MousePad", price=20.0, stock=5)
    product_response = client.post("/products/", json=product_payload)
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]

    # Order 1 stays CREATED
    created_order_response = client.post("/orders/", json={}, headers=headers)
    assert created_order_response.status_code == 200

    # Order 2 becomes PAID
    paid_order_response = client.post("/orders/", json={}, headers=headers)
    assert paid_order_response.status_code == 200
    paid_order_id = paid_order_response.json()["id"]

    item_payload = make_order_item_data(product_id=product_id, quantity=1)
    add_item_response = client.post(
        f"/orders/{paid_order_id}/items",
        json=item_payload,
        headers=headers,
    )
    assert add_item_response.status_code == 200

    pay_response = client.post(
        f"/orders/{paid_order_id}/pay",
        headers=headers,
    )
    assert pay_response.status_code == 200

    filtered_response = client.get("/orders/me?status=PAID", headers=headers)
    assert filtered_response.status_code == 200

    filtered_orders = filtered_response.json()
    assert len(filtered_orders) == 1
    assert filtered_orders[0]["status"] == "PAID"


@pytest.mark.regression
def test_order_history_supports_limit_and_offset(client, create_user_and_login):
    auth_data = create_user_and_login("paginationuser@test.com")
    headers = auth_data["headers"]

    for _ in range(3):
        response = client.post("/orders/", json={}, headers=headers)
        assert response.status_code == 200

    first_page_response = client.get("/orders/me?limit=2&offset=0", headers=headers)
    assert first_page_response.status_code == 200
    first_page = first_page_response.json()
    assert len(first_page) == 2

    second_page_response = client.get("/orders/me?limit=2&offset=2", headers=headers)
    assert second_page_response.status_code == 200
    second_page = second_page_response.json()
    assert len(second_page) == 1


@pytest.mark.regression
def test_user_cannot_retrieve_another_users_order_detail(client, create_user_and_login):
    owner_auth = create_user_and_login("detailowner@test.com")
    other_auth = create_user_and_login("detailother@test.com")

    order_response = client.post("/orders/", json={}, headers=owner_auth["headers"])
    assert order_response.status_code == 200
    order_id = order_response.json()["id"]

    detail_response = client.get(
        f"/orders/{order_id}",
        headers=other_auth["headers"],
    )

    assert detail_response.status_code == 403
    assert detail_response.json()["detail"] == "Not authorized for this order"


@pytest.mark.regression
def test_delivered_orders_still_appear_in_order_history(
    client, create_user_and_login, create_admin_and_login
):
    user_auth = create_user_and_login("historydelivered@test.com")
    admin_auth = create_admin_and_login("historydeliveredadmin@test.com")

    product_payload = make_product_data(name="DeskShelf", price=55.0, stock=5)
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
        headers=user_auth["headers"],
    )
    assert add_item_response.status_code == 200

    pay_response = client.post(
        f"/orders/{order_id}/pay",
        headers=user_auth["headers"],
    )
    assert pay_response.status_code == 200

    ship_response = client.post(
        f"/orders/{order_id}/ship",
        headers=admin_auth["headers"],
    )
    assert ship_response.status_code == 200

    deliver_response = client.post(
        f"/orders/{order_id}/deliver",
        headers=admin_auth["headers"],
    )
    assert deliver_response.status_code == 200
    assert deliver_response.json()["status"] == "DELIVERED"

    history_response = client.get(
        "/orders/me?status=DELIVERED", headers=user_auth["headers"]
    )
    assert history_response.status_code == 200

    history = history_response.json()
    assert len(history) == 1
    assert history[0]["id"] == order_id
    assert history[0]["status"] == "DELIVERED"
