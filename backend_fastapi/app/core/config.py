from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Mithila Medical API"
    database_url: str = "sqlite:///./medical_store.db"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    cancellation_window_minutes: int = 30
    low_stock_threshold: int = 20
    chat_memory_ttl_minutes: int = 180
    allowed_origins: str = "http://localhost:5173"
    email_provider: str = "console"
    sms_provider: str = "console"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_timeout_seconds: int = 30
    admin_email: str = "admin@mithilamedical.com"
    admin_password: str = "Admin@123"
    admin_full_name: str = "System Admin"


@lru_cache
def get_settings() -> Settings:
    return Settings()
