from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class MediaAsset:
    """Standardized media asset contract for all generated content."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    asset_type: str = "generic"
    provider: str = ""
    path: str = ""
    mime_type: str = ""
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    sample_rate: Optional[int] = None
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    # Backward compatibility aliases
    asset_path: str = ""
    format: str = ""
    duration_seconds: Optional[float] = None

    def __post_init__(self) -> None:
        if self.asset_path and not self.path:
            self.path = self.asset_path
        if self.path and not self.asset_path:
            self.asset_path = self.path
        if self.format and not self.mime_type:
            self.mime_type = self.format
        if self.mime_type and not self.format:
            self.format = self.mime_type
        if self.duration is None and self.duration_seconds is not None:
            self.duration = self.duration_seconds
        if self.duration_seconds is None and self.duration is not None:
            self.duration_seconds = self.duration


@dataclass
class ImageAsset(MediaAsset):
    """Represents a generated image asset."""

    kind: str = "image"
    asset_type: str = "image"
    mime_type: str = "image/png"
    format: str = "image/png"


@dataclass
class AudioAsset(MediaAsset):
    """Represents a generated audio asset."""

    kind: str = "audio"
    asset_type: str = "audio"
    mime_type: str = "audio/wav"
    format: str = "audio/wav"
    sample_rate: int = 44100


@dataclass
class VideoAsset(MediaAsset):
    """Represents a generated video asset."""

    kind: str = "video"
    asset_type: str = "video"
    mime_type: str = "video/mp4"
    format: str = "video/mp4"
    width: int = 1920
    height: int = 1080


@dataclass
class ResearchResult:
    """Structured output from a research agent."""

    topic: str
    summary: str
    sources: list[str] = field(default_factory=list)
    key_points: list[str] = field(default_factory=list)


class BaseAgent(ABC):
    """Abstract base class for AI Studio agents."""

    @abstractmethod
    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute the agent logic and return structured output."""
