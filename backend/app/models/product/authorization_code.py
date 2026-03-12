import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class AuthorizationCode(Base):
    __tablename__ = "authorization_codes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    code: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    client_id: Mapped[str] = mapped_column(String(64), index=True)
    email: Mapped[str] = mapped_column(String(255))
    redirect_uri: Mapped[str] = mapped_column(String(2048))
    scope: Mapped[str] = mapped_column(String(512))
    nonce: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    code_challenge: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    code_challenge_method: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True
    )
    state: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
