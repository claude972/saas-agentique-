"""Configuration applicative (variables d'environnement)."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "BTP Agent Platform"
    environment: str = "development"
    debug: bool = True

    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60

    database_url: str = "sqlite:///./btp.db"
    redis_url: str = "redis://localhost:6379/0"

    # Telegram (optionnel) : bot entrant (webhook) + notifications sortantes.
    telegram_bot_token: str = ""
    telegram_webhook_secret: str = ""
    telegram_alert_chat_id: str = ""

    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
