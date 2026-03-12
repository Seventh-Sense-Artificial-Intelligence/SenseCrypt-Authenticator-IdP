from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    OIDC_ISSUER_URL: str = "http://localhost:8000"
    CLIENT_ID: str = ""
    CLIENT_SECRET: str = ""
    REDIRECT_URI: str = "http://localhost:9000/callback"
    SCOPES: str = "openid profile email"

    model_config = {"env_file": ".env", "extra": "ignore"}

@lru_cache
def get_settings() -> Settings:
    return Settings()
