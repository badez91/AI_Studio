from __future__ import annotations

from enum import Enum

import typer

from app.config.container import build_container
from app.config.logging import configure_logging
from app.workflows.engine import Step, WorkflowEngine
from app.workflows.state import WorkflowContext, WorkflowState

app = typer.Typer(add_completion=False, help="AI Studio CLI")


class _StateChoice(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


@app.callback()
def callback() -> None:
    pass


@app.command(name="status")
def status() -> None:
    """Show basic application status."""

    container = build_container()
    settings = container.resolve("settings")
    typer.echo(f"{settings.app_name} is ready in {settings.environment} mode")


@app.command(name="workflow-run")
def workflow_run(name: str) -> None:
    """Run a simple demo workflow."""

    container = build_container()
    settings = container.resolve("settings")
    configure_logging()

    def hello_step(context: WorkflowContext) -> str:
        return "hello"

    engine = WorkflowEngine([Step(name="hello", handler=hello_step)])
    context = WorkflowContext()
    result = engine.run(context)

    typer.echo(
        f"Workflow '{name}' executed with state={result.state.value} "
        f"results={result.results}"
    )


@app.command(name="workflow-status")
def workflow_status(workflow_id: str) -> None:
    """Show workflow status."""

    container = build_container()
    settings = container.resolve("settings")

    typer.echo(
        f"Requested status for workflow '{workflow_id}' on {settings.app_name}"
    )


@app.command(name="workflow-execute")
def workflow_execute(workflow_id: str) -> None:
    """Execute a workflow by ID."""

    container = build_container()
    settings = container.resolve("settings")
    configure_logging()

    def hello_step(context: WorkflowContext) -> str:
        return "hello"

    engine = WorkflowEngine([Step(name="hello", handler=hello_step)])
    context = WorkflowContext()
    result = engine.run(context)

    typer.echo(
        f"Workflow '{workflow_id}' executed with state={result.state.value} "
        f"results={result.results}"
    )


if __name__ == "__main__":
    app()