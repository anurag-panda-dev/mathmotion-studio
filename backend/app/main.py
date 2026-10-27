"""FastAPI application factory: middleware, routes, startup/shutdown.

Wires together everything built so far:

* :class:`~app.core.config.Settings` (immutable per process);
* :class:`~app.storage.database.Database` (SQLite metadata);
* :class:`~app.rendering.worker.RenderWorker` (subprocess render queue);
* the ``/api/v1`` routers.

Middleware order (outermost first): request-id -> CORS -> origin check.
The app listens on loopback only unless explicitly reconfigured.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from app.api import (
    routes_health,
    routes_jobs,
    routes_lessons,
    routes_media,
    routes_prompt,
    routes_reference,
    routes_scene,
    routes_settings,
)
from app.core.config import APP_NAME, APP_VERSION, SCENE_FORMAT_VERSION, Settings, get_settings
from app.core.errors import AppError, NotFoundError
from app.core.logging import RequestContextMiddleware, configure_logging, get_logger, request_id_of
from app.core.security import OriginCheckMiddleware, RateLimiter
from app.rendering.worker import RenderWorker
from app.storage.database import Database

log = get_logger("main")

API_PREFIX = "/api/v1"


def _error_payload(request: Request, code: str, message: str, detail: Any = None) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id_of(request),
            "detail": detail,
        }
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: Settings = app.state.settings
    settings.ensure_directories()
    configure_logging(settings.logs_dir)
    db: Database = app.state.db
    db.init()
    worker: RenderWorker = app.state.worker
    await worker.start()
    log.info("%s %s ready (scene format %s)", APP_NAME, APP_VERSION, SCENE_FORMAT_VERSION)
    try:
        yield
    finally:
        await worker.stop()
        log.info("shutdown complete")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    app = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        lifespan=lifespan,
        docs_url=f"{API_PREFIX}/docs",
        openapi_url=f"{API_PREFIX}/openapi.json",
    )
    app.state.settings = settings
    app.state.db = Database(settings.db_path)
    app.state.worker = RenderWorker(settings, app.state.db)
    app.state.rate_limiter = RateLimiter(
        settings.rate_limit_max_requests, settings.rate_limit_window_s
    )

    # --- middleware (outermost added last) ------------------------------
    app.add_middleware(
        OriginCheckMiddleware, allowed_origins=settings.allowed_origins
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.allowed_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )
    app.add_middleware(RequestContextMiddleware)

    # --- exception handlers --------------------------------------------
    @app.exception_handler(AppError)
    async def _app_error(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(request, exc.code, exc.message, exc.detail),
        )

    @app.exception_handler(ValidationError)
    async def _pydantic_error(request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=_error_payload(
                request, "validation_failed", "The request body is not valid.", exc.errors()
            ),
        )

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        log.exception("unhandled error", extra={"request_id": request_id_of(request)})
        return JSONResponse(
            status_code=500,
            content=_error_payload(
                request, "internal_error", "Something went wrong on the server."
            ),
        )

    # --- routes ---------------------------------------------------------
    for router in (
        routes_health.router,
        routes_prompt.router,
        routes_reference.router,
        routes_scene.router,
        routes_lessons.router,
        routes_jobs.router,
        routes_media.router,
        routes_settings.router,
    ):
        app.include_router(router, prefix=API_PREFIX)

    # --- frontend static assets (built dist, or honest status page) -----
    _mount_frontend(app, settings)
    return app


def _mount_frontend(app: FastAPI, settings: Settings) -> None:
    dist = settings.frontend_dist
    index = dist / "index.html"
    if index.is_file():
        assets = dist / "assets"
        if assets.is_dir():
            app.mount("/assets", StaticFiles(directory=str(assets)), name="assets")

        @app.get("/", include_in_schema=False)
        async def _index() -> FileResponse:  # pragma: no cover - needs a built dist
            return FileResponse(str(index))

        @app.get("/{path:path}", include_in_schema=False)
        async def _spa(path: str) -> FileResponse:  # pragma: no cover
            # Unknown API paths stay API errors: JSON 404, never the SPA
            # shell. Without this guard a typo or a decoded traversal attempt
            # under /api/ would fall through to index.html and look like a
            # successful page load instead of a 404.
            if path == "api" or path.startswith("api/"):
                raise NotFoundError("No such endpoint.")
            candidate = (dist / path).resolve()
            if candidate.is_file() and candidate.is_relative_to(dist.resolve()):
                return FileResponse(str(candidate))
            return FileResponse(str(index))
    else:

        @app.get("/", include_in_schema=False)
        async def _status(request: Request) -> JSONResponse:
            settings_obj: Settings = request.app.state.settings
            db: Database = request.app.state.db
            from app.services import diagnostics

            payload = diagnostics.health_payload(settings_obj)
            return JSONResponse(
                {
                    "status": "frontend_not_built",
                    "message": (
                        "The web interface has not been built yet. "
                        "Run .\\run.ps1 to build and start it, or use the API directly."
                    ),
                    "api_base": API_PREFIX,
                    "health": payload,
                    "job_counts": db.job_counts(),
                    "endpoints": {
                        "health": f"{API_PREFIX}/health",
                        "diagnostics": f"{API_PREFIX}/diagnostics",
                        "docs": f"{API_PREFIX}/docs",
                    },
                }
            )


app = create_app()


def run() -> None:  # pragma: no cover - manual entry point
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        log_level="info",
    )


if __name__ == "__main__":  # pragma: no cover
    run()
