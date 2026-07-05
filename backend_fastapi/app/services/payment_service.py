from uuid import uuid4

from app.models import Payment, PaymentMethod, PaymentStatus


def initiate_payment(order_id: int, method: str, amount: float) -> Payment:
    normalized = method.upper()
    if normalized not in {"COD", "UPI", "CARD"}:
        raise ValueError("Unsupported payment method")

    status = PaymentStatus.PAID if normalized == "COD" else PaymentStatus.INITIATED
    reference = f"pay_{uuid4().hex[:12]}"

    return Payment(
        order_id=order_id,
        method=PaymentMethod(normalized),
        status=status,
        amount=amount,
        gateway_reference=reference,
    )


def mark_payment_success(payment: Payment) -> Payment:
    payment.status = PaymentStatus.PAID
    return payment
