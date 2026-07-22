from __future__ import annotations

from typing import Any

import pytest

from app.evaluation.metrics import format_evaluation, score_workflow
from app.telemetry.hooks import TelemetryHook
from app.telemetry.logging import TelemetryEvent


def test_telemetry_hook_registration() -> None:
    hook = TelemetryHook()
    received: list[TelemetryEvent] = []

    def handler(event: TelemetryEvent) -> None:
        received.append(event)

    hook.register(handler)
    hook.emit(TelemetryEvent(workflow_id="1", step="a", state="completed", duration_ms=1.0))

    assert len(received) == 1
    assert received[0].workflow_id == "1"


def test_telemetry_event_metadata() -> None:
    event = TelemetryEvent(
        workflow_id="1",
        step="a",
        state="completed",
        duration_ms=1.0,
        metadata={"model": "mock"},
    )
    assert event.metadata == {"model": "mock"}


def test_format_evaluation_output() -> None:
    payload: dict[str, Any] = {
        "workflow_id": "wf-1",
        "completeness": 1.0,
        "step_count": 3,
    }
    output = format_evaluation(payload)
    assert "wf-1" in output
    assert "completeness: 1.0" in output
    assert "step_count: 3" in output


def test_score_workflow_completed() -> None:
    context = {"state": "completed", "results": ["a", "b"], "errors": []}
    scores = score_workflow(context)
    assert scores["completeness"] == 1.0
    assert scores["step_count"] == 2
    assert scores["error_count"] == 0


def test_score_workflow_failed() -> None:
    context = {"state": "failed", "results": [], "errors": ["boom"]}
    scores = score_workflow(context)
    assert scores["completeness"] == 0.0
    assert scores["error_count"] == 1
