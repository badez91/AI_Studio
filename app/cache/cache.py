from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config.settings import get_settings


class CacheStore:
    """Simple filesystem-backed cache store placeholder."""

    def __init__(self, root: str | None = None) -> None:
        settings = get_settings()
        self.root = Path(root or settings.cache_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> Any | None:
        path = self.root / key
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def set(self, key: str, value: Any) -> None:
        path = self.root / key
        path.write_text(str(value), encoding="utf-8")
