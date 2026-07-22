from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config.settings import get_settings
from app.utils.paths import ensure_directory


class AssetManager:
    """Manages artifact directories for generated assets."""

    def __init__(self, root: str | None = None) -> None:
        settings = get_settings()
        self.root = Path(root or settings.project_root / "output")
        ensure_directory(self.root)

    def write(self, relative_path: str, content: Any) -> Path:
        """Write content to an asset path relative to the asset root."""

        target = self.root / relative_path
        ensure_directory(target.parent)
        target.write_text(str(content), encoding="utf-8")
        return target

    def read(self, relative_path: str) -> str | None:
        """Read content from an asset path relative to the asset root."""

        target = self.root / relative_path
        if not target.exists():
            return None
        return target.read_text(encoding="utf-8")

    def exists(self, relative_path: str) -> bool:
        """Check whether an asset exists."""

        return (self.root / relative_path).exists()
