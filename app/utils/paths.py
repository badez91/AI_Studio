from __future__ import annotations

from pathlib import Path

from app.config.settings import get_settings


def ensure_directory(path: str | Path) -> Path:
    """Create a directory if it does not exist."""

    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def get_project_root() -> Path:
    """Return the project root directory."""

    return get_settings().project_root
