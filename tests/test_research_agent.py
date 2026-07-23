from __future__ import annotations

import pytest

from app.agents.base import ResearchResult
from app.agents.research import ResearchAgent
from app.providers.mock import MockTextProvider


def test_research_agent_returns_structured_output() -> None:
    agent = ResearchAgent(provider=MockTextProvider())
    result = agent.run({"topic": "AI"})

    assert result["topic"] == "AI"
    assert isinstance(result["summary"], str)
    assert len(result["summary"]) > 0
    assert isinstance(result["sources"], list)
    assert isinstance(result["key_points"], list)


def test_research_agent_raises_on_missing_topic() -> None:
    agent = ResearchAgent(provider=MockTextProvider())
    with pytest.raises(ValueError):
        agent.run({})


def test_research_result_schema() -> None:
    result = ResearchResult(
        topic="test",
        summary="summary text",
        sources=["a"],
        key_points=["1", "2"],
    )
    data = result.__dict__
    assert data["topic"] == "test"
    assert data["sources"] == ["a"]
    assert data["key_points"] == ["1", "2"]
