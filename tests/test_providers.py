from __future__ import annotations

import pytest

from app.providers.base import Provider
from app.providers.mock import MockMediaProvider, MockTextProvider
from app.providers.router import ProviderEntry, ProviderRegistry, ProviderRouter


class _StubProvider(Provider):
    def __init__(self, capabilities_list: list[str]) -> None:
        self._capabilities = capabilities_list

    def capabilities(self) -> list[str]:
        return list(self._capabilities)

    def invoke(self, capability: str, payload: dict[str, str]) -> dict[str, str]:
        return {"capability": capability, "provider": "stub", "output": "ok"}


def test_register_and_get_provider() -> None:
    registry = ProviderRegistry()
    provider = _StubProvider(["text"])
    registry.register(provider)

    entry = registry.get("text")
    assert entry is not None
    assert entry.provider is provider
    assert entry.name == "_StubProvider"


def test_get_missing_capability_returns_none() -> None:
    registry = ProviderRegistry()
    assert registry.get("missing") is None


def test_all_for_capability() -> None:
    registry = ProviderRegistry()
    provider_a = _StubProvider(["text"])
    provider_b = _StubProvider(["text", "chat"])
    registry.register(provider_a)
    registry.register(provider_b)

    entries = registry.all_for("text")
    assert len(entries) == 2


def test_router_returns_first_provider() -> None:
    registry = ProviderRegistry()
    registry.register(MockTextProvider())
    registry.register(MockMediaProvider())

    router = ProviderRouter(registry)
    result = router.route("text", {"prompt": "hello"})
    assert result["provider"] == "mock-text"


def test_router_raises_for_unknown_capability() -> None:
    registry = ProviderRegistry()
    router = ProviderRouter(registry)

    with pytest.raises(LookupError):
        router.route("unknown", {})


def test_router_fallback_to_next_provider() -> None:
    registry = ProviderRegistry()
    failing = _StubProvider(["text"])
    failing.invoke = lambda capability, payload: (_ for _ in ()).throw(RuntimeError("fail"))
    registry.register(failing)
    registry.register(MockTextProvider())

    router = ProviderRouter(registry)
    with pytest.raises(RuntimeError):
        router.route("text", {})
