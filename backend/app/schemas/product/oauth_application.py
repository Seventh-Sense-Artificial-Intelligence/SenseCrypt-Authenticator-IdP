from datetime import datetime
from pydantic import BaseModel, field_validator
from urllib.parse import urlparse


class OAuthApplicationCreate(BaseModel):
    name: str
    application_type: str
    redirect_uris: list[str]
    post_logout_redirect_uris: list[str] = []
    allowed_scopes: list[str] = ["openid", "profile", "email"]
    grant_types: list[str] = ["authorization_code", "refresh_token"]
    token_endpoint_auth_method: str = "client_secret_post"

    @field_validator("application_type")
    @classmethod
    def validate_application_type(cls, v: str) -> str:
        allowed = {"web", "spa", "native", "machine_to_machine"}
        if v not in allowed:
            raise ValueError(
                f"application_type must be one of: {', '.join(sorted(allowed))}"
            )
        return v

    @field_validator("redirect_uris")
    @classmethod
    def validate_redirect_uris(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("At least one redirect_uri is required")
        for uri in v:
            parsed = urlparse(uri)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"Invalid URL: {uri}")
        return v


class OAuthApplicationRead(BaseModel):
    id: str
    name: str
    client_id: str
    application_type: str
    redirect_uris: list[str]
    post_logout_redirect_uris: list[str]
    allowed_scopes: list[str]
    grant_types: list[str]
    token_endpoint_auth_method: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OAuthApplicationCreateResponse(OAuthApplicationRead):
    client_secret: str


class OAuthApplicationUpdate(BaseModel):
    name: str | None = None
    redirect_uris: list[str] | None = None
    post_logout_redirect_uris: list[str] | None = None
    allowed_scopes: list[str] | None = None
    grant_types: list[str] | None = None
    token_endpoint_auth_method: str | None = None
    is_active: bool | None = None


class RotateSecretResponse(BaseModel):
    client_secret: str
