from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.agents.base import AudioAsset, MediaAsset
from app.assets.asset_manager import AssetManager
from app.providers.base import Provider


@dataclass
class MusicArtifact(AudioAsset):
    """Represents a generated music or atmosphere artifact."""

    kind: str = "music"
    mood: str = ""


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

        provider_name = self.provider.__class__.__name__ if self.provider else "none"
        asset_path = f"audio/music/{scene or 'background'}.txt"
        absolute_path = str(self.asset_manager.root / asset_path)

        artifact = MusicArtifact(
            asset_path=asset_path,
            path=absolute_path,
            format="mock-music",
            mime_type="audio/wav",
            duration_seconds=duration,
            duration=float(duration),
            sample_rate=44100,
            mood=mood,
            provider=provider_name,
            metadata={
                "scene": scene,
                "provider": provider_name,
                "mood": mood,
            },
        )

        self.asset_manager.write(artifact.asset_path, f"{mood} music for {duration} seconds")

        return artifact.__dict__
