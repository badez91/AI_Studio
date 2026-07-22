from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.storage.connection import Base


@dataclass
class BaseModel:
    """Base dataclass for simple domain records."""

    id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class TimestampedModel(Base):
    """Base ORM model with id and timestamps."""

    __abstract__ = True

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
