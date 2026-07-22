from __future__ import annotations

import pytest

from app.workflows.engine import Step, WorkflowEngine
from app.workflows.state import WorkflowContext, WorkflowState


def _success_step(value: str) -> Step:
    def handler(context: WorkflowContext) -> str:
        return value

    return Step(name=f"success-{value}", handler=handler)


def _failing_step(message: str) -> Step:
    def handler(context: WorkflowContext) -> None:
        raise RuntimeError(message)

    return Step(name="failing", handler=handler)


def test_successful_workflow_execution() -> None:
    steps = [_success_step("a"), _success_step("b"), _success_step("c")]
    engine = WorkflowEngine(steps)
    context = WorkflowContext()

    result = engine.run(context)

    assert result.state == WorkflowState.COMPLETED
    assert result.current_step == 2
    assert result.results == ["a", "b", "c"]
    assert result.errors == []


def test_failed_step_stops_workflow() -> None:
    steps = [_success_step("a"), _failing_step("boom"), _success_step("c")]
    engine = WorkflowEngine(steps)
    context = WorkflowContext()

    result = engine.run(context)

    assert result.state == WorkflowState.FAILED
    assert result.current_step == 1
    assert result.results == ["a"]
    assert len(result.errors) == 1
    assert "boom" in result.errors[0]


def test_cancel_workflow() -> None:
    steps = [_success_step("a"), _success_step("b")]
    engine = WorkflowEngine(steps)
    context = WorkflowContext()
    context.state = WorkflowState.CANCELLED

    result = engine.run(context)

    assert result.state == WorkflowState.CANCELLED
    assert result.results == []


def test_empty_workflow_completes() -> None:
    engine = WorkflowEngine([])
    context = WorkflowContext()

    result = engine.run(context)

    assert result.state == WorkflowState.COMPLETED
    assert result.results == []


def test_context_reset() -> None:
    context = WorkflowContext()
    context.state = WorkflowState.FAILED
    context.current_step = 2
    context.results.append("x")
    context.errors.append("err")

    context.reset()

    assert context.state == WorkflowState.PENDING
    assert context.current_step == 0
    assert context.results == []
    assert context.errors == []


def test_workflow_engine_cancel_method() -> None:
    engine = WorkflowEngine([_success_step("a")])
    context = WorkflowContext()

    result = engine.cancel(context)

    assert result.state == WorkflowState.CANCELLED
