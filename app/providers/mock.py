from __future__ import annotations

from typing import Any

from app.providers.base import Provider


class MockTextProvider(Provider):
    def capabilities(self) -> list[str]:
        return ["text", "chat"]

    def invoke(self, capability: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {"capability": capability, "provider": "mock-text", "output": "mocked"}


class MockMediaProvider(Provider):
    def capabilities(self) -> list[str]:
        return ["image", "voice"]

    def invoke(self, capability: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {"capability": capability, "provider": "mock-media", "output": "mocked"}
