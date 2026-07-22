from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScriptSection:
    """Represents a single section of a script outline."""

    title: str
    content: str
    duration_seconds: int = 0


@dataclass
class ScriptOutline:
    """Structured output from a script writer agent."""

    topic: str
    sections: list[ScriptSection] = field(default_factory=list)
    total_duration_seconds: int = 0


class ScriptWriterAgent:
    """Generates a structured script outline from validated research content."""

    def __init__(self, default_section_duration: int = 30) -> None:
        self.default_section_duration = default_section_duration

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        topic = payload.get("topic", "")
        summary = payload.get("summary", "")
        key_points = payload.get("key_points", [])

        if not topic:
            raise ValueError("Missing 'topic' in payload.")

        sections = self._build_sections(topic, summary, key_points)
        total_duration = sum(section.duration_seconds for section in sections)

        outline = ScriptOutline(
            topic=topic,
            sections=sections,
            total_duration_seconds=total_duration,
        )
        return outline.__dict__

    def _build_sections(
        self, topic: str, summary: str, key_points: list[str]
    ) -> list[ScriptSection]:
        sections: list[ScriptSection] = []

        sections.append(
            ScriptSection(
                title=f"Introduction: {topic}",
                content=summary or f"Introducing {topic}.",
                duration_seconds=self.default_section_duration,
            )
        )

        for index, point in enumerate(key_points, start=1):
            sections.append(
                ScriptSection(
                    title=f"Point {index}: {point}",
                    content=point,
                    duration_seconds=self.default_section_duration,
                )
            )

        sections.append(
            ScriptSection(
                title="Conclusion",
                content=f"Summary and final thoughts on {topic}.",
                duration_seconds=self.default_section_duration,
            )
        )

        return sections
