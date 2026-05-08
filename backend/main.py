"""LiveMirror FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager
from importlib import import_module

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db
from features import enabled_router_modules
from routes.core_auth import get_current_user
from services.task_queue import shutdown_task_queue
from services.transcription import check_transcription_environment


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    try:
        yield
    finally:
        shutdown_task_queue(wait=False)


def create_app() -> FastAPI:
    init_db()

    app = FastAPI(
        title="LiveMirror Core API",
        description="Core upload, transcription, report, attribution, suggestion, trend, and auth APIs.",
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    for module_name in ["routes.features", *enabled_router_modules()]:
        module = import_module(module_name)
        dependencies = []
        if getattr(module.router, "prefix", "").startswith("/api"):
            dependencies.append(Depends(get_current_user))
        app.include_router(module.router, dependencies=dependencies)

    @app.get("/")
    async def root():
        return {
            "message": "LiveMirror Core API",
            "version": settings.app_version,
            "docs": "/docs",
            "core_routes": [
                "/auth",
                "/api/features",
                "/api/upload",
                "/api/task",
                "/api/report",
                "/api/export",
                "/api/attribution",
                "/api/suggestions",
                "/api/trends",
                "/api/monitor",
                "/api/history",
                "/api/user",
                "/api/batch-export",
            ],
        }

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "version": settings.app_version,
            "transcription_provider": settings.transcription_provider,
            "transcription": check_transcription_environment(),
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
