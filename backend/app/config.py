from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/portal_db"
    SECRET_KEY: str = "change-me-in-production"
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "noreply@yourdomain.com"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    BASE_URL: str = "http://localhost:8000"

    # OIDC Identity Provider settings
    OIDC_ISSUER_URL: str = "http://localhost:8000"
    OIDC_RSA_PRIVATE_KEY: str = ""
    OIDC_AUTH_CODE_EXPIRE_MINUTES: int = 10
    OIDC_ID_TOKEN_EXPIRE_MINUTES: int = 60
    OIDC_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # QR challenge-response auth
    CA_PUBLIC_KEY_PEM: str = ""
    AUTH_CHALLENGE_EXPIRE_MINUTES: int = 5
    DEMO_MODE: bool = True

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
