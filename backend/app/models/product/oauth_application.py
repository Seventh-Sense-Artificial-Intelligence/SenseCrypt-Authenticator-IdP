import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class ApplicationType(str, enum.Enum):
    web = "web"
    spa = "spa"
    native = "native"
    machine_to_machine = "machine_to_machine"


class OAuthApplication(Base):
    __tablename__ = "oauth_applications"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    client_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    client_secret_hash: Mapped[str] = mapped_column(String(255))
    application_type: Mapped[ApplicationType] = mapped_column(Enum(ApplicationType))
    redirect_uris: Mapped[list] = mapped_column(JSON, default=list)
    post_logout_redirect_uris: Mapped[list] = mapped_column(JSON, default=list)
    allowed_scopes: Mapped[list] = mapped_column(
        JSON, default=lambda: ["openid", "profile", "email"]
    )
    grant_types: Mapped[list] = mapped_column(
        JSON, default=lambda: ["authorization_code", "refresh_token"]
    )
    token_endpoint_auth_method: Mapped[str] = mapped_column(
        String(64), default="client_secret_post"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
