from __future__ import annotations

import json
from typing import Any

from app.agents.base import BaseAgent, ResearchResult
from app.providers.base import Provider


RESEARCH_SYSTEM_PROMPT = """You are a research assistant. Given a topic, provide structured research output.

You MUST respond with valid JSON in exactly this format:
{
  "summary": "A 2-3 sentence summary of the topic",
  "sources": ["source 1 description", "source 2 description"],
  "key_points": ["key point 1", "key point 2", "key point 3"]
}

Provide real, accurate information. Include 2-4 sources and 3-5 key points.
Respond ONLY with the JSON object, no other text."""


class ResearchAgent(BaseAgent):
    """Agent that gathers structured context for a workflow input."""

    def __init__(self, provider: Provider) -> None:
        self.provider = provider

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        topic = payload.get("topic", "")
        if not topic:
            raise ValueError("Missing 'topic' in payload.")

        response = self.provider.invoke(
            "chat",
            {
                "system": RESEARCH_SYSTEM_PROMPT,
                "prompt": f"Research this topic thoroughly: {topic}",
            },
        )

        output = response.get("output", "")
        result = self._parse_response(topic, output)
        return result.__dict__

    def _parse_response(self, topic: str, output: str) -> ResearchResult:
        """Parse LLM output into structured ResearchResult."""
        try:
            # Try to extract JSON from the response
            text = output.strip()
            # Handle markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            data = json.loads(text)
            return ResearchResult(
                topic=topic,
                summary=data.get("summary", output[:200]),
                sources=data.get("sources", []),
                key_points=data.get("key_points", []),
            )
        except (json.JSONDecodeError, IndexError, KeyError):
            # Fallback: use raw output as summary
            return ResearchResult(
                topic=topic,
                summary=output[:500] if output else f"Research on {topic}",
                sources=["llm-generated"],
                key_points=self._extract_points(output),
            )

    def _extract_points(self, text: str) -> list[str]:
        """Extract bullet points or sentences as key points."""
        if not text:
            return ["No key points generated"]
        lines = [l.strip().lstrip("•-*1234567890.") .strip() for l in text.split("\n") if l.strip()]
        points = [l for l in lines if 10 < len(l) < 200]
        return points[:5] if points else [text[:100]]
