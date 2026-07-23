from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent, ImageAsset, ImageAsset
from app.assets.asset_manager import AssetManager
from app.providers.base import Provider


class ImageArtifact(ImageAsset):
    """Represents a generated image artifact."""

    kind: str = "image"


class ImageGenerationAgent:
    """Provider-agnostic image generation abstraction for scene visuals."""

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

        provider_name = self.provider.__class__.__name__ if self.provider else "none"
        asset_path = f"images/{scene or 'scene'}.png"
        absolute_path = str(self.asset_manager.root / asset_path)

        artifact = ImageAsset(
            asset_path=asset_path,
            path=absolute_path,
            format="image/png",
            mime_type="image/png",
            width=width,
            height=height,
            provider=provider_name,
            metadata={
                "scene": scene,
                "provider": provider_name,
                "prompt": prompt,
            },
        )

        return artifact.__dict__
