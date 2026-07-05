from fastapi import APIRouter

from app.api.routes import assistant, auth, medicines, orders, staff

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(medicines.router, prefix="/medicines", tags=["medicines"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(staff.router, prefix="/staff", tags=["staff"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
