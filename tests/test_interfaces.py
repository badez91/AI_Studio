from __future__ import annotations

import subprocess
import sys

from fastapi.testclient import TestClient

from app.api.main import app
from app.cli.main import app as cli_app
from app.models.job import Job  # noqa: F401 — register model
from app.storage.connection import Base, engine

# Ensure test database tables exist.
Base.metadata.create_all(bind=engine)

client = TestClient(app)

PYTHON = sys.executable


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_workflow_endpoints() -> None:
    response = client.post("/api/v1/workflows")
    assert response.status_code == 200
    data = response.json()
    assert "workflow_id" in data

    workflow_id = data["workflow_id"]
    response = client.get(f"/api/v1/workflows/{workflow_id}/status")
    assert response.status_code == 200
    assert response.json()["workflow_id"] == workflow_id
    assert response.json()["state"] == "pending"

    response = client.post(f"/api/v1/workflows/{workflow_id}/execute")
    assert response.status_code == 200
    body = response.json()
    assert body["workflow_id"] == workflow_id
    assert body["state"] == "completed"
    assert body["results"] == ["hello"]


def test_workflow_not_found() -> None:
    response = client.get("/api/v1/workflows/nonexistent-id/status")
    assert response.status_code == 404


def test_workflow_execute_twice_returns_conflict() -> None:
    response = client.post("/api/v1/workflows")
    workflow_id = response.json()["workflow_id"]

    # First execution succeeds.
    response = client.post(f"/api/v1/workflows/{workflow_id}/execute")
    assert response.status_code == 200
    assert response.json()["state"] == "completed"

    # Second execution returns 409 (already completed).
    response = client.post(f"/api/v1/workflows/{workflow_id}/execute")
    assert response.status_code == 409


def test_cli_status_command() -> None:
    result = subprocess.run(
        [PYTHON, "-m", "app.cli.main", "status"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "ai-studio is ready" in result.stdout


def test_cli_workflow_run_command() -> None:
    result = subprocess.run(
        [PYTHON, "-m", "app.cli.main", "workflow-run", "demo"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Workflow 'demo' executed" in result.stdout


def test_cli_workflow_status_command() -> None:
    result = subprocess.run(
        [PYTHON, "-m", "app.cli.main", "workflow-status", "wf-1"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "wf-1" in result.stdout


def test_cli_workflow_execute_command() -> None:
    result = subprocess.run(
        [PYTHON, "-m", "app.cli.main", "workflow-execute", "wf-1"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Workflow 'wf-1' executed" in result.stdout
    assert "completed" in result.stdout
