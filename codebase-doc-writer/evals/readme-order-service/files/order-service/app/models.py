from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

OrderStatus = Literal["pending", "confirmed", "shipped", "cancelled"]


class OrderItem(BaseModel):
    sku: str = Field(min_length=1, max_length=32)
    qty: int = Field(ge=1, le=99)
    unit_price: Decimal = Field(gt=0)


class OrderCreate(BaseModel):
    items: list[OrderItem] = Field(min_length=1)
    note: str | None = Field(default=None, max_length=500)


class OrderOut(BaseModel):
    id: int
    user_id: str
    status: OrderStatus
    items: list[OrderItem]
    total_amount: Decimal
    note: str | None
    created_at: datetime


class OrderPage(BaseModel):
    items: list[OrderOut]
    total: int
    limit: int
    offset: int
