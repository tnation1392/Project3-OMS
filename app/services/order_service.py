from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.user import User
from app.services.notification_service import send_shipping_notification


def create_order_for_user(db: Session, user_id: int) -> Order:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    order = Order(user_id=user_id, status="CREATED", total_price=0.0)
    db.add(order)
    db.commit()
    db.refresh(order)

    return order


def get_order_by_id(db: Session, order_id: int) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


def get_order_for_user(db: Session, order_id: int, user_id: int) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized for this order")

    return order


def recalculate_order_total(order: Order) -> float:
    return sum(item.quantity * item.price_at_purchase for item in order.items)


def add_item_to_order(
    db: Session, order_id: int, product_id: int, quantity: int
) -> OrderItem:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != "CREATED":
        raise HTTPException(
            status_code=400, detail="Items can only be added to CREATED orders"
        )

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if quantity > product.stock:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    existing_item = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order.id, OrderItem.product_id == product.id)
        .first()
    )

    if existing_item:
        existing_item.quantity += quantity
        order_item = existing_item
    else:
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            price_at_purchase=product.price,
        )
        db.add(order_item)

    product.stock -= quantity

    db.flush()
    db.refresh(order)

    order.total_price = recalculate_order_total(order)

    db.commit()
    db.refresh(order_item)

    return order_item


def list_orders_for_user(
    db: Session,
    user_id: int,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Order]:
    query = db.query(Order).filter(Order.user_id == user_id)

    if status:
        query = query.filter(Order.status == status)

    return query.order_by(Order.id.desc()).offset(offset).limit(limit).all()


def pay_order(db: Session, order: Order) -> Order:
    if order.status != "CREATED":
        raise HTTPException(status_code=400, detail="Only CREATED orders can be paid")

    if not order.items:
        raise HTTPException(status_code=400, detail="Cannot pay for an empty order")

    order.status = "PAID"
    db.commit()
    db.refresh(order)

    return order


def ship_order(db: Session, order: Order) -> Order:
    if order.status != "PAID":
        raise HTTPException(status_code=400, detail="Only PAID orders can be shipped")

    order.status = "SHIPPED"
    db.commit()
    db.refresh(order)

    try:
        send_shipping_notification(order.id, order.user.email)
    except Exception:
        # Shipping is the primary business action
        # Notification failure shouldn't undo the shipped state
        pass

    return order


def cancel_order(db: Session, order: Order) -> Order:
    if order.status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Order is already cancelled")

    if order.status not in ["CREATED", "PAID"]:
        raise HTTPException(
            status_code=400, detail="Only CREATED or PAID orders can be cancelled"
        )

    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock += item.quantity

    order.status = "CANCELLED"
    db.commit()
    db.refresh(order)

    return order


def deliver_order(db, order):
    if order.status != "SHIPPED":
        raise HTTPException(
            status_code=400, detail="Only SHIPPED orders can be delivered"
        )

    order.status = "DELIVERED"
    db.commit()
    db.refresh(order)

    return order
