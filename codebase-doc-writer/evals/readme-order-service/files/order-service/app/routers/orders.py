from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import get_current_user
from app.config import settings
from app.models import OrderCreate, OrderOut, OrderPage
from app.services import orders as svc

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(body: OrderCreate, user_id: str = Depends(get_current_user)) -> OrderOut:
    if len(body.items) > settings.order_max_items:
        raise HTTPException(status_code=422, detail=f"Too many items (max {settings.order_max_items})")
    return svc.create_order(user_id, body)


@router.get("", response_model=OrderPage)
def list_orders(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user),
) -> OrderPage:
    return svc.list_orders(user_id, limit, offset)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, user_id: str = Depends(get_current_user)) -> OrderOut:
    order = svc.get_order(user_id, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(order_id: int, user_id: str = Depends(get_current_user)) -> OrderOut:
    order = svc.get_order(user_id, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "pending":
        raise HTTPException(status_code=409, detail=f"Order cannot be cancelled in status {order.status}")
    return svc.cancel_order(order)
