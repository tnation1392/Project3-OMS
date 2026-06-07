from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    pass


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total_price: float

    class Config:
        from_attributes = True


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    price_at_purchase: float

    class Config:
        from_attributes = True


class OrderItemDetailResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_at_purchase: float

    class Config:
        from_attributes = True


class OrderDetailResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total_price: float
    items: list[OrderItemDetailResponse]

    class Config:
        from_attributes = True
