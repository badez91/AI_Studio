from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Track:
    """Represents a single track in a render plan."""

    kind: str
    asset_path: str
    start_seconds: float = 0.0
    duration_seconds: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RenderPlan:
    """Structured composition plan for assembling media assets."""

    output_path: str
    tracks: list[Track] = field(default_factory=list)
    total_duration_seconds: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class Composer:
    """Builds a render plan from available media assets."""

    def __init__(self, default_output: str = "output/final.mp4") -> None:
        self.default_output = default_output

    def compose(self, payload: dict[str, Any]) -> dict[str, Any]:
        assets = payload.get("assets", [])
        script = payload.get("script", {})

        if not assets:
            raise ValueError("No assets provided for composition.")

        tracks = self._build_tracks(assets, script)
        total_duration = self._calculate_duration(tracks, script)

        plan = RenderPlan(
            output_path=payload.get("output_path", self.default_output),
            tracks=tracks,
            total_duration_seconds=total_duration,
            metadata={
                "asset_count": len(assets),
                "track_count": len(tracks),
            },
        )
        return {
            "output_path": plan.output_path,
            "tracks": [
                {
                    "kind": t.kind,
                    "asset_path": t.asset_path,
                    "start_seconds": t.start_seconds,
                    "duration_seconds": t.duration_seconds,
                    "metadata": t.metadata,
                }
                for t in plan.tracks
            ],
            "total_duration_seconds": plan.total_duration_seconds,
            "metadata": plan.metadata,
        }

    def _build_tracks(self, assets: list[Any], script: Any) -> list[Track]:
        tracks: list[Track] = []
        current_time = 0.0

        for asset in assets:
            asset_dict = asset if isinstance(asset, dict) else asset.__dict__
            kind = asset_dict.get("kind", asset_dict.get("format", "unknown"))
            path = asset_dict.get("asset_path", "")
            duration = float(asset_dict.get("duration_seconds", 0))

            tracks.append(
                Track(
                    kind=kind,
                    asset_path=path,
                    start_seconds=current_time,
                    duration_seconds=duration,
                    metadata=asset_dict.get("metadata", {}),
                )
            )
            current_time += duration

        return tracks

    def _calculate_duration(self, tracks: list[Track], script: Any) -> float:
        if isinstance(script, dict) and script.get("total_duration_seconds"):
            return float(script["total_duration_seconds"])
        if not tracks:
            return 0.0
        last_track = tracks[-1]
        return last_track.start_seconds + last_track.duration_seconds
