from __future__ import annotations

from fastapi import FastAPI

from app.api.router import router as workflow_router
from app.config.container import build_container
from app.config.logging import configure_logging


def create_app() -> FastAPI:
    """Create the FastAPI application instance."""

    configure_logging()
    container = build_container()
    settings = container.resolve("settings")

    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.include_router(workflow_router, prefix="/api/v1", tags=["workflows"])

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
