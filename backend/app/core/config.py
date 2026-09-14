from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AgroGuard API"
    app_version: str = "0.1.0"
    environment: Literal["development", "test", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/agroguard"
    )
    initialize_database: bool = False
    cors_origins: list[str] = ["http://localhost:5173"]

    telegram_bot_token: SecretStr | None = None
    telegram_chat_id: str | None = None

    llm_api_key: SecretStr | None = None
    llm_endpoint: str = "http://localhost:11434/v1"
    llm_model: str = "gemma3:latest"
    openweather_api_key: SecretStr | None = None
    openweather_base_url: str = "https://api.openweathermap.org"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="AGROGUARD_",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

