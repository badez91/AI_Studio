from __future__ import annotations

from pathlib import Path

import pytest

from app.agents.voice import VoiceArtifact, VoiceGenerationAgent
from app.assets.asset_manager import AssetManager
from app.providers.base import Provider


class _StubProvider(Provider):
    def capabilities(self) -> list[str]:
        return ["voice"]

    def invoke(self, capability: str, payload: dict[str, str]) -> dict[str, str]:
        return {"capability": capability, "provider": "stub", "output": "mocked"}


def _make_agent(tmp_path: Path) -> VoiceGenerationAgent:
    return VoiceGenerationAgent(
        provider=_StubProvider(),
        asset_manager=AssetManager(root=str(tmp_path)),
    )


def test_voice_agent_generates_artifact(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    payload = {
        "script": "Hello world",
        "scene": "intro",
        "duration_seconds": 15,
    }

    result = agent.run(payload)

    assert result["format"] == "mock-audio"
    assert result["duration_seconds"] == 15
    assert "intro" in result["asset_path"]
    assert result["metadata"]["scene"] == "intro"


def test_voice_agent_registers_asset(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    payload = {"script": "Audio content", "scene": "scene-1"}

    agent.run(payload)

    asset_path = tmp_path / "audio" / "scene-1.txt"
    assert asset_path.exists()
    assert asset_path.read_text(encoding="utf-8") == "Audio content"


def test_voice_agent_uses_default_scene(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    payload = {"script": "Default narration"}

    result = agent.run(payload)

    assert result["asset_path"] == "audio/narration.txt"
    assert result["metadata"]["scene"] == ""


def test_voice_agent_raises_on_missing_script(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    with pytest.raises(ValueError):
        agent.run({"scene": "intro"})


def test_voice_artifact_metadata() -> None:
    artifact = VoiceArtifact(
        asset_path="audio/test.txt",
        format="wav",
        duration_seconds=60,
        metadata={"sample_rate": 44100},
    )
    data = artifact.__dict__
    assert data["format"] == "wav"
    assert data["metadata"]["sample_rate"] == 44100
