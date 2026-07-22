from __future__ import annotations

from typing import Any


def format_evaluation(payload: dict[str, Any]) -> str:
    """Format evaluation output for logging or reporting."""

    lines = [f"Evaluation for {payload.get('workflow_id', 'unknown')}:"]
    for key, value in payload.items():
        if key != "workflow_id":
            lines.append(f"  {key}: {value}")
    return "\n".join(lines)


def score_workflow(context: dict[str, Any]) -> dict[str, Any]:
    """Return simple evaluation scores for a workflow context."""

    return {
        "completeness": 1.0 if context.get("state") == "completed" else 0.0,
        "step_count": len(context.get("results", [])),
        "error_count": len(context.get("errors", [])),
    }


def format_review(review: dict[str, Any]) -> str:
    """Format review output for logging or reporting."""

    status = "PASSED" if review.get("passed") else "FAILED"
    lines = [f"Review {status} with score={review.get('score', 0.0):.2f}"]
    issues = review.get("issues", [])
    if issues:
        lines.append("Issues:")
        for issue in issues:
            lines.append(f"  - {issue}")
    suggestions = review.get("suggestions", [])
    if suggestions:
        lines.append("Suggestions:")
        for suggestion in suggestions:
            lines.append(f"  - {suggestion}")
    return "\n".join(lines)


def score_review(review: dict[str, Any]) -> float:
    """Return the numeric score from a review result."""

    return float(review.get("score", 0.0))
