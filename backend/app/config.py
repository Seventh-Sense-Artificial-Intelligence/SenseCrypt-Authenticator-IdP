from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/portal_db"
    SECRET_KEY: str = "change-me-in-production"
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "noreply@yourdomain.com"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    BASE_URL: str = "http://localhost:8000"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
