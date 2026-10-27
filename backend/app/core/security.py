"""Security helpers: origin checks, safe paths, and a local rate limiter.

MathMotion Studio is a loopback-only local service, so the threat model is
"another tab or another local process tries to drive the API without the
teacher's intent" and "a hostile scene.md tries to escape the data
directory". The controls here address both:

* ``OriginCheckMiddleware`` — state-changing requests must come from an
  origin the application itself serves (or the local dev server).
* :func:`safe_join` / :func:`safe_slug` — every filesystem path derived
  from untrusted content is confined to a configured root.
* :class:`RateLimiter` — a small sliding-window limiter for expensive
  endpoints (validation, import), appropriate for a single-user local app.
"""

from __future__ import annotations

import re
import threading
import time
from collections import deque
from pathlib import Path, PurePosixPath, PureWindowsPath
from urllib.parse import urlparse

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.errors import ForbiddenError, RateLimitError

STATE_CHANGING = frozenset({"POST", "PUT", "PATCH", "DELETE"})

_SLUG_RE = re.compile(r"[^a-z0-9]+")
_FILENAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def safe_slug(text: str, *, max_length: int = 60, fallback: str = "lesson") -> str:
    """Turn untrusted text into a safe filename fragment."""
    slug = _SLUG_RE.sub("-", text.lower()).strip("-")
    slug = slug[:max_length].strip("-")
    return slug or fallback


def safe_filename(name: str) -> str:
    """Validate a caller-supplied filename (no directories, safe charset)."""
    if not name or len(name) > 200:
        raise ForbiddenError("File name is missing or too long.")
    # Reject any directory component on either path grammar, plus traversal.
    if "/" in name or "\\" in name or ":" in name or ".." in name:
        raise ForbiddenError("File name must not contain a path.")
    if not _FILENAME_RE.match(name):
        raise ForbiddenError("File name contains unsupported characters.")
    return name


def safe_join(root: Path, *parts: str) -> Path:
    """Join untrusted path parts under ``root``; reject escapes.

    Uses the *root's* native path grammar and resolves symlinks before the
    containment check, so both ``../`` and alternate-Grammar traversal fail.
    """
    root_resolved = root.resolve()
    candidate = root_resolved
    for part in parts:
        # Reject traversal expressed with either separator grammar up front.
        if PurePosixPath(part).is_absolute() or PureWindowsPath(part).is_absolute():
            raise ForbiddenError("Absolute paths are not allowed.")
        if ".." in PurePosixPath(part).parts or ".." in PureWindowsPath(part).parts:
            raise ForbiddenError("Path traversal is not allowed.")
        candidate = candidate / part
    resolved = candidate.resolve()
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise ForbiddenError("Path escapes the allowed directory.")
    return resolved


def is_under(path: Path, root: Path) -> bool:
    try:
        resolved = path.resolve()
        root_resolved = root.resolve()
    except OSError:  # pragma: no cover - unresolvable paths are not allowed
        return False
    return resolved == root_resolved or root_resolved in resolved.parents


class OriginCheckMiddleware(BaseHTTPMiddleware):
    """Reject state-changing requests from unexpected browser origins.

    Requests without an ``Origin`` header (curl, the test client, plain
    navigation) are allowed: browsers always attach ``Origin`` on
    cross-origin state-changing fetches, which is the case being defended.
    """

    def __init__(self, app, allowed_origins: tuple[str, ...]):  # noqa: ANN001
        super().__init__(app)
        self._allowed = set(allowed_origins)

    async def dispatch(self, request: Request, call_next):  # noqa: ANN001, ANN201
        if request.method in STATE_CHANGING:
            origin = request.headers.get("origin")
            if origin and origin not in self._allowed and not self._is_same_origin(request, origin):
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": {
                            "code": "forbidden_origin",
                            "message": "Request blocked: it came from an unexpected origin.",
                            "request_id": getattr(request.state, "request_id", "-"),
                        }
                    },
                )
        return await call_next(request)

    @staticmethod
    def _is_same_origin(request: Request, origin: str) -> bool:
        parsed = urlparse(origin)
        host = request.headers.get("host", "")
        return parsed.netloc == host


class RateLimiter:
    """Sliding-window limiter, one bucket (single-user local application)."""

    def __init__(self, max_requests: int, window_s: int) -> None:
        self.max_requests = max_requests
        self.window_s = window_s
        self._hits: deque[float] = deque()
        self._lock = threading.Lock()

    def check(self) -> None:
        now = time.monotonic()
        with self._lock:
            while self._hits and now - self._hits[0] > self.window_s:
                self._hits.popleft()
            if len(self._hits) >= self.max_requests:
                raise RateLimitError(
                    "Too many requests in a short time. Wait a moment and try again."
                )
            self._hits.append(now)
