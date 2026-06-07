import pytest

from app.models.order import Order
from tests.factories.product_factory import make_product_data
from tests.helpers.order_helpers import (
    create_order_for_authenticated_user,
    add_item_to_order_for_user,
)


@pytest.mark.db
@pytest.mark.regression
def test_order_total_is_correct_after_merged_item_additions(
    client, db, create_user_and_login
):
    auth_data = create_user_and_login("ordertotal@test.com")
    headers = auth_data["headers"]

    product_payload = make_product_data(name="Speaker", price=75.0, stock=10)
    product_response = client.post("/products/", json=product_payload)
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]

    order = create_order_for_authenticated_user(client, headers)

    add_item_to_order_for_user(client, headers, order["id"], product_id, quantity=1)
    add_item_to_order_for_user(client, headers, order["id"], product_id, quantity=2)

    order_in_db = db.query(Order).filter(Order.id == order["id"]).first()
    assert order_in_db.total_price == 225.0
