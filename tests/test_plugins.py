from __future__ import annotations

import sys
from pathlib import Path

import pytest

from app.plugins.base import PluginBase
from app.plugins.manager import PluginManager


class ValidPlugin(PluginBase):
    @property
    def name(self) -> str:
        return "valid"

    @property
    def version(self) -> str:
        return "1.0.0"

    def initialize(self) -> None:
        self.initialized = True

    def shutdown(self) -> None:
        self.shutdown_called = True


class MalformedPlugin:
    pass


def _write_plugin(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_discover_valid_plugin(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    _write_plugin(
        plugin_dir / "valid_plugin.py",
        "from app.plugins.base import PluginBase\n"
        "class ValidPlugin(PluginBase):\n"
        "    name = 'valid'\n"
        "    version = '1.0.0'\n"
        "    def initialize(self): pass\n"
        "    def shutdown(self): pass\n",
    )

    manager = PluginManager(plugin_dir=str(plugin_dir))
    manager.discover()

    assert len(manager.loaded) == 1
    assert manager.get("valid") is not None
    assert manager.errors == []


def test_discover_malformed_plugin_does_not_crash(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    _write_plugin(
        plugin_dir / "malformed_plugin.py",
        "raise RuntimeError('bad plugin')\n",
    )

    manager = PluginManager(plugin_dir=str(plugin_dir))
    manager.discover()

    assert len(manager.loaded) == 0
    assert len(manager.errors) == 1
    assert "malformed_plugin.py" in manager.errors[0]


def test_discover_ignores_non_plugin_classes(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    _write_plugin(
        plugin_dir / "noop_plugin.py",
        "class NoopPlugin:\n"
        "    pass\n",
    )

    manager = PluginManager(plugin_dir=str(plugin_dir))
    manager.discover()

    assert len(manager.loaded) == 0
    assert manager.errors == []
