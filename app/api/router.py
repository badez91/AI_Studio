from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.storage.workflow_repository import WorkflowRepository
from app.workflows.engine import Step, WorkflowEngine
from app.workflows.state import WorkflowContext, WorkflowState


router = APIRouter()


class WorkflowCreateRequest(BaseModel):
    topic: str = ""
    style: str = "default"
    duration: str = "5m"


def _get_repo() -> WorkflowRepository:
    return WorkflowRepository()


@router.get("/workflows")
async def list_workflows() -> list[dict[str, Any]]:
    repo = _get_repo()
    try:
        jobs = repo.list_all()
        results = []
        for job in jobs:
            payload = json.loads(job.payload) if job.payload else {}
            results.append({
                "id": job.id,
                "name": job.name,
                "status": job.status,
                "current_step": job.current_step,
                "topic": payload.get("topic", ""),
                "style": payload.get("style", ""),
                "duration": payload.get("duration", ""),
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "updated_at": job.updated_at.isoformat() if job.updated_at else None,
            })
        return results
    finally:
        repo.close()


@router.post("/workflows")
async def submit_workflow(body: WorkflowCreateRequest | None = None) -> dict[str, str]:
    repo = _get_repo()
    try:
        topic = body.topic if body and body.topic else "Untitled"
        style = body.style if body else "default"
        duration = body.duration if body else "5m"

        payload = json.dumps({
            "topic": topic,
            "style": style,
            "duration": duration,
        })
        name = topic[:100] if topic else "default"

        job = repo.create(name=name, payload=payload)
        return {"workflow_id": job.id}
    finally:
        repo.close()


@router.get("/workflows/{workflow_id}/status")
async def get_workflow_status(workflow_id: str) -> dict[str, str]:
    repo = _get_repo()
    try:
        job = repo.get(workflow_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return {"workflow_id": job.id, "state": job.status}
    finally:
        repo.close()


@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str) -> dict[str, Any]:
    repo = _get_repo()
    try:
        job = repo.get(workflow_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Workflow not found")

        # Resume support: if the workflow already completed or was cancelled, reject.
        if job.status == WorkflowState.COMPLETED.value:
            raise HTTPException(status_code=409, detail="Workflow already completed")
        if job.status == WorkflowState.CANCELLED.value:
            raise HTTPException(status_code=409, detail="Workflow was cancelled")

        # Build the context from persisted state (enables resume from last step).
        context = repo.to_context(job)

        # Build the full video generation pipeline.
        from app.workflows.video_pipeline import build_video_pipeline

        steps = build_video_pipeline()

        # If resuming a failed workflow, skip already-completed steps.
        if context.state == WorkflowState.FAILED:
            completed_count = len(context.results)
            steps = steps[completed_count:]
            context.state = WorkflowState.PENDING
            context.errors.clear()

        engine_instance = WorkflowEngine(steps)
        result = engine_instance.run(context)

        # Persist final state back to the database.
        repo.sync_from_context(job, result)

        return {
            "workflow_id": job.id,
            "state": result.state.value,
            "results": result.results,
        }
    finally:
        repo.close()
