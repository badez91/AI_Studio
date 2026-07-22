from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import router as workflow_router
from app.config.container import build_container
from app.config.logging import configure_logging
from app.models.job import Job  # noqa: F401 — ensure model is registered before create_all
from app.storage.connection import Base, engine


def create_app() -> FastAPI:
    """Create the FastAPI application instance."""

    configure_logging()
    container = build_container()
    settings = container.resolve("settings")

    # Ensure database tables exist.
    Base.metadata.create_all(bind=engine)

    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.include_router(workflow_router, prefix="/api/v1", tags=["workflows"])

    # Serve static files
    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ui", response_class=HTMLResponse)
    async def ui():
        """Serve the web dashboard."""
        index_path = static_dir / "index.html"
        return index_path.read_text()

    return app


app = create_app()
