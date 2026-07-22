from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReviewResult:
    """Structured output from a reviewer agent."""

    passed: bool
    score: float
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


class ReviewerAgent:
    """Evaluates output completeness, structure, and consistency."""

    def __init__(self, min_score: float = 0.8) -> None:
        self.min_score = min_score

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        issues: list[str] = []
        suggestions: list[str] = []
        metrics: dict[str, Any] = {}

        research = payload.get("research", {})
        script = payload.get("script", {})
        storyboard = payload.get("storyboard", {})
        assets = payload.get("assets", [])

        metrics["has_research"] = bool(research)
        metrics["has_script"] = bool(script)
        metrics["has_storyboard"] = bool(storyboard)
        metrics["asset_count"] = len(assets)

        if not research:
            issues.append("Missing research output.")
            suggestions.append("Run the research agent before review.")

        if research:
            topic = research.get("topic", "")
            summary = research.get("summary", "")
            sources = research.get("sources", [])
            key_points = research.get("key_points", [])

            if not topic:
                issues.append("Research is missing topic.")
            if not summary:
                issues.append("Research is missing summary.")
            if len(sources) == 0:
                issues.append("Research has no sources.")
            if len(key_points) == 0:
                issues.append("Research has no key points.")

        if not script:
            issues.append("Missing script output.")
            suggestions.append("Run the script writer agent before review.")
        else:
            sections = script.get("sections", [])
            if not sections:
                issues.append("Script has no sections.")
            else:
                for index, section in enumerate(sections):
                    title = section.get("title", "") if isinstance(section, dict) else getattr(section, "title", "")
                    duration = section.get("duration_seconds", 0) if isinstance(section, dict) else getattr(section, "duration_seconds", 0)
                    if not title:
                        issues.append(f"Script section {index + 1} is missing a title.")
                    if duration <= 0:
                        issues.append(f"Script section {index + 1} has invalid duration.")

        if not storyboard:
            issues.append("Missing storyboard output.")
            suggestions.append("Run the storyboard agent before review.")
        else:
            scenes = storyboard.get("scenes", [])
            script_sections = script.get("sections", [])
            if len(scenes) != len(script_sections):
                issues.append(
                    f"Storyboard scene count ({len(scenes)}) does not match script sections ({len(script_sections)})."
                )
            for index, scene in enumerate(scenes):
                title = scene.get("title", "") if isinstance(scene, dict) else getattr(scene, "title", "")
                if not title:
                    issues.append(f"Storyboard scene {index + 1} is missing a title.")

        if not assets:
            issues.append("No assets generated.")
            suggestions.append("Generate media assets before final review.")

        score = self._calculate_score(issues, metrics)
        passed = score >= self.min_score and len(issues) == 0

        result = ReviewResult(
            passed=passed,
            score=score,
            issues=issues,
            suggestions=suggestions,
            metrics=metrics,
        )
        return result.__dict__

    def _calculate_score(self, issues: list[str], metrics: dict[str, Any]) -> float:
        if not issues:
            return 1.0
        penalty = len(issues) * 0.15
        missing_section_penalty = sum(
            0.1 for key in ["has_research", "has_script", "has_storyboard"] if not metrics.get(key)
        )
        return max(0.0, 1.0 - penalty - missing_section_penalty)
