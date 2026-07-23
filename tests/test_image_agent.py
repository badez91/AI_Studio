from __future__ import annotations

from pathlib import Path

import pytest

from app.agents.image import ImageArtifact, ImageGenerationAgent
from app.assets.asset_manager import AssetManager
from app.providers.base import Provider


class _StubProvider(Provider):
    def capabilities(self) -> list[str]:
        return ["image"]

    def invoke(self, capability: str, payload: dict[str, str]) -> dict[str, str]:
        return {"capability": capability, "provider": "stub", "output": "mocked"}


def _make_agent(tmp_path: Path) -> ImageGenerationAgent:
    return ImageGenerationAgent(
        provider=_StubProvider(),
        asset_manager=AssetManager(root=str(tmp_path)),
    )


def test_image_agent_generates_artifact(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    payload = {
        "prompt": "A sunset over the ocean",
        "scene": "intro",
        "width": 1024,
        "height": 768,
    }

    result = agent.run(payload)

    assert result["kind"] == "image"
    assert result["format"] == "mock-image"
    assert result["width"] == 1024
    assert result["height"] == 768
    assert "intro" in result["asset_path"]
    assert result["metadata"]["scene"] == "intro"


def test_image_agent_registers_asset(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    payload = {"prompt": "A mountain landscape", "scene": "scene-1"}

    agent.run(payload)

    asset_path = tmp_path / "images" / "scene-1.txt"
    assert asset_path.exists()
    assert asset_path.read_text(encoding="utf-8") == "A mountain landscape"


def test_image_agent_uses_default_scene(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    payload = {"prompt": "Default image"}

    result = agent.run(payload)

    assert result["asset_path"] == "images/scene.txt"
    assert result["metadata"]["scene"] == ""
    assert result["width"] == 1024
    assert result["height"] == 1024


def test_image_agent_raises_on_missing_prompt(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    with pytest.raises(ValueError):
        agent.run({"scene": "intro"})


def test_image_artifact_metadata() -> None:
    artifact = ImageArtifact(
        asset_path="images/test.txt",
        format="png",
        width=512,
        height=512,
        metadata={"style": "realistic"},
    )
    data = artifact.__dict__
    assert data["format"] == "png"
    assert data["width"] == 512
    assert data["metadata"]["style"] == "realistic"
