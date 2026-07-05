import csv
import io
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.config import get_settings
from app.db.session import get_db
from app.models import Medicine, Order, OrderEvent, OrderStatus, User
from app.schemas.medicine import MedicineCreate, MedicineUpdate
from app.services.notification_service import notify_order_state_change

router = APIRouter()
settings = get_settings()


@router.post("/medicines")
def create_medicine(payload: MedicineCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    medicine = Medicine(**payload.model_dump())
    db.add(medicine)
    db.commit()
    db.refresh(medicine)
    return medicine


@router.patch("/medicines/{medicine_id}")
def update_medicine(
    medicine_id: int,
    payload: MedicineUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    medicine = db.get(Medicine, medicine_id)
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(medicine, key, value)

    db.commit()
    db.refresh(medicine)
    return medicine


@router.post("/medicines/bulk-import")
def bulk_import_medicines(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload a CSV file")

    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    created = 0
    updated = 0

    for row in reader:
        name = (row.get("medicine_name") or "").strip()
        if not name:
            continue
        existing = db.query(Medicine).filter(Medicine.medicine_name == name).first()
        if existing:
            existing.quantity = int(row.get("quantity") or existing.quantity)
            existing.price = float(row.get("price") or existing.price)
            existing.category = row.get("category") or existing.category
            existing.manufacturer = row.get("manufacturer") or existing.manufacturer
            updated += 1
        else:
            db.add(
                Medicine(
                    medicine_name=name,
                    quantity=int(row.get("quantity") or 0),
                    price=float(row.get("price") or 0),
                    description=row.get("description"),
                    category=row.get("category"),
                    manufacturer=row.get("manufacturer"),
                )
            )
            created += 1

    db.commit()
    return {"created": created, "updated": updated}


@router.get("/inventory/reorder-suggestions")
def reorder_suggestions(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    rows = (
        db.query(Medicine)
        .filter(Medicine.quantity < 10)
        .order_by(Medicine.quantity.asc())
        .all()
    )
    return [
        {
            "medicine_id": med.id,
            "medicine_name": med.medicine_name,
            "current_quantity": med.quantity,
            "suggested_reorder": max(20 - med.quantity, 10),
        }
        for med in rows
    ]


@router.patch("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    staff: User = Depends(require_admin),
):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        new_status = OrderStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")

    order.status = new_status
    db.add(OrderEvent(order_id=order.id, event_type="STATUS_CHANGED", note=f"Updated to {status} by {staff.full_name}"))

    customer = db.get(User, order.user_id)
    if customer:
        notify_order_state_change(db, order.id, order.phone, customer.email, status)

    db.commit()
    return {"message": "Order status updated"}
