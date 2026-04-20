"""LiveMirror core FastAPI application."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db
from routes import attribution
from routes import core_auth
from routes import core_export
from routes import core_reports
from routes import core_tasks
from routes import core_upload
from routes import suggestions
from routes import trends

init_db()

app = FastAPI(
    title="LiveMirror Core API",
    description="Core upload, transcription, report, attribution, suggestion, trend, and auth APIs.",
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(core_auth.router)
app.include_router(core_upload.router)
app.include_router(core_tasks.router)
app.include_router(core_reports.router)
app.include_router(core_export.router)
app.include_router(attribution.router)
app.include_router(suggestions.router)
app.include_router(trends.router)


@app.get("/")
async def root():
    return {
        "message": "LiveMirror Core API",
        "version": settings.app_version,
        "docs": "/docs",
        "core_routes": [
            "/auth",
            "/api/upload",
            "/api/task",
            "/api/report",
            "/api/export",
            "/api/attribution",
            "/api/suggestions",
            "/api/trends",
        ],
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.app_version,
        "transcription_provider": settings.transcription_provider,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
