from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.job import Job
from app.storage.database import Database, Repository
from app.storage.connection import Base


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = session_factory()
    yield session
    session.close()


def test_session_creation() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = session_factory()
    assert session.is_active
    session.close()


def test_model_instantiation() -> None:
    job = Job(id=str(uuid4()), name="test-job", status="pending")
    assert job.id is not None
    assert job.name == "test-job"
    assert job.status == "pending"


def test_repository_add_and_get(session) -> None:
    repository = Repository(Job, session=session)
    job = Job(id=str(uuid4()), name="repo-job", status="pending")
    repository.add(job)
    session.commit()

    fetched = repository.get(job.id)
    assert fetched is not None
    assert fetched.name == "repo-job"
    assert fetched.status == "pending"


def test_repository_delete(session) -> None:
    repository = Repository(Job, session=session)
    job = Job(id=str(uuid4()), name="delete-job", status="pending")
    repository.add(job)
    session.commit()

    repository.delete(job)
    session.commit()

    assert repository.get(job.id) is None


def test_database_create_all() -> None:
    database = Database()
    database.create_all(Base)
    # Should not raise; tables are created in memory by default settings
