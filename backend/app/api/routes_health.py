"""Health and diagnostics endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_app_settings, get_db
from app.core.config import Settings
from app.schemas.api import DiagnosticsResponse, HealthResponse
from app.services import diagnostics
from app.storage.database import Database

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_app_settings)) -> dict:
    """Liveness + dependency availability. ``degraded`` is honest, not an error."""
    return diagnostics.health_payload(settings)


@router.get("/diagnostics", response_model=DiagnosticsResponse)
def diag(
    settings: Settings = Depends(get_app_settings),
    db: Database = Depends(get_db),
) -> dict:
    return {
        "health": diagnostics.health_payload(settings),
        "storage": diagnostics.storage_payload(settings),
        "render_concurrency": settings.max_concurrent_renders,
        "rate_limit": {
            "window_s": settings.rate_limit_window_s,
            "max_requests": settings.rate_limit_max_requests,
        },
        "job_counts": db.job_counts(),
    }
