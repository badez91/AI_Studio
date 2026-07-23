from __future__ import annotations

import pytest

from app.agents.script_writer import ScriptSection
from app.agents.storyboard import StoryboardAgent


def _make_sections() -> list[dict[str, Any]]:
    return [
        {"title": "Intro", "content": "Welcome", "duration_seconds": 30},
        {"title": "Body", "content": "Main content", "duration_seconds": 60},
        {"title": "Outro", "content": "Goodbye", "duration_seconds": 20},
    ]


def test_storyboard_generates_scenes() -> None:
    agent = StoryboardAgent()
    payload = {"topic": "Demo", "sections": _make_sections()}

    result = agent.run(payload)

    assert result["topic"] == "Demo"
    assert len(result["scenes"]) == 3
    assert result["total_duration_seconds"] == 110


def test_storyboard_scene_ordering() -> None:
    agent = StoryboardAgent()
    payload = {"topic": "Demo", "sections": _make_sections()}

    result = agent.run(payload)
    scenes = result["scenes"]

    assert scenes[0]["scene_number"] == 1
    assert scenes[0]["title"] == "Intro"
    assert scenes[1]["scene_number"] == 2
    assert scenes[1]["title"] == "Body"
    assert scenes[2]["scene_number"] == 3
    assert scenes[2]["title"] == "Outro"


def test_storyboard_raises_on_missing_topic() -> None:
    agent = StoryboardAgent()
    with pytest.raises(ValueError):
        agent.run({"sections": _make_sections()})


def test_storyboard_handles_empty_sections() -> None:
    agent = StoryboardAgent()
    payload = {"topic": "Empty", "sections": []}

    result = agent.run(payload)
    assert result["scenes"] == []
    assert result["total_duration_seconds"] == 0


def test_storyboard_nested_scene_data() -> None:
    agent = StoryboardAgent()
    sections = [
        ScriptSection(title="Intro", content="Welcome", duration_seconds=10),
        ScriptSection(title="Demo", content="Showcase", duration_seconds=20),
    ]
    payload = {"topic": "Nested", "sections": sections}

    result = agent.run(payload)
    scene = result["scenes"][0]

    assert scene["scene_number"] == 1
    assert scene["title"] == "Intro"
    assert scene["description"] == "Welcome"
    assert scene["duration_seconds"] == 10
    assert "Intro" in scene["prompt"]
