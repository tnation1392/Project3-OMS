import pytest
from tests.factories.product_factory import make_product_data
from app.models.product import Product
from tests.factories.order_factory import make_order_item_data


@pytest.mark.db
@pytest.mark.regression
def test_cancelling_order_restores_stock(client, db, create_user_and_login):
    auth_data = create_user_and_login("restock@test.com")
    headers = auth_data["headers"]

    product_payload = make_product_data(name="Monitor", price=200.0, stock=5)
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

    product_before_cancel = db.query(Product).filter(Product.id == product_id).first()
    assert product_before_cancel.stock == 3

    cancel_response = client.post(
        f"/orders/{order_id}/cancel",
        headers=headers
    )
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "CANCELLED"

    product_after_cancel = db.query(Product).filter(Product.id == product_id).first()
    assert product_after_cancel.stock == 5
