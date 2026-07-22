from __future__ import annotations

from pathlib import Path

import pytest

from app.agents.music import MusicArtifact, MusicAgent
from app.assets.asset_manager import AssetManager
from app.providers.base import Provider


class _StubProvider(Provider):
    def capabilities(self) -> list[str]:
        return ["music"]

    def invoke(self, capability: str, payload: dict[str, str]) -> dict[str, str]:
        return {"capability": capability, "provider": "stub", "output": "mocked"}


def _make_agent(tmp_path: Path) -> MusicAgent:
    return MusicAgent(
        provider=_StubProvider(),
        asset_manager=AssetManager(root=str(tmp_path)),
    )


def test_music_agent_generates_artifact(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    payload = {
        "mood": "calm",
        "duration_seconds": 120,
        "scene": "intro",
    }

    result = agent.run(payload)

    assert result["format"] == "mock-music"
    assert result["duration_seconds"] == 120
    assert result["mood"] == "calm"
    assert "intro" in result["asset_path"]
    assert result["metadata"]["scene"] == "intro"


def test_music_agent_registers_asset(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    payload = {"mood": "upbeat", "duration_seconds": 45, "scene": "scene-1"}

    agent.run(payload)

    asset_path = tmp_path / "audio" / "music" / "scene-1.txt"
    assert asset_path.exists()
    assert asset_path.read_text(encoding="utf-8") == "upbeat music for 45 seconds"


def test_music_agent_uses_defaults(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    payload = {"mood": "neutral"}

    result = agent.run(payload)

    assert result["asset_path"] == "audio/music/background.txt"
    assert result["metadata"]["scene"] == ""
    assert result["mood"] == "neutral"


def test_music_agent_metadata_contains_provider(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    payload = {"mood": "dramatic"}

    result = agent.run(payload)

    assert result["metadata"]["provider"] == "_StubProvider"


def test_music_artifact_metadata() -> None:
    artifact = MusicArtifact(
        asset_path="audio/music/test.txt",
        format="mp3",
        duration_seconds=90,
        mood="epic",
        metadata={"tempo": "fast"},
    )
    data = artifact.__dict__
    assert data["format"] == "mp3"
    assert data["mood"] == "epic"
    assert data["metadata"]["tempo"] == "fast"
