from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FactCheckResult:
    """Structured output from a fact-check agent."""

    passed: bool
    score: float
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


class FactCheckAgent:
    """Validates research output for consistency and completeness."""

    def __init__(self, min_score: float = 0.7) -> None:
        self.min_score = min_score

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        topic = payload.get("topic", "")
        summary = payload.get("summary", "")
        sources = payload.get("sources", [])
        key_points = payload.get("key_points", [])

        issues: list[str] = []
        suggestions: list[str] = []

        if not topic:
            issues.append("Missing topic.")
        if not summary:
            issues.append("Missing summary.")
        if len(sources) == 0:
            issues.append("No sources provided.")
        if len(key_points) == 0:
            issues.append("No key points provided.")

        if len(summary.split()) < 5:
            issues.append("Summary is too short.")
            suggestions.append("Provide a more detailed summary.")

        if len(sources) < 2:
            issues.append("Fewer than two sources.")
            suggestions.append("Add more sources for better verification.")

        score = self._calculate_score(issues)
        passed = score >= self.min_score and len(issues) == 0

        result = FactCheckResult(
            passed=passed,
            score=score,
            issues=issues,
            suggestions=suggestions,
        )
        return result.__dict__

    def _calculate_score(self, issues: list[str]) -> float:
        if not issues:
            return 1.0
        penalty = len(issues) * 0.2
        return max(0.0, 1.0 - penalty)
