"""Logging setup and the request-ID middleware.

Full stack traces are written to the log file only — the JSON error payload
sent to the teacher never contains a traceback (MASTER-PROMPT.md section 9).
"""

from __future__ import annotations

import logging
import uuid
from logging.handlers import RotatingFileHandler
from pathlib import Path

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-ID"

_configured = False


def configure_logging(logs_dir: Path, *, level: int = logging.INFO) -> None:
    """Configure the root application logger once (idempotent)."""
    global _configured
    if _configured:
        return
    _configured = True

    logs_dir.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter(
        "%(asctime)s %(levelname)-7s %(name)s [%(request_id)s] %(message)s"
    )

    class _RequestIDFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:  # noqa: D102
            if not hasattr(record, "request_id"):
                record.request_id = "-"
            return True

    root = logging.getLogger("mathmotion")
    root.setLevel(level)

    # The request-id filter must live on the *handlers*, not the logger:
    # records from child loggers (mathmotion.*) propagate straight to the
    # handlers and never pass through ancestor logger filters.
    file_handler = RotatingFileHandler(
        logs_dir / "backend.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    file_handler.addFilter(_RequestIDFilter())
    root.addHandler(file_handler)

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("%(levelname)-7s %(name)s: %(message)s"))
    console.addFilter(_RequestIDFilter())
    root.addHandler(console)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"mathmotion.{name}")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Assigns a request id, stores it on the request, and echoes the header."""

    async def dispatch(self, request: Request, call_next):  # noqa: ANN001, ANN201
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex[:12]
        request.state.request_id = request_id
        try:
            response: Response = await call_next(request)
        except Exception:  # pragma: no cover - handled by exception handlers
            logging.getLogger("mathmotion.api").exception(
                "unhandled error", extra={"request_id": request_id}
            )
            raise
        response.headers[REQUEST_ID_HEADER] = request_id
        return response


def request_id_of(request: Request) -> str:
    return getattr(request.state, "request_id", "-")
