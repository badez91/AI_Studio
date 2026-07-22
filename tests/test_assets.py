from __future__ import annotations

from pathlib import Path

import pytest

from app.assets.asset_manager import AssetManager
from app.cache.cache import CacheStore


def test_asset_manager_write_and_read(tmp_path: Path) -> None:
    manager = AssetManager(root=str(tmp_path))
    target = manager.write("demo/note.txt", "hello")

    assert target.exists()
    assert manager.read("demo/note.txt") == "hello"


def test_asset_manager_exists(tmp_path: Path) -> None:
    manager = AssetManager(root=str(tmp_path))
    manager.write("demo/note.txt", "hello")

    assert manager.exists("demo/note.txt") is True
    assert manager.exists("demo/missing.txt") is False


def test_asset_manager_creates_nested_directories(tmp_path: Path) -> None:
    manager = AssetManager(root=str(tmp_path))
    manager.write("a/b/c/deep.txt", "deep")

    assert (tmp_path / "a" / "b" / "c" / "deep.txt").exists()


def test_cache_store_set_and_get(tmp_path: Path) -> None:
    store = CacheStore(root=str(tmp_path))
    store.set("key", "value")

    assert store.get("key") == "value"


def test_cache_store_missing_key_returns_none(tmp_path: Path) -> None:
    store = CacheStore(root=str(tmp_path))

    assert store.get("missing") is None
