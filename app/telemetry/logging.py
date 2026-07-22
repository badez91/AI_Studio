from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TelemetryEvent:
    """Structured telemetry event for workflow execution."""

    workflow_id: str
    step: str
    state: str
    duration_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)
