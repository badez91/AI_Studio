# AI Studio

AI Studio is a modular AI workflow platform implemented as an extensible Python monolith. It provides a testable orchestration foundation for AI-driven media workflows, with a focus on clean dependency boundaries, provider abstraction, and agent-based pipeline stages.

## Status

- All planned tasks in the implementation plan are complete.
- The repository currently passes `pytest -q` with `90 passed`.
- Core features include workflow orchestration, provider routing, plugin discovery, asset management, evaluation hooks, and a set of modular agents.

## What is implemented

- API and CLI entry points for submitting workflows, checking status, and executing workflows.
- Workflow engine with sequential step execution, state tracking, and failure handling.
- Provider abstraction layer with capability-based routing and pluggable providers.
- Plugin manager with safe discovery and load error handling.
- Asset manager for artifact staging and filesystem persistence.
- Telemetry and evaluation helpers for structured workflow observability.
- Agents for research, fact-check, script writing, storyboard generation, voice, image, music, composition, and review.

## System design review

### Architecture

- Modular monolith: clear separation between API, CLI, agents, workflows, providers, plugins, services, and storage.
- Dependency wiring is explicit through a lightweight container pattern.
- Workflow execution is isolated in `app/workflows/engine.py`, making orchestration logic easy to test and extend.
- Provider routing is abstracted in `app/providers`, enabling future integration with real AI backends without changing workflow logic.

### User-facing flow

A user or client can:

1. Submit a workflow via `POST /api/v1/workflows`.
2. Check workflow state via `GET /api/v1/workflows/{workflow_id}/status`.
3. Execute a workflow via `POST /api/v1/workflows/{workflow_id}/execute`.
4. Use CLI commands such as:
   - `python -m app.cli.main status`
   - `python -m app.cli.main workflow-run "demo"`
   - `python -m app.cli.main workflow-status wf-1`
   - `python -m app.cli.main workflow-execute wf-1`

### User experience

- The platform is designed to be approachable from both API and CLI.
- Workflow operations return deterministic states and structured results for easy automation.
- Asset generation steps currently produce structured placeholder artifacts and can be extended with real media provider implementations.
- The review and telemetry layers provide quality signals and can be used to validate outputs before publishing.

## How to run

1. Create a Python virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the API:
   ```bash
   uvicorn app.api.main:create_app --factory --reload
   ```
4. Use the CLI:
   ```bash
   python -m app.cli.main status
   python -m app.cli.main workflow-run demo
   ```
5. Run tests:
   ```bash
   pytest -q
   ```

## Notes for future work

- Real provider implementations and media generation backends should be added behind the existing provider abstraction.
- Workflow persistence and resume support can be expanded beyond the current in-memory workflow store.
- Additional user-facing workflows, publishing adapters, and frontend integration are natural next steps.
