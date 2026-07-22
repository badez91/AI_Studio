from __future__ import annotations

from pydantic import BaseModel


class WorkflowSubmitResponse(BaseModel):
    workflow_id: str


class WorkflowStatusResponse(BaseModel):
    workflow_id: str
    state: str
