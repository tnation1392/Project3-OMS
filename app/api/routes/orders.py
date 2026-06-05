from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_admin
from app.models.user import User
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderItemCreate,
    OrderItemResponse,
)
from app.services.order_service import (
    create_order_for_user,
    get_order_for_user,
    get_order_by_id,
    add_item_to_order,
    pay_order,
    ship_order,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse)
def create_order(
    _: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_order_for_user(db, current_user.id)


@router.post("/{order_id}/items", response_model=OrderItemResponse)
def add_order_item(
    order_id: int,
    item: OrderItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = get_order_for_user(db, order_id, current_user.id)
    return add_item_to_order(db, order.id, item.product_id, item.quantity)


@router.post("/{order_id}/pay", response_model=OrderResponse)
def pay_for_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = get_order_for_user(db, order_id, current_user.id)
    return pay_order(db, order)


@router.post("/{order_id}/ship", response_model=OrderResponse)
def ship_existing_order(
    order_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    order = get_order_by_id(db, order_id)
    return ship_order(db, order)