from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.agents.base import BaseAgent
from app.assets.asset_manager import AssetManager
from app.providers.base import Provider


@dataclass
class MusicArtifact:
    """Represents a generated music or atmosphere artifact."""

    asset_path: str
    format: str
    duration_seconds: int
    mood: str
    metadata: dict[str, Any] = field(default_factory=dict)


class MusicAgent:
    """Provides background music and atmosphere generation for media projects."""

    def __init__(
        self,
        provider: Provider | None = None,
        asset_manager: AssetManager | None = None,
    ) -> None:
        self.provider = provider
        self.asset_manager = asset_manager or AssetManager()

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        mood = payload.get("mood", "neutral")
        duration = payload.get("duration_seconds", 60)
        scene = payload.get("scene", "")

        artifact = MusicArtifact(
            asset_path=f"audio/music/{scene or 'background'}.txt",
            format="mock-music",
            duration_seconds=duration,
            mood=mood,
            metadata={
                "scene": scene,
                "provider": self.provider.__class__.__name__
                if self.provider
                else "none",
            },
        )

        self.asset_manager.write(
            artifact.asset_path,
            f"{mood} music for {duration} seconds",
        )

        return artifact.__dict__
