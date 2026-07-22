from __future__ import annotations

from typing import Any

import pytest

from app.agents.reviewer import ReviewResult, ReviewerAgent
from app.evaluation.metrics import format_review, score_review


def _make_payload(
    research: dict[str, Any] | None = None,
    script: dict[str, Any] | None = None,
    storyboard: dict[str, Any] | None = None,
    assets: list[Any] | None = None,
) -> dict[str, Any]:
    return {
        "research": research or {},
        "script": script or {},
        "storyboard": storyboard or {},
        "assets": assets or [],
    }


def test_reviewer_passes_complete_output() -> None:
    agent = ReviewerAgent(min_score=0.8)
    payload = _make_payload(
        research={
            "topic": "AI",
            "summary": "Artificial intelligence is transforming industries.",
            "sources": ["a", "b"],
            "key_points": ["1", "2"],
        },
        script={
            "sections": [
                {"title": "Intro", "content": "Welcome", "duration_seconds": 30},
                {"title": "Body", "content": "Main", "duration_seconds": 60},
            ]
        },
        storyboard={
            "scenes": [
                {"title": "Intro", "description": "Welcome", "duration_seconds": 30},
                {"title": "Body", "description": "Main", "duration_seconds": 60},
            ]
        },
        assets=[{"kind": "image", "asset_path": "img.txt", "duration_seconds": 30}],
    )

    result = agent.run(payload)

    assert result["passed"] is True
    assert result["score"] == 1.0
    assert result["issues"] == []
    assert result["suggestions"] == []


def test_reviewer_flags_missing_sections() -> None:
    agent = ReviewerAgent(min_score=0.8)
    payload = _make_payload()

    result = agent.run(payload)

    assert result["passed"] is False
    assert result["score"] < 0.8
    assert "Missing research output." in result["issues"]
    assert "Missing script output." in result["issues"]
    assert "Missing storyboard output." in result["issues"]
    assert "No assets generated." in result["issues"]


def test_reviewer_validates_script_sections() -> None:
    agent = ReviewerAgent(min_score=0.8)
    payload = _make_payload(
        research={
            "topic": "AI",
            "summary": "Summary.",
            "sources": ["a"],
            "key_points": ["1"],
        },
        script={"sections": [{"title": "", "content": "Welcome", "duration_seconds": 0}]},
        storyboard={"scenes": [{"title": "Intro", "description": "Welcome", "duration_seconds": 30}]},
        assets=[],
    )

    result = agent.run(payload)

    assert "Script section 1 is missing a title." in result["issues"]
    assert "Script section 1 has invalid duration." in result["issues"]


def test_reviewer_validates_storyboard_consistency() -> None:
    agent = ReviewerAgent(min_score=0.8)
    payload = _make_payload(
        research={
            "topic": "AI",
            "summary": "Summary.",
            "sources": ["a"],
            "key_points": ["1"],
        },
        script={
            "sections": [
                {"title": "Intro", "content": "Welcome", "duration_seconds": 30},
                {"title": "Body", "content": "Main", "duration_seconds": 60},
            ]
        },
        storyboard={"scenes": [{"title": "Intro", "description": "Welcome", "duration_seconds": 30}]},
        assets=[],
    )

    result = agent.run(payload)

    assert "Storyboard scene count (1) does not match script sections (2)." in result["issues"]


def test_reviewer_deterministic_output() -> None:
    agent = ReviewerAgent(min_score=0.8)
    payload = _make_payload(
        research={"topic": "", "summary": "", "sources": [], "key_points": []},
        script={"sections": []},
        storyboard={"scenes": []},
        assets=[],
    )

    first = agent.run(payload)
    second = agent.run(payload)

    assert first == second


def test_format_review_output() -> None:
    review = {
        "passed": False,
        "score": 0.6,
        "issues": ["Missing research."],
        "suggestions": ["Run research agent."],
    }
    output = format_review(review)
    assert "FAILED" in output
    assert "Missing research." in output
    assert "Run research agent." in output


def test_score_review() -> None:
    review = {"passed": True, "score": 0.95}
    assert score_review(review) == pytest.approx(0.95)
