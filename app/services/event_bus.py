from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Event:
    """Represents a message published on the event bus."""

    name: str
    payload: dict[str, Any]


class EventBus:
    """Lightweight publish/subscribe event bus."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[Event], None]]] = {}

    def subscribe(self, event_name: str, handler: Callable[[Event], None]) -> None:
        """Register a handler for a specific event name."""

        self._subscribers.setdefault(event_name, []).append(handler)

    def publish(self, event: Event) -> None:
        """Publish an event to all registered handlers."""

        handlers = self._subscribers.get(event.name, [])
        for handler in handlers:
            handler(event)

    def clear(self) -> None:
        """Remove all subscribers."""

        self._subscribers.clear()
