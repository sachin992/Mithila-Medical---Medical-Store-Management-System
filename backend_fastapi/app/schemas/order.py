from datetime import datetime, date
from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    medicine_id: int
    quantity: int = Field(ge=1)


class CartItemOut(BaseModel):
    id: int
    medicine_id: int
    medicine_name: str
    unit_price: float
    quantity: int
    line_total: float


class CheckoutRequest(BaseModel):
    customer_name: str
    phone: str
    address: str
    city: str
    pincode: str
    payment_method: str


class OrderItemOut(BaseModel):
    medicine_id: int
    medicine_name: str
    unit_price: float
    quantity: int
    line_total: float


class OrderEventOut(BaseModel):
    event_type: str
    note: str | None
    created_at: datetime


class PaymentOut(BaseModel):
    method: str
    status: str
    amount: float
    gateway_reference: str | None


class InvoiceOut(BaseModel):
    invoice_id: str
    issued_at: datetime
    order_id: int
    customer_name: str
    total_amount: float
    payment_method: str


class OrderOut(BaseModel):
    id: int
    status: str
    total_price: float
    created_at: datetime
    delivery_date: date | None
    customer_name: str
    phone: str
    address: str
    city: str
    pincode: str
    items: list[OrderItemOut]
    timeline: list[OrderEventOut]
    payments: list[PaymentOut]
