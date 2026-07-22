"""Shared test fixtures for AI Studio."""

from __future__ import annotations

import os
import sys

# Force tests to use a separate test database.
os.environ["DATABASE_URL"] = "sqlite:///./test_ai_studio.db"

# Make the current Python interpreter path available for CLI tests.
PYTHON_EXE = sys.executable
