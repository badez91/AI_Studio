from __future__ import annotations

from typing import Any

import pytest

from app.services.composer import Composer, RenderPlan, Track


def _make_assets() -> list[dict[str, Any]]:
    return [
        {
            "kind": "image",
            "asset_path": "images/scene-1.txt",
            "duration_seconds": 30,
            "metadata": {"scene": "scene-1"},
        },
        {
            "kind": "voice",
            "asset_path": "audio/narration.txt",
            "duration_seconds": 25,
            "metadata": {"scene": "scene-1"},
        },
        {
            "kind": "music",
            "asset_path": "audio/music/background.txt",
            "duration_seconds": 55,
            "metadata": {"mood": "calm"},
        },
    ]


def test_composer_builds_render_plan() -> None:
    composer = Composer()
    payload = {
        "assets": _make_assets(),
        "script": {"topic": "Test"},
    }

    result = composer.compose(payload)

    assert result["output_path"] == "output/final.mp4"
    assert len(result["tracks"]) == 3
    assert result["total_duration_seconds"] == 110.0
    assert result["metadata"]["asset_count"] == 3
    assert result["metadata"]["track_count"] == 3


def test_composer_track_ordering() -> None:
    composer = Composer()
    assets = _make_assets()
    payload = {"assets": assets}

    result = composer.compose(payload)
    tracks = result["tracks"]

    assert tracks[0]["start_seconds"] == 0.0
    assert tracks[0]["kind"] == "image"
    assert tracks[1]["start_seconds"] == 30.0
    assert tracks[1]["kind"] == "voice"
    assert tracks[2]["start_seconds"] == 55.0
    assert tracks[2]["kind"] == "music"


def test_composer_raises_on_empty_assets() -> None:
    composer = Composer()
    with pytest.raises(ValueError):
        composer.compose({"assets": []})


def test_composer_uses_custom_output_path() -> None:
    composer = Composer()
    payload = {
        "assets": _make_assets(),
        "output_path": "output/custom.mp4",
    }

    result = composer.compose(payload)
    assert result["output_path"] == "output/custom.mp4"


def test_composer_handles_script_duration() -> None:
    composer = Composer()
    assets = _make_assets()
    payload = {"assets": assets, "script": {"total_duration_seconds": 120}}

    result = composer.compose(payload)
    assert result["total_duration_seconds"] == 120.0


def test_render_plan_dataclass() -> None:
    plan = RenderPlan(
        output_path="output/test.mp4",
        tracks=[
            Track(kind="image", asset_path="img.txt", start_seconds=0.0, duration_seconds=10.0)
        ],
        total_duration_seconds=10.0,
    )
    data = plan.__dict__
    assert data["output_path"] == "output/test.mp4"
    assert len(data["tracks"]) == 1
    assert data["tracks"][0].kind == "image"
