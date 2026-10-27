"""Structured application errors and consistent error responses.

Every error leaving the API has the same JSON shape::

    {"error": {"code": "...", "message": "...", "request_id": "...", "detail": ...}}

Teacher-facing messages are plain language; technical detail (stack traces,
field paths, stderr) is attached only under ``detail`` so the UI can put it
in an expandable diagnostics panel.
"""

from __future__ import annotations

from typing import Any


class AppError(Exception):
    """Base class for errors with a stable machine-readable code."""

    status_code = 400
    code = "bad_request"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        status_code: int | None = None,
        detail: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code
        self.detail = detail


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"


class PayloadTooLargeError(AppError):
    status_code = 413
    code = "file_too_large"


class UnprocessableError(AppError):
    """Validation failed or the request cannot be carried out as-is."""

    status_code = 422
    code = "validation_failed"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        detail: Any = None,
    ) -> None:
        super().__init__(message, code=code, status_code=422, detail=detail)


class ForbiddenError(AppError):
    status_code = 403
    code = "forbidden"


class RateLimitError(AppError):
    status_code = 429
    code = "rate_limited"


class DependencyMissingError(AppError):
    status_code = 503
    code = "dependency_missing"
