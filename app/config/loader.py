from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from app.config.settings import get_settings


def load_yaml_config(path: str | Path) -> dict[str, Any]:
    """Load YAML configuration from disk."""

    config_path = Path(path)
    if not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_app_config() -> dict[str, Any]:
    """Load environment-backed application config."""

    settings = get_settings()
    return {
        "app_name": settings.app_name,
        "environment": settings.environment,
        "debug": settings.debug,
        "log_level": settings.log_level,
        "database_url": settings.database_url,
        "cache_dir": settings.cache_dir,
    }
