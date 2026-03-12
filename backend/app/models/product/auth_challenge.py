import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class AuthChallenge(Base):
    __tablename__ = "auth_challenges"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    challenge_nonce: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    purpose_id: Mapped[str] = mapped_column(String(64))
    client_id: Mapped[str] = mapped_column(String(64))
    redirect_uri: Mapped[str] = mapped_column(String(2048))
    scope: Mapped[str] = mapped_column(String(512))
    state: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    nonce: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    code_challenge: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    code_challenge_method: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True
    )
    response_type: Mapped[str] = mapped_column(String(16), default="code")
    login_hint: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    redirect_url: Mapped[Optional[str]] = mapped_column(String(4096), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
