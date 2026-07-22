from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.workflows.engine import Step, WorkflowEngine
from app.workflows.state import WorkflowContext, WorkflowState


router = APIRouter()

_workflows: Dict[str, WorkflowContext] = {}


@router.post("/workflows")
async def submit_workflow() -> dict[str, str]:
    workflow_id = "wf-1"
    context = WorkflowContext()
    _workflows[workflow_id] = context
    return {"workflow_id": workflow_id}


@router.get("/workflows/{workflow_id}/status")
async def get_workflow_status(workflow_id: str) -> dict[str, str]:
    context = _workflows.get(workflow_id)
    if context is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"workflow_id": workflow_id, "state": context.state.value}


@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str) -> dict[str, Any]:
    context = _workflows.get(workflow_id)
    if context is None:
        raise HTTPException(status_code=404, detail="Workflow not found")

    def hello_step(ctx: WorkflowContext) -> str:
        return "hello"

    engine = WorkflowEngine([Step(name="hello", handler=hello_step)])
    result = engine.run(context)

    return {
        "workflow_id": workflow_id,
        "state": result.state.value,
        "results": result.results,
    }
