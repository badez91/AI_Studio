# AIVideo Studio

An AI orchestration platform that automatically researches, writes, generates, edits, reviews, and publishes videos using the best available free AI providers, with seamless fallback to local models.

---

## 1. Vision & Goals

### 1.1 Objective

Generate a high-quality, fully finalized video from a single text prompt with zero manual editing required for common use cases.

### 1.2 User Interface Example (CLI)

```bash
aivideo create \
    --topic "Why Volcanoes Erupt" \
    --style pixar \
    --language en \
    --duration 5m
```

### 1.3 Expected Output Structure

```
📁 output/
├── script.md
├── storyboard.json
├── narration.mp3
├── subtitles.srt
├── thumbnail.png
├── youtube.json
└── video.mp4
```

---

## 2. Architectural Design Principles

- **Provider-Agnostic:** Abstracted layer to swap AI services seamlessly.
- **Cost-Optimized Strategy:** Free cloud AI tiers utilized first; local models utilized as an offline fallback.
- **Modular Extensibility:** Built around distinct plugins and agent workflows.
- **State Persistence & Resilience:** Every intermediate AI response is cached; failed jobs can resume from any point of failure without losing data.
- **Offline-Capable:** Fully runnable locally without internet connectivity if local models (Ollama, ComfyUI, etc.) are available.
- **Performance Optimization:** Highly parallelized asset generation where dependencies allow.

---

## 3. High-Level Architecture

### 3.1 Block Diagram

```
                        User
                          │
                          ▼
                   CLI / Web UI
                          │
                          ▼
                  Workflow Engine
                          │
      ┌───────────────────┼────────────────────┐
      ▼                   ▼                    ▼
 AI Provider Manager   Asset Manager     Job Manager
      │                   │                    │
      ▼                   ▼                    ▼
  AI Providers        File Storage         SQLite
```

### 3.2 Component Breakdown

- **CLI / Web UI:** Command-line wrapper and API frontend interacting with the engine.
- **Workflow Engine:** Manages linear and parallel DAG execution routes for the video pipeline.
- **AI Provider Manager:** Handles API authentication, rate limits, intelligent routing, cost tracking, and fallbacks.
- **Asset Manager:** Controls structural reads/writes across local file storage and caches.
- **Job Manager:** Uses an internal SQLite instance to track job status, resume states, and process logs.

---

## 4. Pipeline Workflow

```
Topic ➔ Research ➔ Fact Verification ➔ Script ➔ Storyboard ➔ Scene Planning
  ➔ Voice ➔ Character Gen ➔ Background Gen ➔ Animation ➔ Music ➔ SFX
  ➔ Subtitle ➔ Video Composition ➔ Quality Review ➔ Thumbnail ➔ Metadata ➔ Publish
```

---

## 5. Multi-Agent System

Agents communicate strictly using structured JSON schemas rather than loose markdown or free-form text.

| Agent Name         | Primary Responsibility                                              |
|--------------------|---------------------------------------------------------------------|
| ResearchAgent      | Performs web intelligence and gathering.                             |
| FactCheckAgent     | Cross-references extracted facts to clear out hallucinations.        |
| ScriptWriterAgent  | Constructs narrative scripts based on verified facts.               |
| StoryboardAgent    | Generates chronological visual prompts and scenes descriptions.      |
| CharacterAgent     | Formulates visual identity consistency definitions.                  |
| ImageAgent         | Controls the background, object, and element image creations.        |
| AnimationAgent     | Orchestrates image-to-video or text-to-video generation engines.    |
| VoiceAgent         | Handles Text-to-Speech (TTS) narrations and actor tone.             |
| SubtitleAgent      | Uses STT models to synchronize timecode subtitle files.             |
| MusicAgent         | Identifies and downloads/generates appropriate background scoring.  |
| ComposerAgent      | Orchestrates automated timeline video and audio rendering.          |
| ThumbnailAgent     | Handles contextually driven visual banner/thumbnail assets.         |
| ReviewerAgent      | Validates image and final video files against quality standards.    |
| PublisherAgent     | Handles automated programmatic API upload schemas to social platforms. |

---

## 6. AI Capability & Router Strategy

### 6.1 Provider Capabilities Matrix

The system ranks and fallbacks capabilities dynamically across cloud and local nodes:

| Capability    | Gemini | OpenRouter | Groq | HF | Ollama | Local Models |
|---------------|--------|------------|------|----|--------|--------------|
| Research      | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐   | ⭐⭐⭐ | ⭐  | ⭐⭐     | ⭐            |
| Script        | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐   | ⭐⭐⭐⭐ | ⭐  | ⭐⭐     | ⭐            |
| Storyboard    | ⭐⭐⭐⭐  | ⭐⭐⭐⭐   | ⭐⭐⭐ | ⭐  | ⭐⭐     | ⭐            |
| Translation   | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐   | ⭐⭐⭐ | ⭐  | ⭐⭐⭐    | ⭐            |
| Vision        | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐   | ⭐⭐⭐ | ⭐⭐ | ⭐⭐     | ⭐⭐           |
| Image         | ❌     | ❌         | ❌   | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐      |
| Video         | ❌     | ❌         | ❌   | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐      |
| Voice         | ⭐⭐⭐  | ⭐⭐       | ❌   | ⭐⭐ | ⭐⭐⭐    | ⭐⭐⭐⭐⭐      |

### 6.2 Service Provider Endpoints

**Language Models (LLM / Vision / Translation)**

- **Google AI Studio (Gemini):** High context tier, ideal for research, multi-turn review, and video structuring.
- **OpenRouter / Hugging Face:** Router endpoint targeting cost-free open models.
- **Groq:** Ultra low-latency scripting and meta extraction.
- **Ollama / LM Studio:** Local environment fallback for runtime offline independence.

**Specialized Providers**

- **Research:** Tavily, Serper, Brave Search, DuckDuckGo, Local RAG.
- **Image Generation:** Hugging Face Spaces (Free Cloud), FLUX, SDXL, ComfyUI API (Local).
- **Video Generation:** ComfyUI workflows, Wan2.x, CogVideoX, LTX Video, Pika (Limited Cloud).
- **Audio (TTS/STT):** Whisper (Local/Cloud), Piper, Kokoro TTS, Coqui, Google AI TTS.
- **Music & SFX:** Stable Audio Open, MusicGen, Freesound API, Pixabay Audio Library.

---

## 7. Storage & Project Directory Layout

```
project/
├── config.yaml          # Configures system preferences, priorities, and concurrency limits
├── input/               # Raw prompts and initial script concepts
├── cache/               # Shared response cache folder for LLM/Image calls
├── prompts/             # Core base prompts for the specialized agent matrix
├── jobs/                # SQLite persistent engine tracking state machines
├── logs/                # Global runtime tracking logs
├── assets/              # Staging directory for partial rendering
│   ├── images/
│   ├── voice/
│   ├── music/
│   └── video/
└── output/              # Final deliverable distributions
    ├── script.md
    ├── storyboard.json
    ├── subtitles.srt
    ├── thumbnail.png
    ├── metadata.json
    └── final.mp4
```

---

## 8. Technology Stack

- **Language & Runtime:** Python 3.12+
- **Interfaces:** Typer (CLI Execution) + FastAPI (Backend Web Dashboard)
- **Orchestration Logic:** LangGraph or Prefect (DAG workflow orchestration engine)
- **Persistence Layers:** SQLite (Internal state, jobs tracking, local caching)
- **Composition Engine:** FFmpeg CLI / Python binding wrapper
- **Model Integration Abstraction:** LiteLLM (Cloud provider routing unified wrapper)
- **Local Infrastructure Hooks:** Ollama API, LM Studio local host, ComfyUI API nodes
- **Containerization Deployment:** Docker + Docker Compose

---

## 9. Implementation Roadmap

### Phase 1: Minimum Viable Product (MVP)

- Build basic modular monolith architecture patterns.
- Core CLI configuration implementation.
- Basic Provider routing manager hook for Gemini, Hugging Face, and local TTS/FFmpeg compilers.

### Phase 2: Advanced Automation

- Character embedding injection to maintain structural visual consistency.
- Automated B-roll selection heuristic maps.
- Integrated AI closed-loop automated structural quality review checking.

### Phase 3: Publishing Ecosystem

- Integration with YouTube, TikTok, and Instagram programmatic video uploading interfaces.
- SEO script generation and localized metadata translations.
- Automated A/B optimization testing frameworks for visual elements.

### Phase 4: Enterprise Layer

- Web layout management framework panels.
- Asynchronous parallel execution worker orchestration via distributed job runners.
- Kubernetes provisioning configuration systems.

---

## Design Implementation Recommendation

Maintain an agile internal plugin layout inside a unified **Modular Monolith** pattern first. This prevents operational infrastructure strain over network boundaries during early prototyping stages, allowing an easy migration transition route into standard Microservices when scale bottlenecks are met later on.
