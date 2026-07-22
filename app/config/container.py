from __future__ import annotations

from typing import Any, Callable, TypeVar

T = TypeVar("T")


class Container:
    """Lightweight dependency registration and resolution container."""

    def __init__(self) -> None:
        self._registry: dict[str, Callable[[], Any]] = {}

    def register(self, name: str, factory: Callable[[], T]) -> None:
        self._registry[name] = factory

    def resolve(self, name: str) -> Any:
        try:
            factory = self._registry[name]
        except KeyError as exc:
            raise KeyError(f"Dependency '{name}' is not registered.") from exc
        return factory()

    def clear(self) -> None:
        self._registry.clear()


def build_container() -> Container:
    """Build and return a container preloaded with core services."""

    from app.config.logging import configure_logging
    from app.config.settings import get_settings

    container = Container()
    container.register("settings", get_settings)
    container.register("logger", configure_logging)
    return container
