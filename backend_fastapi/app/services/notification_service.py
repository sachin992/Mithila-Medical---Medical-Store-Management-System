from sqlalchemy.orm import Session

from app.models import NotificationLog


def send_notification(db: Session, channel: str, recipient: str, message: str, order_id: int | None = None) -> None:
    # Provider integration point: Twilio/MSG91/SendGrid can be added here.
    log = NotificationLog(
        order_id=order_id,
        channel=channel,
        recipient=recipient,
        message=message,
        status="sent",
    )
    db.add(log)


def notify_order_state_change(db: Session, order_id: int, phone: str, email: str, status_text: str) -> None:
    send_notification(db, "sms", phone, f"Your order #{order_id} is now {status_text}", order_id=order_id)
    send_notification(db, "email", email, f"Order #{order_id} update: {status_text}", order_id=order_id)
