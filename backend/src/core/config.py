"""
NexERP Enterprise ERP - Production Configuration & Settings.
Uses Pydantic BaseSettings to load from environment variables with
sensible secure defaults for both development and production modes.
"""

import secrets
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class NexERPSettings(BaseSettings):
    """
    Application-wide configuration settings loaded from environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ---- Application Identity ----
    app_name: str = "NexERP Enterprise"
    app_version: str = "1.0.0"
    environment: str = "development"  # production | staging | development
    debug: bool = False

    # ---- Database ----
    database_url: str = "sqlite+aiosqlite:///./nexerp.db"
    db_pool_size: int = 20
    db_max_overflow: int = 40
    db_pool_timeout_seconds: int = 30
    db_echo_sql: bool = False

    # ---- Authentication & JWT ----
    jwt_secret_key: str = secrets.token_hex(32)  # Override in production!
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7

    # ---- Password Policy ----
    password_min_length: int = 12
    password_max_failed_attempts: int = 5
    account_lockout_minutes: int = 30

    # ---- API Rate Limiting ----
    rate_limit_requests_per_minute: int = 120
    rate_limit_burst: int = 30

    # ---- CORS Origins ----
    allowed_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ---- Redis ----
    redis_url: Optional[str] = None

    # ---- Celery ----
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None

    # ---- File Storage ----
    upload_max_size_mb: int = 50
    upload_allowed_extensions: List[str] = ["pdf", "xlsx", "csv", "jpg", "png", "docx"]

    # ---- Email Notifications (SMTP) ----
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: str = "no-reply@nexerp.internal"
    smtp_use_tls: bool = True

    # ---- Logging ----
    log_level: str = "INFO"
    log_format: str = "json"  # json | plain

    # Backward-compatible names used by the original application bootstrap.
    @property
    def APP_NAME(self) -> str:
        return self.app_name

    @property
    def APP_VERSION(self) -> str:
        return self.app_version

    @property
    def ENVIRONMENT(self) -> str:
        return self.environment

    @property
    def DATABASE_URL(self) -> str:
        return self.database_url

    @property
    def DATABASE_ECHO(self) -> bool:
        return self.db_echo_sql

    @property
    def DATABASE_POOL_SIZE(self) -> int:
        return self.db_pool_size

    @property
    def DATABASE_MAX_OVERFLOW(self) -> int:
        return self.db_max_overflow

    @property
    def DATABASE_POOL_TIMEOUT(self) -> int:
        return self.db_pool_timeout_seconds

    @property
    def DEFAULT_TENANT_ID(self) -> str:
        return "org_corp_hq_001"

    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        return self.jwt_access_token_expire_minutes

    @property
    def REFRESH_TOKEN_EXPIRE_DAYS(self) -> int:
        return self.jwt_refresh_token_expire_days

    @property
    def SECRET_KEY(self) -> str:
        return self.jwt_secret_key

    @property
    def JWT_ALGORITHM(self) -> str:
        return self.jwt_algorithm

    @property
    def CORS_ORIGINS(self) -> List[str]:
        return self.allowed_origins

    @property
    def MAX_UPLOAD_SIZE_MB(self) -> int:
        return self.upload_max_size_mb

    @property
    def ALLOWED_UPLOAD_EXTENSIONS(self) -> List[str]:
        return self.upload_allowed_extensions

    @property
    def STORAGE_LOCAL_ROOT(self) -> str:
        return "./storage"

    @property
    def API_V1_PREFIX(self) -> str:
        return "/api/v1"


@lru_cache(maxsize=1)
def get_settings() -> NexERPSettings:
    """
    Cached singleton settings instance.
    Use get_settings() everywhere in the application.
    """
    return NexERPSettings()


# Module-level alias for convenience
settings = get_settings()
