from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from app.storage.connection import SessionLocal

T = TypeVar("T")


class Repository(Generic[T]):
    """Base repository for SQLAlchemy ORM models."""

    def __init__(self, model: type[T], session: Session | None = None) -> None:
        self.model = model
        self.session = session or SessionLocal()

    def add(self, entity: T) -> T:
        self.session.add(entity)
        self.session.flush()
        return entity

    def get(self, entity_id: str) -> T | None:
        return self.session.get(self.model, entity_id)

    def delete(self, entity: T) -> None:
        self.session.delete(entity)
        self.session.flush()


class Database:
    """Provides session management and schema initialization."""

    def __init__(self, session_factory: Session | None = None) -> None:
        self.session_factory = session_factory or SessionLocal

    def get_session(self) -> Session:
        return self.session_factory()

    def create_all(self, base: type[T]) -> None:
        from app.storage.connection import engine

        base.metadata.create_all(bind=engine)
