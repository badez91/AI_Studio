from __future__ import annotations

import pytest

from app.agents.script_writer import ScriptOutline, ScriptWriterAgent


def test_script_writer_generates_outline() -> None:
    agent = ScriptWriterAgent(default_section_duration=30)
    payload = {
        "topic": "AI",
        "summary": "AI is transforming industries.",
        "key_points": ["automation", "creativity"],
    }

    result = agent.run(payload)

    assert result["topic"] == "AI"
    assert len(result["sections"]) == 4
    assert result["total_duration_seconds"] == 120


def test_script_writer_sequence_ordering() -> None:
    agent = ScriptWriterAgent(default_section_duration=10)
    payload = {
        "topic": "Test",
        "summary": "Summary.",
        "key_points": ["first", "second", "third"],
    }

    result = agent.run(payload)
    sections = result["sections"]

    assert sections[0].title.startswith("Introduction:")
    assert sections[1].title == "Point 1: first"
    assert sections[2].title == "Point 2: second"
    assert sections[3].title == "Point 3: third"
    assert sections[4].title == "Conclusion"
    assert result["total_duration_seconds"] == 50


def test_script_writer_raises_on_missing_topic() -> None:
    agent = ScriptWriterAgent()
    with pytest.raises(ValueError):
        agent.run({"summary": "no topic"})


def test_script_writer_handles_empty_key_points() -> None:
    agent = ScriptWriterAgent(default_section_duration=20)
    payload = {
        "topic": "Solo Topic",
        "summary": "Only intro and conclusion.",
        "key_points": [],
    }

    result = agent.run(payload)
    assert len(result["sections"]) == 2
    assert result["total_duration_seconds"] == 40


def test_script_writer_custom_duration() -> None:
    agent = ScriptWriterAgent(default_section_duration=60)
    payload = {
        "topic": "Long",
        "summary": "Summary.",
        "key_points": ["point"],
    }

    result = agent.run(payload)
    assert result["total_duration_seconds"] == 180
    assert result["sections"][0].duration_seconds == 60
