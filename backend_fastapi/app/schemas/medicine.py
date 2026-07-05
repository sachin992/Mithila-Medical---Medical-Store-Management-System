from datetime import date
from pydantic import BaseModel


class MedicineCreate(BaseModel):
    medicine_name: str
    quantity: int
    price: float
    description: str | None = None
    category: str | None = None
    manufacturer: str | None = None
    expiry_date: date | None = None


class MedicineUpdate(BaseModel):
    medicine_name: str | None = None
    quantity: int | None = None
    price: float | None = None
    description: str | None = None
    category: str | None = None
    manufacturer: str | None = None
    expiry_date: date | None = None


class MedicineOut(BaseModel):
    id: int
    medicine_name: str
    quantity: int
    price: float
    description: str | None
    category: str | None
    manufacturer: str | None
    expiry_date: date | None

    class Config:
        from_attributes = True
