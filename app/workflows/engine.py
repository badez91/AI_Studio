from __future__ import annotations

from typing import Any, Callable, Sequence

from app.workflows.state import WorkflowContext, WorkflowState


class Step:
    """Represents a single executable workflow step."""

    def __init__(self, name: str, handler: Callable[[WorkflowContext], Any]) -> None:
        self.name = name
        self.handler = handler

    def execute(self, context: WorkflowContext) -> Any:
        return self.handler(context)


class WorkflowEngine:
    """Executes a sequence of workflow steps and tracks state."""

    def __init__(self, steps: Sequence[Step]) -> None:
        self.steps = list(steps)

    def run(self, context: WorkflowContext) -> WorkflowContext:
        """Execute all steps sequentially and update the workflow context."""

        if context.state != WorkflowState.CANCELLED:
            context.state = WorkflowState.RUNNING
        for index, step in enumerate(self.steps):
            if context.state == WorkflowState.CANCELLED:
                break
            context.current_step = index
            try:
                result = step.execute(context)
                context.results.append(result)
            except Exception as exc:
                context.state = WorkflowState.FAILED
                context.errors.append(f"{step.name}: {exc}")
                break
        else:
            if context.state not in (WorkflowState.FAILED, WorkflowState.CANCELLED):
                context.state = WorkflowState.COMPLETED
        return context

    def cancel(self, context: WorkflowContext) -> WorkflowContext:
        """Cancel a running workflow."""

        context.state = WorkflowState.CANCELLED
        return context
