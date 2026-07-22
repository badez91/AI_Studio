from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.agents.base import BaseAgent
from app.assets.asset_manager import AssetManager
from app.providers.base import Provider


@dataclass
class ImageArtifact:
    """Represents a generated image artifact."""

    asset_path: str
    format: str
    width: int
    height: int
    metadata: dict[str, Any] = field(default_factory=dict)


class ImageGenerationAgent:
    """Supports image generation for storyboard-driven visuals."""

    def __init__(
        self,
        provider: Provider | None = None,
        asset_manager: AssetManager | None = None,
    ) -> None:
        self.provider = provider
        self.asset_manager = asset_manager or AssetManager()

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        prompt = payload.get("prompt", "")
        scene = payload.get("scene", "")
        width = payload.get("width", 1024)
        height = payload.get("height", 1024)

        if not prompt:
            raise ValueError("Missing 'prompt' in payload.")

        artifact = ImageArtifact(
            asset_path=f"images/{scene or 'scene'}.txt",
            format="mock-image",
            width=width,
            height=height,
            metadata={
                "scene": scene,
                "provider": self.provider.__class__.__name__
                if self.provider
                else "none",
            },
        )

        self.asset_manager.write(artifact.asset_path, prompt)

        return artifact.__dict__
