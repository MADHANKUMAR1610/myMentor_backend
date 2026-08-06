"""Application configuration."""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env."""

    APP_NAME: str = "Digipin Academy API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # MongoDB (keep temporarily while migrating)
    MONGO_DATABASE_URL: str | None = None
    MONGO_DATABASE_NAME: str | None = None

    # PostgreSQL
    POSTGRES_DATABASE_URL: str

    # Gemini AI
    GEMINI_API_KEY: SecretStr

    JWT_SECRET: SecretStr = SecretStr(
        "change-this-secret"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://my-mentor-lms.onrender.com",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()