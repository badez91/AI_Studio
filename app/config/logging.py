from __future__ import annotations

import logging
import sys
from pathlib import Path

from loguru import logger

from app.config.settings import get_settings


def configure_logging() -> None:
    """Configure Loguru for the application."""

    settings = get_settings()
    log_path = Path(settings.log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.log_level,
        enqueue=True,
        backtrace=True,
        diagnose=settings.debug,
    )
    logger.add(
        str(log_path),
        level=settings.log_level,
        enqueue=True,
        rotation="10 MB",
        retention="7 days",
        backtrace=True,
        diagnose=settings.debug,
    )

    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn.access").handlers = []
