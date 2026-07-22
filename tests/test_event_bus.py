from __future__ import annotations

from app.services.event_bus import Event, EventBus


def test_subscribe_and_receive_event() -> None:
    bus = EventBus()
    received: list[Event] = []

    def handler(event: Event) -> None:
        received.append(event)

    bus.subscribe("test", handler)
    bus.publish(Event(name="test", payload={"key": "value"}))

    assert len(received) == 1
    assert received[0].name == "test"
    assert received[0].payload == {"key": "value"}


def test_publish_to_multiple_handlers() -> None:
    bus = EventBus()
    calls: list[str] = []

    def handler_a(event: Event) -> None:
        calls.append("a")

    def handler_b(event: Event) -> None:
        calls.append("b")

    bus.subscribe("test", handler_a)
    bus.subscribe("test", handler_b)
    bus.publish(Event(name="test", payload={}))

    assert calls == ["a", "b"]


def test_handler_not_called_for_other_events() -> None:
    bus = EventBus()
    received: list[Event] = []

    def handler(event: Event) -> None:
        received.append(event)

    bus.subscribe("test", handler)
    bus.publish(Event(name="other", payload={}))

    assert received == []


def test_clear_removes_all_subscribers() -> None:
    bus = EventBus()
    received: list[Event] = []

    def handler(event: Event) -> None:
        received.append(event)

    bus.subscribe("test", handler)
    bus.clear()
    bus.publish(Event(name="test", payload={}))

    assert received == []
