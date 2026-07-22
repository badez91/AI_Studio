from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResearchResult:
    """Structured output from a research agent."""

    topic: str
    summary: str
    sources: list[str] = field(default_factory=list)
    key_points: list[str] = field(default_factory=list)


class BaseAgent(ABC):
    """Abstract base class for AI Studio agents."""

    @abstractmethod
    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute the agent logic and return structured output."""
