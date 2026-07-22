# AI Studio

AI Studio is a modular AI workflow platform implemented as an extensible Python monolith. It provides a testable orchestration foundation for AI-driven media workflows, with a focus on clean dependency boundaries, provider abstraction, and agent-based pipeline stages.

## Status

- All planned tasks in the implementation plan are complete.
- The repository currently passes `pytest -q` with `102 passed`.
- Core features include workflow orchestration, persistent storage, provider routing, plugin discovery, asset management, evaluation hooks, and a set of modular agents.

## What is implemented

- **Workflow Persistence** — Workflows are persisted to SQLite via SQLAlchemy. Supports resume from failure, conflict detection (409 on re-execute), and UUID-based identification.
- **Web UI** — A simple browser-based dashboard for submitting, executing, and monitoring workflows.
- **REST API** — FastAPI endpoints for workflow submission, status queries, and execution.
- **CLI** — Typer-based commands for workflow operations.
- **Workflow Engine** — Sequential step execution with state tracking, failure handling, and cancellation.
- **Provider Abstraction** — Capability-based routing with pluggable AI backends.
- **Plugin System** — Safe directory-based plugin discovery and loading.
- **Asset Manager** — Filesystem-based artifact staging and retrieval.
- **Telemetry & Evaluation** — Structured observability hooks and quality metrics.
- **9 Agents** — Research, Fact-Check, Script Writer, Storyboard, Voice, Image, Music, Composer, and Reviewer.

## Architecture

```
User ──→ Web UI / CLI / API
              │
              ▼
        FastAPI Router
              │
              ▼
     WorkflowRepository ←──→ SQLite (Job persistence)
              │
              ▼
       WorkflowEngine
              │
     ┌────────┼────────┐
     ▼        ▼        ▼
  Agents   Providers  EventBus
     │        │
     ▼        ▼
AssetManager  AI Backends (mock/real)
```

## How to run

### 1. Setup

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the API server

```bash
uvicorn app.api.main:app --reload --port 8000
```

### 3. Open the Web UI

Open your browser to: **http://localhost:8000/ui**

The UI provides:
- Submit new workflows
- View all workflows with status
- Execute pending/failed workflows
- Resume failed workflows automatically
- Real-time status refresh

### 4. Use the CLI

```bash
python -m app.cli.main status
python -m app.cli.main workflow-run demo
python -m app.cli.main workflow-status <workflow-id>
python -m app.cli.main workflow-execute <workflow-id>
```

### 5. Use the API directly

```bash
# Submit a workflow
curl -X POST http://localhost:8000/api/v1/workflows

# Check status
curl http://localhost:8000/api/v1/workflows/{id}/status

# Execute
curl -X POST http://localhost:8000/api/v1/workflows/{id}/execute
```

### 6. Run tests

```bash
pytest -q
```

### 7. Docker

```bash
docker-compose up --build
```

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/workflows` | POST | Create new workflow (returns UUID) |
| `/api/v1/workflows/{id}/status` | GET | Get workflow state |
| `/api/v1/workflows/{id}/execute` | POST | Execute or resume workflow |
| `/api/v1/workflows` | GET | List all workflows |
| `/ui` | GET | Web dashboard |

## Configuration

Copy `.env.example` to `.env` and adjust:

```env
APP_NAME=ai-studio
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./ai_studio.db
```

## Project Structure

```
app/
├── api/          # FastAPI routes and schemas
├── agents/       # 9 pipeline agents (research → review)
├── assets/       # Artifact staging manager
├── cache/        # Response cache
├── cli/          # Typer CLI commands
├── config/       # Settings, container, providers.yaml
├── evaluation/   # Quality metrics
├── models/       # SQLAlchemy ORM models (Job)
├── plugins/      # Plugin system
├── providers/    # AI backend abstraction
├── services/     # Composer, EventBus
├── storage/      # DB connection, WorkflowRepository
├── static/       # Web UI (HTML/JS)
├── telemetry/    # Observability hooks
├── utils/        # Path helpers
└── workflows/    # Engine, state machine
```

## Notes for future work

- Real AI provider implementations (Gemini, Ollama, HuggingFace) behind the existing provider abstraction.
- End-to-end video pipeline workflow definition (chain all 9 agents).
- Parallel execution for independent steps (Voice/Image/Music).
- WebSocket-based live progress updates in the UI.
- Publishing adapters for YouTube, TikTok, Instagram.
