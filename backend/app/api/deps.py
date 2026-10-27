"""Shared FastAPI dependencies: settings, database, worker, rate limiting.

The application object carries the singletons (``app.state``); routers ask
for them through these callables so tests can substitute fakes by building
their own app with :func:`app.main.create_app`.
"""

from __future__ import annotations

from fastapi import Depends, Request

from app.core.config import Settings
from app.core.security import RateLimiter
from app.rendering.worker import RenderWorker
from app.storage.database import Database


def get_app_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_db(request: Request) -> Database:
    return request.app.state.db


def get_worker(request: Request) -> RenderWorker:
    return request.app.state.worker


def get_rate_limiter(request: Request) -> RateLimiter:
    return request.app.state.rate_limiter


def rate_limit(
    request: Request,
    limiter: RateLimiter = Depends(get_rate_limiter),
) -> None:
    """Dependency for expensive endpoints (validation, import, prompt)."""
    limiter.check()


SettingsDep = Depends(get_app_settings)
DatabaseDep = Depends(get_db)
WorkerDep = Depends(get_worker)
RateLimitDep = Depends(rate_limit)
