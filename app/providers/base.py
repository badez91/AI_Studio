from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Provider(ABC):
    """Abstract provider contract for AI backends."""

    @abstractmethod
    def capabilities(self) -> list[str]:
        """Return the list of capabilities this provider supports."""

    @abstractmethod
    def invoke(self, capability: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Invoke the provider for a specific capability."""
