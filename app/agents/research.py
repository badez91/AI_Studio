from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent, ResearchResult
from app.providers.base import Provider


class ResearchAgent(BaseAgent):
    """Agent that gathers structured context for a workflow input."""

    def __init__(self, provider: Provider) -> None:
        self.provider = provider

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        topic = payload.get("topic", "")
        if not topic:
            raise ValueError("Missing 'topic' in payload.")

        response = self.provider.invoke(
            "text",
            {"prompt": f"Research the topic: {topic}"},
        )

        output = response.get("output", "")
        result = ResearchResult(
            topic=topic,
            summary=output,
            sources=["mock-source"],
            key_points=["key-point-1", "key-point-2"],
        )
        return result.__dict__
