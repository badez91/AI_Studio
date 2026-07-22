from __future__ import annotations

from typing import Callable

from app.telemetry.logging import TelemetryEvent


class TelemetryHook:
    """Collects telemetry events from workflow execution."""

    def __init__(self) -> None:
        self._handlers: list[Callable[[TelemetryEvent], None]] = []

    def register(self, handler: Callable[[TelemetryEvent], None]) -> None:
        self._handlers.append(handler)

    def emit(self, event: TelemetryEvent) -> None:
        for handler in self._handlers:
            handler(event)
