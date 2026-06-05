import pytest

from app.models.product import Product
from tests.factories.product_factory import make_product_data
from tests.helpers.order_helpers import (
    create_order_for_authenticated_user,
    add_item_to_order_for_user,
    cancel_order_for_user,
)
from tests.assertions.order_assertions import assert_order_cancelled


@pytest.mark.db
@pytest.mark.regression
def test_cancelling_order_restores_stock(client, db, create_user_and_login):
    auth_data = create_user_and_login("restock@test.com")
    headers = auth_data["headers"]

    product_payload = make_product_data(name="Monitor", price=200.0, stock=5)
    product_response = client.post("/products/", json=product_payload)
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]

    order = create_order_for_authenticated_user(client, headers)

    add_item_to_order_for_user(client, headers, order["id"], product_id, quantity=2)

    product_before_cancel = db.query(Product).filter(Product.id == product_id).first()
    assert product_before_cancel.stock == 3

    cancelled_order = cancel_order_for_user(client, headers, order["id"])
    assert_order_cancelled(cancelled_order)

    product_after_cancel = db.query(Product).filter(Product.id == product_id).first()
    assert product_after_cancel.stock == 5
