from __future__ import annotations

from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import TimestampedModel


class Job(TimestampedModel):
    """Represents a workflow execution job."""

    __tablename__ = "jobs"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
