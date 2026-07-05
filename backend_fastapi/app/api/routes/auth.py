from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models import User, UserRole
from app.schemas.auth import LoginRequest, SignUpRequest, TokenResponse

router = APIRouter()


@router.post("/signup", response_model=TokenResponse)
def signup(payload: SignUpRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.CUSTOMER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(str(user.id))
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        full_name=user.full_name,
        role="admin" if user.role == UserRole.ADMIN else "customer",
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(str(user.id))
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        full_name=user.full_name,
        role="admin" if user.role == UserRole.ADMIN else "customer",
    )
