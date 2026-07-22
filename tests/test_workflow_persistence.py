from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.job import Job
from app.storage.connection import Base
from app.storage.workflow_repository import WorkflowRepository
from app.workflows.state import WorkflowContext, WorkflowState


@pytest.fixture()
def repo():
    """Create a repository backed by an in-memory SQLite database."""
    test_engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=test_engine)
    TestSession = sessionmaker(bind=test_engine, autoflush=False, autocommit=False, future=True)
    session = TestSession()
    repository = WorkflowRepository(session=session)
    yield repository
    session.close()


def test_create_workflow(repo: WorkflowRepository) -> None:
    job = repo.create(name="test-workflow")
    assert job.id is not None
    assert job.status == "pending"
    assert job.current_step == 0
    assert job.results == []
    assert job.errors == []


def test_get_workflow(repo: WorkflowRepository) -> None:
    job = repo.create(name="lookup-test")
    fetched = repo.get(job.id)
    assert fetched is not None
    assert fetched.id == job.id
    assert fetched.name == "lookup-test"


def test_get_nonexistent_workflow(repo: WorkflowRepository) -> None:
    result = repo.get("does-not-exist")
    assert result is None


def test_update_state(repo: WorkflowRepository) -> None:
    job = repo.create(name="state-test")
    repo.update_state(
        job,
        state=WorkflowState.RUNNING,
        current_step=1,
        results=["step-0-result"],
        errors=[],
    )
    fetched = repo.get(job.id)
    assert fetched.status == "running"
    assert fetched.current_step == 1
    assert fetched.results == ["step-0-result"]


def test_to_context(repo: WorkflowRepository) -> None:
    job = repo.create(name="context-test")
    repo.update_state(
        job,
        state=WorkflowState.RUNNING,
        current_step=2,
        results=["a", "b"],
        errors=[],
    )
    context = repo.to_context(job)
    assert context.state == WorkflowState.RUNNING
    assert context.current_step == 2
    assert context.results == ["a", "b"]
    assert context.errors == []


def test_sync_from_context(repo: WorkflowRepository) -> None:
    job = repo.create(name="sync-test")
    context = WorkflowContext(
        state=WorkflowState.COMPLETED,
        current_step=3,
        results=["x", "y", "z"],
        errors=[],
    )
    repo.sync_from_context(job, context)
    fetched = repo.get(job.id)
    assert fetched.status == "completed"
    assert fetched.current_step == 3
    assert fetched.results == ["x", "y", "z"]


def test_list_all(repo: WorkflowRepository) -> None:
    repo.create(name="job-a")
    repo.create(name="job-b")
    all_jobs = repo.list_all()
    assert len(all_jobs) == 2


def test_list_by_status(repo: WorkflowRepository) -> None:
    job_a = repo.create(name="pending-job")
    job_b = repo.create(name="completed-job")
    repo.update_state(job_b, state=WorkflowState.COMPLETED)

    pending_jobs = repo.list_all(status="pending")
    assert len(pending_jobs) == 1
    assert pending_jobs[0].id == job_a.id

    completed_jobs = repo.list_all(status="completed")
    assert len(completed_jobs) == 1
    assert completed_jobs[0].id == job_b.id


def test_resume_failed_workflow(repo: WorkflowRepository) -> None:
    """A failed workflow can be resumed by reading persisted state."""
    job = repo.create(name="resume-test")
    # Simulate partial progress then failure.
    repo.update_state(
        job,
        state=WorkflowState.FAILED,
        current_step=1,
        results=["step-0-ok"],
        errors=["step-1: something went wrong"],
    )

    # Resume: load context, verify we can see where it left off.
    context = repo.to_context(job)
    assert context.state == WorkflowState.FAILED
    assert len(context.results) == 1
    assert context.results[0] == "step-0-ok"
    assert len(context.errors) == 1
