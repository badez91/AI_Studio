from __future__ import annotations

import pytest

from app.config.container import Container


class FakeService:
    def __init__(self, value: str = "default") -> None:
        self.value = value


def test_resolve_registered_dependency() -> None:
    container = Container()
    container.register("service", lambda: FakeService("resolved"))
    service = container.resolve("service")
    assert isinstance(service, FakeService)
    assert service.value == "resolved"


def test_resolve_unregistered_dependency_raises() -> None:
    container = Container()
    with pytest.raises(KeyError):
        container.resolve("missing")


def test_clear_registry() -> None:
    container = Container()
    container.register("service", lambda: FakeService())
    container.clear()
    with pytest.raises(KeyError):
        container.resolve("service")


def test_register_overwrites_existing() -> None:
    container = Container()
    container.register("service", lambda: FakeService("first"))
    container.register("service", lambda: FakeService("second"))
    service = container.resolve("service")
    assert service.value == "second"
