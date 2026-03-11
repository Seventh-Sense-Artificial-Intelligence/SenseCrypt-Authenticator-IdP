from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from app.config import get_settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: str) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token, get_settings().SECRET_KEY, algorithms=["HS256"]
        )
        return payload.get("sub")
    except jwt.PyJWTError:
        return None


def create_verification_token(user_id: str) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {"sub": user_id, "purpose": "email-verification", "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_verification_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token, get_settings().SECRET_KEY, algorithms=["HS256"]
        )
        if payload.get("purpose") != "email-verification":
            return None
        return payload.get("sub")
    except jwt.PyJWTError:
        return None


def create_password_reset_token(user_id: str) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    payload = {"sub": user_id, "purpose": "password-reset", "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_password_reset_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token, get_settings().SECRET_KEY, algorithms=["HS256"]
        )
        if payload.get("purpose") != "password-reset":
            return None
        return payload.get("sub")
    except jwt.PyJWTError:
        return None
