import json
from decimal import Decimal

import redis
from sqlalchemy import create_engine, text

from app.config import settings
from app.models import OrderCreate, OrderOut, OrderPage

engine = create_engine(settings.database_url, pool_pre_ping=True)
queue = redis.Redis.from_url(settings.redis_url)
QUEUE_NAME = "orders.created"


def create_order(user_id: str, body: OrderCreate) -> OrderOut:
    # TODO: add idempotency key — client retry hiện có thể tạo đơn trùng
    total = sum((i.unit_price * i.qty for i in body.items), Decimal("0"))
    with engine.begin() as conn:
        row = conn.execute(
            text(
                "INSERT INTO orders (user_id, status, items, total_amount, note) "
                "VALUES (:u, 'pending', :items, :total, :note) RETURNING id, created_at"
            ),
            {"u": user_id, "items": body.model_dump_json(include={"items"}), "total": total, "note": body.note},
        ).one()
    queue.lpush(QUEUE_NAME, json.dumps({"order_id": row.id, "user_id": user_id}))
    return OrderOut(id=row.id, user_id=user_id, status="pending", items=body.items,
                    total_amount=total, note=body.note, created_at=row.created_at)


def get_order(user_id: str, order_id: int) -> OrderOut | None:
    with engine.connect() as conn:
        row = conn.execute(text("SELECT * FROM orders WHERE id = :i AND user_id = :u"),
                           {"i": order_id, "u": user_id}).mappings().first()
    return None if row is None else OrderOut.model_validate({**row, "items": json.loads(row["items"])["items"]})


def list_orders(user_id: str, limit: int, offset: int) -> OrderPage:
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM orders WHERE user_id = :u ORDER BY created_at DESC LIMIT :l OFFSET :o"),
                            {"u": user_id, "l": limit, "o": offset}).mappings().all()
        total = conn.execute(text("SELECT count(*) FROM orders WHERE user_id = :u"), {"u": user_id}).scalar_one()
    items = [OrderOut.model_validate({**r, "items": json.loads(r["items"])["items"]}) for r in rows]
    return OrderPage(items=items, total=total, limit=limit, offset=offset)


def cancel_order(order: OrderOut) -> OrderOut:
    with engine.begin() as conn:
        conn.execute(text("UPDATE orders SET status = 'cancelled' WHERE id = :i"), {"i": order.id})
    return order.model_copy(update={"status": "cancelled"})
