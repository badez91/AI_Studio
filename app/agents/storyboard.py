from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StoryboardEntry:
    """Represents a single scene in a storyboard."""

    scene_number: int
    title: str
    description: str
    duration_seconds: int = 0
    prompt: str = ""


@dataclass
class Storyboard:
    """Structured output from a storyboard agent."""

    topic: str
    scenes: list[StoryboardEntry] = field(default_factory=list)
    total_duration_seconds: int = 0


class StoryboardAgent:
    """Translates script structure into visual planning data."""

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        topic = payload.get("topic", "")
        sections = payload.get("sections", [])

        if not topic:
            raise ValueError("Missing 'topic' in payload.")

        scenes = self._build_scenes(topic, sections)
        total_duration = sum(scene.duration_seconds for scene in scenes)

        storyboard = Storyboard(
            topic=topic,
            scenes=scenes,
            total_duration_seconds=total_duration,
        )
        return storyboard.__dict__

    def _build_scenes(self, topic: str, sections: list[Any]) -> list[StoryboardEntry]:
        scenes: list[StoryboardEntry] = []

        for index, section in enumerate(sections, start=1):
            if isinstance(section, dict):
                title = section.get("title", "")
                content = section.get("content", "")
                duration = section.get("duration_seconds", 30)
            else:
                title = getattr(section, "title", "")
                content = getattr(section, "content", "")
                duration = getattr(section, "duration_seconds", 30)

            scenes.append(
                StoryboardEntry(
                    scene_number=index,
                    title=title,
                    description=content,
                    duration_seconds=duration,
                    prompt=f"Visual scene for: {title}",
                )
            )

        return scenes
