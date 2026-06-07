from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_admin
from app.models.user import User
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderItemCreate,
    OrderItemResponse,
    OrderDetailResponse,
)

from app.services.order_service import (
    create_order_for_user,
    get_order_for_user,
    get_order_by_id,
    add_item_to_order,
    pay_order,
    ship_order,
    cancel_order,
    list_orders_for_user,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse)
def create_order(
    _: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_order_for_user(db, current_user.id)


@router.post("/{order_id}/items", response_model=OrderItemResponse)
def add_order_item(
    order_id: int,
    item: OrderItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = get_order_for_user(db, order_id, current_user.id)
    return add_item_to_order(db, order.id, item.product_id, item.quantity)


@router.post("/{order_id}/pay", response_model=OrderResponse)
def pay_for_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = get_order_for_user(db, order_id, current_user.id)
    return pay_order(db, order)


@router.post("/{order_id}/ship", response_model=OrderResponse)
def ship_existing_order(
    order_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)
):
    order = get_order_by_id(db, order_id)
    return ship_order(db, order)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_existing_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = get_order_for_user(db, order_id, current_user.id)
    return cancel_order(db, order)


@router.get("/me", response_model=list[OrderResponse])
def list_my_orders(
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_orders_for_user(
        db=db,
        user_id=current_user.id,
        status=status,
        limit=limit,
        offset=offset,
    )


@router.get("/{order_id}", response_model=OrderDetailResponse)
def get_my_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_order_for_user(db, order_id, current_user.id)



def deliver_order(db, order):
    if order.status != "SHIPPED":
        raise HTTPException(
            status_code=400,
            detail="Only SHIPPED orders can be delivered"
        )

    order.status = "DELIVERED"
    db.commit()
    db.refresh(order)

    return order

@router.post("/{order_id}/deliver", response_model=OrderResponse)
def deliver_existing_order(
    order_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    order = get_order_by_id(db, order_id)
    return deliver_order(db, order)
