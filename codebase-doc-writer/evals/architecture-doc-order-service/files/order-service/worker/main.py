"""Worker: tiêu thụ queue Redis `orders.created`, xác nhận đơn và gửi email cho khách."""
import json
import logging
import os
import smtplib
import time
from email.message import EmailMessage

import redis
from sqlalchemy import create_engine, text

from app.config import settings

log = logging.getLogger("worker")
SMTP_HOST = os.environ["SMTP_HOST"]
MAX_RETRIES = 3


def send_confirmation(order_id: int, user_id: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = f"Đơn hàng #{order_id} đã được xác nhận"
    msg["From"] = "no-reply@example.com"
    msg["To"] = f"{user_id}@users.example.com"  # FIXME: lấy email thật từ user-service
    msg.set_content(f"Đơn hàng #{order_id} của bạn đã được xác nhận.")
    with smtplib.SMTP(SMTP_HOST) as s:
        s.send_message(msg)


def handle(payload: dict) -> None:
    engine = create_engine(settings.database_url)
    with engine.begin() as conn:
        conn.execute(text("UPDATE orders SET status = 'confirmed' WHERE id = :i AND status = 'pending'"),
                     {"i": payload["order_id"]})
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            send_confirmation(payload["order_id"], payload["user_id"])
            return
        except smtplib.SMTPException:
            log.warning("send mail failed, attempt %s", attempt)
            time.sleep(2 ** attempt)
    log.error("give up sending mail for order %s", payload["order_id"])


def main() -> None:
    r = redis.Redis.from_url(settings.redis_url)
    while True:
        _, raw = r.brpop("orders.created")
        handle(json.loads(raw))


if __name__ == "__main__":
    main()
