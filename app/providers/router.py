from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


class ProviderRegistry:
    """Registry for provider instances by capability."""

    def __init__(self) -> None:
        self._providers: dict[str, list[ProviderEntry]] = {}

    def register(self, provider: Provider) -> None:
        for capability in provider.capabilities():
            self._providers.setdefault(capability, []).append(
                ProviderEntry(provider=provider, name=provider.__class__.__name__)
            )

    def get(self, capability: str) -> ProviderEntry | None:
        providers = self._providers.get(capability, [])
        if not providers:
            return None
        return providers[0]

    def all_for(self, capability: str) -> list[ProviderEntry]:
        return list(self._providers.get(capability, []))


@dataclass
class ProviderEntry:
    provider: Provider
    name: str = field(default="")


class ProviderRouter:
    """Routes capability requests to registered providers with fallback."""

    def __init__(self, registry: ProviderRegistry) -> None:
        self.registry = registry

    def route(self, capability: str, payload: dict[str, Any]) -> dict[str, Any]:
        entry = self.registry.get(capability)
        if entry is None:
            raise LookupError(f"No provider registered for capability '{capability}'.")
        return entry.provider.invoke(capability, payload)
