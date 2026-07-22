from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class WorkflowState(str, Enum):
    """Possible states for a workflow execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowContext:
    """Tracks the state and results of a workflow execution."""

    state: WorkflowState = WorkflowState.PENDING
    current_step: int = 0
    results: list[Any] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def reset(self) -> None:
        self.state = WorkflowState.PENDING
        self.current_step = 0
        self.results.clear()
        self.errors.clear()
