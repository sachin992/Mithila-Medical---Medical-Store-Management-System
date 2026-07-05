from datetime import date, datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models import CartItem, Medicine, Order, OrderEvent, OrderItem, OrderStatus, Payment, PaymentStatus, User
from app.schemas.order import CartItemCreate, CheckoutRequest
from app.services.notification_service import notify_order_state_change
from app.services.payment_service import initiate_payment, mark_payment_success

router = APIRouter()
settings = get_settings()


def _build_order_response(order: Order) -> dict:
    payment_method = order.payments[-1].method.value if order.payments else "N/A"
    return {
        "id": order.id,
        "status": order.status.value,
        "total_price": order.total_price,
        "created_at": order.created_at,
        "delivery_date": order.delivery_date,
        "customer_name": order.customer_name,
        "phone": order.phone,
        "address": order.address,
        "city": order.city,
        "pincode": order.pincode,
        "items": [
            {
                "medicine_id": i.medicine_id,
                "medicine_name": i.medicine_name_snapshot,
                "unit_price": i.unit_price,
                "quantity": i.quantity,
                "line_total": i.line_total,
            }
            for i in order.items
        ],
        "timeline": [
            {"event_type": e.event_type, "note": e.note, "created_at": e.created_at}
            for e in sorted(order.events, key=lambda x: x.created_at)
        ],
        "payments": [
            {
                "method": p.method.value,
                "status": p.status.value,
                "amount": p.amount,
                "gateway_reference": p.gateway_reference,
            }
            for p in order.payments
        ],
        "invoice": {
            "invoice_id": f"INV-{order.id}-{order.created_at.strftime('%Y%m%d')}",
            "issued_at": datetime.utcnow(),
            "order_id": order.id,
            "customer_name": order.customer_name,
            "total_amount": order.total_price,
            "payment_method": payment_method,
        },
    }


@router.get("/cart")
def get_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = (
        db.query(CartItem, Medicine)
        .join(Medicine, Medicine.id == CartItem.medicine_id)
        .filter(CartItem.user_id == current_user.id)
        .all()
    )
    payload = []
    total = 0.0
    for cart_item, medicine in items:
        line_total = medicine.price * cart_item.quantity
        total += line_total
        payload.append(
            {
                "id": cart_item.id,
                "medicine_id": medicine.id,
                "medicine_name": medicine.medicine_name,
                "unit_price": medicine.price,
                "quantity": cart_item.quantity,
                "line_total": line_total,
            }
        )
    return {"items": payload, "total": total}


@router.post("/cart")
def add_to_cart(payload: CartItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    medicine = db.get(Medicine, payload.medicine_id)
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    if medicine.quantity < payload.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    existing = (
        db.query(CartItem)
        .filter(CartItem.user_id == current_user.id, CartItem.medicine_id == payload.medicine_id)
        .first()
    )
    if existing:
        existing.quantity += payload.quantity
    else:
        existing = CartItem(user_id=current_user.id, medicine_id=payload.medicine_id, quantity=payload.quantity)
        db.add(existing)
    db.commit()
    return {"message": "Added to cart"}


@router.delete("/cart/{cart_item_id}")
def remove_cart_item(cart_item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(CartItem).filter(CartItem.id == cart_item_id, CartItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(item)
    db.commit()
    return {"message": "Removed"}


@router.post("/checkout")
def checkout(payload: CheckoutRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart_rows = (
        db.query(CartItem, Medicine)
        .join(Medicine, Medicine.id == CartItem.medicine_id)
        .filter(CartItem.user_id == current_user.id)
        .all()
    )
    if not cart_rows:
        raise HTTPException(status_code=400, detail="Cart is empty")

    try:
        order = Order(
            user_id=current_user.id,
            customer_name=payload.customer_name,
            phone=payload.phone,
            address=payload.address,
            city=payload.city,
            pincode=payload.pincode,
            status=OrderStatus.PENDING,
            total_price=0,
        )
        db.add(order)
        db.flush()

        total_price = 0.0
        for cart_item, medicine in cart_rows:
            if medicine.quantity < cart_item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for {medicine.medicine_name}")
            medicine.quantity -= cart_item.quantity
            line_total = medicine.price * cart_item.quantity
            total_price += line_total

            db.add(
                OrderItem(
                    order_id=order.id,
                    medicine_id=medicine.id,
                    medicine_name_snapshot=medicine.medicine_name,
                    unit_price=medicine.price,
                    quantity=cart_item.quantity,
                    line_total=line_total,
                )
            )
            db.delete(cart_item)

        order.total_price = total_price

        payment = initiate_payment(order.id, payload.payment_method, total_price)
        db.add(payment)

        db.add(OrderEvent(order_id=order.id, event_type="ORDER_PLACED", note="Order created by customer"))
        if payment.status == PaymentStatus.PAID:
            db.add(OrderEvent(order_id=order.id, event_type="PAYMENT_CONFIRMED", note="Payment captured"))

        notify_order_state_change(db, order.id, payload.phone, current_user.email, "Pending")
        db.commit()
        db.refresh(order)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))

    order_full = (
        db.query(Order)
        .options(joinedload(Order.items), joinedload(Order.events), joinedload(Order.payments))
        .filter(Order.id == order.id)
        .first()
    )
    return _build_order_response(order_full)


@router.post("/{order_id}/payments/{payment_id}/confirm")
def confirm_online_payment(order_id: int, payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    payment = (
        db.query(Payment)
        .join(Order, Order.id == Payment.order_id)
        .filter(Payment.id == payment_id, Payment.order_id == order_id, Order.user_id == current_user.id)
        .first()
    )
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    mark_payment_success(payment)
    db.add(OrderEvent(order_id=order_id, event_type="PAYMENT_CONFIRMED", note="Online payment confirmed"))
    db.commit()
    return {"message": "Payment confirmed"}


@router.get("")
def list_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orders = (
        db.query(Order)
        .options(joinedload(Order.items), joinedload(Order.events), joinedload(Order.payments))
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return [_build_order_response(o) for o in orders]


@router.post("/{order_id}/cancel")
def cancel_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = (
        db.query(Order)
        .options(joinedload(Order.items), joinedload(Order.events))
        .filter(Order.id == order_id, Order.user_id == current_user.id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status in {OrderStatus.DELIVERED, OrderStatus.CANCELLED}:
        raise HTTPException(status_code=400, detail="Order can no longer be cancelled")

    deadline = order.created_at + timedelta(minutes=settings.cancellation_window_minutes)
    if datetime.utcnow() > deadline:
        raise HTTPException(status_code=400, detail="Cancellation window closed")

    order.status = OrderStatus.CANCELLED
    for item in order.items:
        medicine = db.get(Medicine, item.medicine_id)
        if medicine:
            medicine.quantity += item.quantity

    db.add(OrderEvent(order_id=order.id, event_type="ORDER_CANCELLED", note="Cancelled by customer"))
    notify_order_state_change(db, order.id, order.phone, current_user.email, "Cancelled")
    db.commit()
    return {"message": "Order cancelled"}
