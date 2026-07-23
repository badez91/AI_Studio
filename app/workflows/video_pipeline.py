"""Video generation pipeline — chains all 9 agents into workflow steps."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from app.agents.fact_check import FactCheckAgent
from app.agents.music import MusicAgent
from app.agents.research import ResearchAgent
from app.agents.reviewer import ReviewerAgent
from app.agents.script_writer import ScriptWriterAgent
from app.agents.storyboard import StoryboardAgent
from app.assets.asset_manager import AssetManager
from app.providers.base import Provider
from app.providers.mock import MockMediaProvider, MockTextProvider
from app.workflows.engine import Step
from app.workflows.state import WorkflowContext


def _get_text_provider() -> Provider:
    """Get the best available text provider (Ollama if running, else mock)."""
    use_ollama = os.environ.get("AI_PROVIDER", "auto")

    if use_ollama == "mock":
        return MockTextProvider()

    # Try Ollama
    try:
        from app.providers.ollama import OllamaProvider

        model = os.environ.get("OLLAMA_MODEL", "llama3.2")
        provider = OllamaProvider(model=model)
        # Quick health check
        import urllib.request
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
        return provider
    except Exception:
        return MockTextProvider()


def _get_payload(ctx: WorkflowContext) -> dict[str, Any]:
    """Parse the JSON payload from the workflow context."""
    if not ctx.payload:
        return {}
    return json.loads(ctx.payload)


def _get_output_root(ctx: WorkflowContext) -> Path:
    """Determine the output directory for this workflow's assets."""
    payload = _get_payload(ctx)
    topic_slug = payload.get("topic", "untitled").lower().replace(" ", "_")[:30]
    return Path("output") / topic_slug


# --- Step Handlers ---


def research_step(ctx: WorkflowContext) -> dict[str, Any]:
    """Step 1: Research the topic."""
    payload = _get_payload(ctx)
    topic = payload.get("topic", "")

    provider = _get_text_provider()
    agent = ResearchAgent(provider=provider)
    return agent.run({"topic": topic})


def fact_check_step(ctx: WorkflowContext) -> dict[str, Any]:
    """Step 2: Validate research quality."""
    research = ctx.results[0]  # output from step 1

    agent = FactCheckAgent(min_score=0.5)
    return agent.run(research)


def script_step(ctx: WorkflowContext) -> dict[str, Any]:
    """Step 3: Generate script outline from research."""
    research = ctx.results[0]  # output from step 1
    payload = _get_payload(ctx)

    # Parse duration to determine section length
    duration_str = payload.get("duration", "5m")
    total_seconds = _parse_duration(duration_str)

    # For short videos (under 30s), limit key points to fit duration
    key_points = research.get("key_points", [])
    if total_seconds <= 30:
        # ~4 seconds per scene minimum for narration
        max_sections = max(total_seconds // 4, 2) - 2  # minus intro and conclusion
        key_points = key_points[:max(int(max_sections), 1)]

    num_points = len(key_points)
    # intro + points + conclusion = num_points + 2 sections
    section_duration = total_seconds // max(num_points + 2, 1)

    agent = ScriptWriterAgent(default_section_duration=max(section_duration, 2))
    return agent.run({
        "topic": research["topic"],
        "summary": research["summary"],
        "key_points": key_points,
    })


def storyboard_step(ctx: WorkflowContext) -> dict[str, Any]:
    """Step 4: Convert script to visual storyboard."""
    research = ctx.results[0]  # topic from step 1
    script = ctx.results[2]    # output from step 3

    agent = StoryboardAgent()
    return agent.run({
        "topic": research["topic"],
        "sections": script["sections"],
    })


def voice_step(ctx: WorkflowContext) -> dict[str, Any]:
    """Step 5: Generate narration audio for each scene."""
    from app.rendering.tts import text_to_speech

    script = ctx.results[2]      # output from step 3
    storyboard = ctx.results[3]  # output from step 4

    output_root = _get_output_root(ctx)
    artifacts = []
    sections = script.get("sections", [])
    scenes = storyboard.get("scenes", [])

    for idx, scene in enumerate(scenes):
        section = sections[idx] if idx < len(sections) else {}
        content = section.get("content", "") if isinstance(section, dict) else getattr(section, "content", "")
        duration = section.get("duration_seconds", 30) if isinstance(section, dict) else getattr(section, "duration_seconds", 30)
        scene_num = scene.get("scene_number", idx + 1) if isinstance(scene, dict) else getattr(scene, "scene_number", idx + 1)

        audio_path = str(output_root / f"audio/scene-{scene_num}.mp3")
        text_to_speech(content, audio_path)

        artifacts.append({
            "asset_path": audio_path,
            "format": "mp3",
            "duration_seconds": duration,
            "metadata": {"scene": f"scene-{scene_num}", "provider": "edge-tts"},
        })

    return {"artifacts": artifacts, "count": len(artifacts)}


def image_step(ctx: WorkflowContext) -> dict[str, Any]:
    """Step 6: Generate visual images for each scene."""
    from app.rendering.image_gen import generate_scene_image

    storyboard = ctx.results[3]  # output from step 4
    payload = _get_payload(ctx)
    style = payload.get("style", "default")
    topic = payload.get("topic", "")

    output_root = _get_output_root(ctx)
    artifacts = []
    scenes = storyboard.get("scenes", [])

    for scene in scenes:
        title = scene.get("title", "") if isinstance(scene, dict) else getattr(scene, "title", "")
        description = scene.get("description", "") if isinstance(scene, dict) else getattr(scene, "description", "")
        scene_num = scene.get("scene_number", 0) if isinstance(scene, dict) else getattr(scene, "scene_number", 0)

        image_path = str(output_root / f"images/scene-{scene_num}.png")
        generate_scene_image(
            title=title,
            description=description,
            output_path=image_path,
            style=style,
            scene_number=scene_num,
            topic=topic,
        )

        artifacts.append({
            "asset_path": image_path,
            "format": "png",
            "width": 1280,
            "height": 720,
            "metadata": {"scene": f"scene-{scene_num}", "provider": "loremflickr+pillow"},
        })

    return {"artifacts": artifacts, "count": len(artifacts)}


def music_step(ctx: WorkflowContext) -> dict[str, Any]:
    """Step 7: Generate background music for each scene."""
    storyboard = ctx.results[3]  # output from step 4
    payload = _get_payload(ctx)
    style = payload.get("style", "default")

    output_root = _get_output_root(ctx)
    asset_mgr = AssetManager(root=str(output_root))
    provider = MockMediaProvider()
    agent = MusicAgent(provider=provider, asset_manager=asset_mgr)

    # Map style to mood
    mood_map = {
        "pixar": "upbeat",
        "documentary": "ambient",
        "explainer": "light",
        "cinematic": "dramatic",
        "cartoon": "playful",
        "default": "neutral",
    }
    mood = mood_map.get(style, "neutral")

    artifacts = []
    scenes = storyboard.get("scenes", [])

    for scene in scenes:
        duration = scene.get("duration_seconds", 30) if isinstance(scene, dict) else getattr(scene, "duration_seconds", 30)
        scene_num = scene.get("scene_number", 0) if isinstance(scene, dict) else getattr(scene, "scene_number", 0)

        artifact = agent.run({
            "mood": mood,
            "duration_seconds": duration,
            "scene": f"scene-{scene_num}",
        })
        artifacts.append(artifact)

    return {"artifacts": artifacts, "count": len(artifacts)}


def compose_step(ctx: WorkflowContext) -> dict[str, Any]:
    """Step 8: Assemble all assets into a real video using FFmpeg."""
    from app.rendering.video import compose_video

    script = ctx.results[2]    # output from step 3
    voice = ctx.results[4]     # output from step 5
    images = ctx.results[5]    # output from step 6
    payload = _get_payload(ctx)

    total_target = _parse_duration(payload.get("duration", "5m"))
    output_root = _get_output_root(ctx)
    output_path = str(output_root / "final.mp4")

    voice_artifacts = voice.get("artifacts", [])
    image_artifacts = images.get("artifacts", [])
    sections = script.get("sections", [])

    # Build scene list — enforce duration per scene
    num_scenes = min(len(voice_artifacts), len(image_artifacts))
    per_scene = max(total_target / max(num_scenes, 1), 2)

    scenes = []
    for idx in range(num_scenes):
        scenes.append({
            "image_path": image_artifacts[idx]["asset_path"],
            "audio_path": voice_artifacts[idx]["asset_path"],
            "duration": per_scene,
        })

    video_path = compose_video(scenes, output_path)

    return {
        "output_path": video_path,
        "total_duration_seconds": per_scene * num_scenes,
        "scene_count": len(scenes),
        "metadata": {
            "format": "mp4",
            "codec": "h264+aac",
            "resolution": "1280x720",
        },
    }


def review_step(ctx: WorkflowContext) -> dict[str, Any]:
    """Step 9: Final quality review."""
    research = ctx.results[0]
    script = ctx.results[2]
    storyboard = ctx.results[3]
    voice = ctx.results[4]
    images = ctx.results[5]
    music = ctx.results[6]
    compose = ctx.results[7]

    # Combine all assets for the reviewer
    all_assets = (
        voice.get("artifacts", [])
        + images.get("artifacts", [])
        + music.get("artifacts", [])
    )

    agent = ReviewerAgent(min_score=0.5)
    review = agent.run({
        "research": research,
        "script": script,
        "storyboard": storyboard,
        "assets": all_assets,
    })

    # Add video output info
    review["video_path"] = compose.get("output_path", "")
    return review


# --- Pipeline Builder ---


def build_video_pipeline() -> list[Step]:
    """Build the full 9-step video generation pipeline."""
    return [
        Step(name="research", handler=research_step),
        Step(name="fact_check", handler=fact_check_step),
        Step(name="script", handler=script_step),
        Step(name="storyboard", handler=storyboard_step),
        Step(name="voice", handler=voice_step),
        Step(name="image", handler=image_step),
        Step(name="music", handler=music_step),
        Step(name="compose", handler=compose_step),
        Step(name="review", handler=review_step),
    ]


# --- Helpers ---


def _parse_duration(duration_str: str) -> int:
    """Parse a duration string like '5m' or '10m' to seconds."""
    duration_str = duration_str.strip().lower()
    if duration_str.endswith("m"):
        try:
            return int(duration_str[:-1]) * 60
        except ValueError:
            return 300
    if duration_str.endswith("s"):
        try:
            return int(duration_str[:-1])
        except ValueError:
            return 300
    try:
        return int(duration_str)
    except ValueError:
        return 300
