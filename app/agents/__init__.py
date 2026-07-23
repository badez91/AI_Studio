"""Agent abstractions for AI Studio."""

from app.agents.base import BaseAgent, MediaAsset, ResearchResult
from app.agents.fact_check import FactCheckAgent
from app.agents.image import ImageArtifact, ImageGenerationAgent
from app.agents.music import MusicArtifact, MusicAgent
from app.agents.research import ResearchAgent
from app.agents.reviewer import ReviewResult, ReviewerAgent
from app.agents.script_writer import ScriptOutline, ScriptSection, ScriptWriterAgent
from app.agents.storyboard import Storyboard, StoryboardAgent, StoryboardEntry
from app.agents.voice import VoiceArtifact, VoiceGenerationAgent

__all__ = [
    "BaseAgent",
    "FactCheckAgent",
    "ImageArtifact",
    "ImageGenerationAgent",
    "MediaAsset",
    "MusicArtifact",
    "MusicAgent",
    "ResearchAgent",
    "ResearchResult",
    "ReviewResult",
    "ReviewerAgent",
    "ScriptOutline",
    "ScriptSection",
    "ScriptWriterAgent",
    "Storyboard",
    "StoryboardAgent",
    "StoryboardEntry",
    "VoiceArtifact",
    "VoiceGenerationAgent",
]
