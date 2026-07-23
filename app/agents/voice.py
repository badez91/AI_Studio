from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.agents.base import AudioAsset, BaseAgent
from app.assets.asset_manager import AssetManager
from app.providers.base import Provider


@dataclass
class VoiceArtifact(AudioAsset):
    """Represents a generated voice artifact."""

    kind: str = "voice"


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

        provider_name = self.provider.__class__.__name__ if self.provider else "none"
        asset_path = f"audio/{scene or 'narration'}.txt"
        absolute_path = str(self.asset_manager.root / asset_path)

        artifact = VoiceArtifact(
            asset_path=asset_path,
            path=absolute_path,
            format="mock-audio",
            mime_type="audio/wav",
            duration_seconds=duration,
            duration=float(duration),
            provider=provider_name,
            metadata={
                "scene": scene,
                "provider": provider_name,
            },
        )

        self.asset_manager.write(artifact.asset_path, script)

        return artifact.__dict__
