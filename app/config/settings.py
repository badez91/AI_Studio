from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env files."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="ai-studio")
    environment: Literal["development", "testing", "production"] = "development"
    debug: bool = False
    log_level: str = "INFO"
    log_path: str = "logs/ai-studio.log"
    database_url: str = "sqlite:///./ai_studio.db"
    cache_dir: str = "cache"

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[2]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
