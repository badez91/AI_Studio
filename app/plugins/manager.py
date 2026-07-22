from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

from app.config.settings import get_settings
from app.plugins.base import PluginBase


class PluginManager:
    """Discovers, loads, and manages application plugins."""

    def __init__(self, plugin_dir: str | None = None) -> None:
        settings = get_settings()
        self.plugin_dir = Path(plugin_dir or settings.project_root / "plugins")
        self._plugins: dict[str, PluginBase] = {}
        self._errors: list[str] = []

    def discover(self) -> None:
        """Discover plugins from the plugin directory."""

        if not self.plugin_dir.exists():
            return
        for path in sorted(self.plugin_dir.glob("*.py")):
            if path.name.startswith("_"):
                continue
            try:
                module = self._import_module(path)
                plugin = self._load_plugin(module)
                if plugin is not None:
                    self._plugins[plugin.name] = plugin
            except Exception as exc:
                self._errors.append(f"Failed to load plugin {path.name}: {exc}")

    def _import_module(self, path: Path) -> Any:
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[path.stem] = module
        spec.loader.exec_module(module)
        return module

    def _load_plugin(self, module: Any) -> PluginBase | None:
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, PluginBase)
                and attr is not PluginBase
            ):
                return attr()
        return None

    def get(self, name: str) -> PluginBase | None:
        """Return a loaded plugin by name."""

        return self._plugins.get(name)

    @property
    def loaded(self) -> list[PluginBase]:
        """Return all successfully loaded plugins."""

        return list(self._plugins.values())

    @property
    def errors(self) -> list[str]:
        """Return plugin loading errors."""

        return list(self._errors)
