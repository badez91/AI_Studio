from __future__ import annotations

import pytest

from app.agents.fact_check import FactCheckAgent


def test_fact_check_passes_valid_research() -> None:
    agent = FactCheckAgent(min_score=0.7)
    payload = {
        "topic": "AI",
        "summary": "Artificial intelligence is transforming many industries worldwide.",
        "sources": ["source-a", "source-b"],
        "key_points": ["point-1", "point-2"],
    }

    result = agent.run(payload)

    assert result["passed"] is True
    assert result["score"] == 1.0
    assert result["issues"] == []
    assert result["suggestions"] == []


def test_fact_check_flags_missing_fields() -> None:
    agent = FactCheckAgent(min_score=0.7)
    payload = {
        "topic": "",
        "summary": "",
        "sources": [],
        "key_points": [],
    }

    result = agent.run(payload)

    assert result["passed"] is False
    assert result["score"] < 0.7
    assert len(result["issues"]) >= 4
    assert "Missing topic." in result["issues"]
    assert "Missing summary." in result["issues"]
    assert "No sources provided." in result["issues"]
    assert "No key points provided." in result["issues"]


def test_fact_check_suggests_improvements() -> None:
    agent = FactCheckAgent(min_score=0.7)
    payload = {
        "topic": "AI",
        "summary": "Short text.",
        "sources": ["only-one"],
        "key_points": [],
    }

    result = agent.run(payload)

    assert result["passed"] is False
    assert "Summary is too short." in result["issues"]
    assert "Provide a more detailed summary." in result["suggestions"]
    assert "Fewer than two sources." in result["issues"]
    assert "Add more sources for better verification." in result["suggestions"]


def test_fact_check_deterministic_output() -> None:
    agent = FactCheckAgent(min_score=0.7)
    payload = {
        "topic": "",
        "summary": "",
        "sources": [],
        "key_points": [],
    }

    first = agent.run(payload)
    second = agent.run(payload)

    assert first == second


def test_fact_check_custom_threshold() -> None:
    agent = FactCheckAgent(min_score=0.5)
    payload = {
        "topic": "AI",
        "summary": "Short.",
        "sources": ["source"],
        "key_points": [],
    }

    result = agent.run(payload)
    assert result["score"] == pytest.approx(0.4)
    assert result["passed"] is False
