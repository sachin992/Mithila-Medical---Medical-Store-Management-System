from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import User, UserRole

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.allowed_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


def bootstrap_admin_user() -> None:
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if existing_admin:
            return

        admin_user = db.query(User).filter(User.email == settings.admin_email).first()
        if admin_user:
            admin_user.role = UserRole.ADMIN
            admin_user.password_hash = hash_password(settings.admin_password)
            admin_user.full_name = settings.admin_full_name
        else:
            admin_user = User(
                full_name=settings.admin_full_name,
                email=settings.admin_email,
                password_hash=hash_password(settings.admin_password),
                role=UserRole.ADMIN,
            )
            db.add(admin_user)
        db.commit()
    finally:
        db.close()


@app.on_event("startup")
def startup_create_tables():
    Base.metadata.create_all(bind=engine)
    bootstrap_admin_user()
