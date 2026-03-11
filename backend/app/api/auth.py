from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token, ForgotPassword, ResetPassword
from app.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_verification_token,
    decode_verification_token,
    create_password_reset_token,
    decode_password_reset_token,
)
from app.services.email import send_verification_email, send_welcome_email, send_password_reset_email

router = APIRouter(prefix="/auth", tags=["auth"])

VERIFICATION_EXPIRY_HOURS = 24


def _build_verification_url(token: str) -> str:
    base = get_settings().BASE_URL.rstrip("/")
    return f"{base}/verify-email?token={token}"


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    existing = result.scalar_one_or_none()

    if existing and existing.is_verified:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    if existing and not existing.is_verified:
        # First to register wins — don't update name/password, just resend email
        token = create_verification_token(existing.id)
        existing.verification_token = token
        existing.verification_token_expires_at = datetime.now(timezone.utc) + timedelta(
            hours=VERIFICATION_EXPIRY_HOURS
        )
        await db.commit()
        send_verification_email(data.email, _build_verification_url(token))
        return {"message": "Check your email to verify your account"}

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        is_verified=False,
    )
    db.add(user)
    await db.flush()

    token = create_verification_token(user.id)
    user.verification_token = token
    user.verification_token_expires_at = datetime.now(timezone.utc) + timedelta(
        hours=VERIFICATION_EXPIRY_HOURS
    )
    await db.commit()

    send_verification_email(data.email, _build_verification_url(token))
    return {"message": "Check your email to verify your account"}


@router.get("/verify-email", response_model=Token)
async def verify_email(token: str = Query(...), db: AsyncSession = Depends(get_db)):
    user_id = decode_verification_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired link"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired link"
        )

    if user.is_verified:
        # Already verified — just log them in
        return Token(access_token=create_access_token(user.id))

    if user.verification_token != token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired link"
        )

    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires_at = None
    await db.commit()

    send_welcome_email(user.email, user.full_name)
    return Token(access_token=create_access_token(user.id))


@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified"
        )
    return Token(access_token=create_access_token(user.id))


@router.post("/forgot-password")
async def forgot_password(data: ForgotPassword, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if user and user.is_verified:
        token = create_password_reset_token(user.id)
        base = get_settings().BASE_URL.rstrip("/")
        reset_url = f"{base}/?resetToken={token}"
        send_password_reset_email(user.email, reset_url)
    return {"message": "If an account exists, a reset email has been sent"}


@router.post("/reset-password")
async def reset_password(data: ResetPassword, db: AsyncSession = Depends(get_db)):
    user_id = decode_password_reset_token(data.token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired link"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired link"
        )

    user.password_hash = hash_password(data.password)
    await db.commit()
    return {"message": "Password has been reset successfully"}
