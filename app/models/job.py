from __future__ import annotations

import json
from typing import Any, Optional

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import TimestampedModel


class Job(TimestampedModel):
    """Represents a workflow execution job."""

    __tablename__ = "jobs"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    current_step: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    results_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    errors_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    @property
    def results(self) -> list[Any]:
        if not self.results_json:
            return []
        return json.loads(self.results_json)

    @results.setter
    def results(self, value: list[Any]) -> None:
        self.results_json = json.dumps(value)

    @property
    def errors(self) -> list[str]:
        if not self.errors_json:
            return []
        return json.loads(self.errors_json)

    @errors.setter
    def errors(self, value: list[str]) -> None:
        self.errors_json = json.dumps(value)
