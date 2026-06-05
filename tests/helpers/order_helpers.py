def create_order_for_authenticated_user(client, headers):
    response = client.post("/orders/", json={}, headers=headers)
    assert response.status_code == 200
    return response.json()


def add_item_to_order_for_user(client, headers, order_id, product_id, quantity=1):
    response = client.post(
        f"/orders/{order_id}/items",
        json={"product_id": product_id, "quantity": quantity},
        headers=headers,
    )
    assert response.status_code == 200
    return response.json()


def pay_order_for_user(client, headers, order_id):
    response = client.post(f"/orders/{order_id}/pay", headers=headers)
    assert response.status_code == 200
    return response.json()


def cancel_order_for_user(client, headers, order_id):
    response = client.post(f"/orders/{order_id}/cancel", headers=headers)
    assert response.status_code == 200
    return response.json()


def ship_order_as_admin(client, headers, order_id):
    response = client.post(f"/orders/{order_id}/ship", headers=headers)
    assert response.status_code == 200
    return response.json()
