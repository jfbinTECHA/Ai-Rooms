from __future__ import annotations

from functools import lru_cache

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Runtime configuration for the backend service."""

    secret_key: str = Field("change-me", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    database_url: str = Field("sqlite:///./ai_rooms.db", env="DATABASE_URL")

    class Config:
        env_file = ".env"
        env_prefix = "AI_ROOMS_"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
