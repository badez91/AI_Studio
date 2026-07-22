from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.agents.base import BaseAgent
from app.assets.asset_manager import AssetManager
from app.providers.base import Provider


@dataclass
class VoiceArtifact:
    """Represents a generated voice artifact."""

    asset_path: str
    format: str
    duration_seconds: int
    metadata: dict[str, Any] = field(default_factory=dict)


class VoiceGenerationAgent:
    """Provider-agnostic voice generation abstraction for narration assets."""

    def __init__(
        self,
        provider: Provider | None = None,
        asset_manager: AssetManager | None = None,
    ) -> None:
        self.provider = provider
        self.asset_manager = asset_manager or AssetManager()

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        script = payload.get("script", "")
        scene = payload.get("scene", "")
        duration = payload.get("duration_seconds", 30)

        if not script:
            raise ValueError("Missing 'script' in payload.")

        artifact = VoiceArtifact(
            asset_path=f"audio/{scene or 'narration'}.txt",
            format="mock-audio",
            duration_seconds=duration,
            metadata={
                "scene": scene,
                "provider": self.provider.__class__.__name__
                if self.provider
                else "none",
            },
        )

        self.asset_manager.write(artifact.asset_path, script)

        return artifact.__dict__
