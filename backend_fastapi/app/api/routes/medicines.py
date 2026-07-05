from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Medicine, User
from app.schemas.medicine import MedicineOut

router = APIRouter()


@router.get("", response_model=list[MedicineOut])
def search_medicines(
    q: str | None = Query(None, description="Search by medicine name"),
    category: str | None = None,
    manufacturer: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    exp_before: date | None = None,
    exp_after: date | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    filters = []
    if q:
        filters.append(Medicine.medicine_name.ilike(f"%{q}%"))
    if category:
        filters.append(Medicine.category == category)
    if manufacturer:
        filters.append(Medicine.manufacturer == manufacturer)
    if min_price is not None:
        filters.append(Medicine.price >= min_price)
    if max_price is not None:
        filters.append(Medicine.price <= max_price)
    if exp_before:
        filters.append(Medicine.expiry_date <= exp_before)
    if exp_after:
        filters.append(Medicine.expiry_date >= exp_after)

    query = db.query(Medicine)
    if filters:
        query = query.filter(and_(*filters))

    return query.order_by(Medicine.medicine_name.asc()).limit(100).all()
