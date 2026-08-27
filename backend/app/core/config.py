"""Enterprise Pydantic Settings Configuration for FraudGuard AI."""

from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration container."""

    # Project Information
    PROJECT_NAME: str = "FraudGuard AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True

    # Security & JWT Credentials
    SECRET_KEY: str = "fraudguard_ai_super_secret_jwt_encryption_key_2026_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Cross-Origin Resource Sharing (CORS)
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # Database Configuration (Postgres / Async SQLite fallback)
    DATABASE_URL: str = "sqlite+aiosqlite:///./fraudguard.db"
    POSTGRES_SERVER: Optional[str] = "localhost"
    POSTGRES_USER: Optional[str] = "postgres"
    POSTGRES_PASSWORD: Optional[str] = "postgres"
    POSTGRES_DB: Optional[str] = "fraudguard_db"
    POSTGRES_PORT: Optional[int] = 5432

    # Redis Cache & Online Feature Store
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False

    # Machine Learning & Decision Thresholds
    ML_REVIEW_THRESHOLD: float = 0.30
    ML_CHALLENGE_3DS_THRESHOLD: float = 0.65
    ML_DECLINE_THRESHOLD: float = 0.85
    IMPOSSIBLE_TRAVEL_MAX_KMH: float = 950.0

    # Operational Parameters
    SIMULATOR_DEFAULT_TPS: int = 5
    ENABLE_WEBSOCKET_STREAM: bool = True
    MAX_HISTORICAL_TRANSACTIONS_BUFFER: int = 5000

    # Default Superuser Credentials
    FIRST_SUPERUSER_EMAIL: str = "admin@fraudguard.ai"
    FIRST_SUPERUSER_PASSWORD: str = "Admin@FraudGuard2026"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
