from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.storage.connection import SessionLocal
from app.workflows.state import WorkflowContext, WorkflowState


def _get_job_model():
    """Late import to avoid circular dependency with models → storage."""
    from app.models.job import Job
    return Job


class WorkflowRepository:
    """Persists workflow state to the database via the Job model."""

    def __init__(self, session: Session | None = None) -> None:
        self._session = session

    @property
    def session(self) -> Session:
        if self._session is None:
            self._session = SessionLocal()
        return self._session

    def create(self, name: str = "default", payload: str | None = None):
        """Create a new workflow job in PENDING state."""
        Job = _get_job_model()
        job = Job(
            id=str(uuid.uuid4()),
            name=name,
            status=WorkflowState.PENDING.value,
            current_step=0,
            results_json="[]",
            errors_json="[]",
            payload=payload,
        )
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job

    def get(self, workflow_id: str):
        """Retrieve a workflow job by ID."""
        Job = _get_job_model()
        return self.session.get(Job, workflow_id)

    def update_state(
        self,
        job,
        *,
        state: WorkflowState,
        current_step: int | None = None,
        results: list[Any] | None = None,
        errors: list[str] | None = None,
    ):
        """Update a job's workflow state and persist it."""
        job.status = state.value
        if current_step is not None:
            job.current_step = current_step
        if results is not None:
            job.results = results
        if errors is not None:
            job.errors = errors
        job.updated_at = datetime.utcnow()
        self.session.commit()
        self.session.refresh(job)
        return job

    def to_context(self, job) -> WorkflowContext:
        """Convert a persisted Job into a WorkflowContext for engine execution."""
        return WorkflowContext(
            state=WorkflowState(job.status),
            current_step=job.current_step,
            results=list(job.results),
            errors=list(job.errors),
        )

    def sync_from_context(self, job, context: WorkflowContext):
        """Persist the engine's WorkflowContext back to the Job record."""
        return self.update_state(
            job,
            state=context.state,
            current_step=context.current_step,
            results=context.results,
            errors=context.errors,
        )

    def list_all(self, status: str | None = None) -> list:
        """List jobs, optionally filtering by status."""
        Job = _get_job_model()
        query = self.session.query(Job)
        if status:
            query = query.filter(Job.status == status)
        return query.order_by(Job.created_at.desc()).all()

    def close(self) -> None:
        """Close the underlying session."""
        if self._session:
            self._session.close()
            self._session = None
