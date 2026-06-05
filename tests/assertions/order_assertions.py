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