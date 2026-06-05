def assert_order_created(order_data, expected_user_id):
    assert order_data["user_id"] == expected_user_id
    assert order_data["status"] == "CREATED"
    assert order_data["total_price"] == 0.0
    assert "id" in order_data


def assert_order_paid(order_data, expected_total):
    assert order_data["status"] == "PAID"
    assert order_data["total_price"] == expected_total


def assert_order_cancelled(order_data):
    assert order_data["status"] == "CANCELLED"


def assert_order_shipped(order_data):
    assert order_data["status"] == "SHIPPED"


def assert_order_item(item_data, expected_order_id, expected_product_id, expected_quantity, expected_price):
    assert item_data["order_id"] == expected_order_id
    assert item_data["product_id"] == expected_product_id
    assert item_data["quantity"] == expected_quantity
    assert item_data["price_at_purchase"] == expected_price
