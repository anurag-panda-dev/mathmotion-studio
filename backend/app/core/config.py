"""Application configuration.

Settings come from (in increasing priority):

1. Documented defaults rooted at the repository layout.
2. Environment variables (``MATHMOTION_*``) — used by the launcher and tests.
3. The persisted ``settings`` table (output directory, defaults) which is
   layered on top at runtime by :mod:`app.storage.database`.

The :class:`Settings` object itself is immutable per process; the launcher
never mutates it, and the Settings API persists teacher preferences in
SQLite rather than mutating process state.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

APP_NAME = "MathMotion Studio"
APP_VERSION = "0.1.0"
SCENE_FORMAT_VERSION = "1.0"

# backend/app/core/config.py -> parents[3] is the repository root.
REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPO_ROOT / "backend"


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_path(name: str) -> Path | None:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return None
    return Path(raw).expanduser()


@dataclass(frozen=True)
class Settings:
    """Process-level configuration for the backend service."""

    repo_root: Path = REPO_ROOT
    data_dir: Path = field(default_factory=lambda: REPO_ROOT / "data")
    default_output_dir: Path = field(default_factory=lambda: REPO_ROOT / "output")
    host: str = "127.0.0.1"
    port: int = 8765
    max_upload_bytes: int = 512 * 1024
    max_concurrent_renders: int = 1
    max_paste_chars: int = 512 * 1024
    render_timeout_s: dict[str, int] = field(
        default_factory=lambda: {"preview": 600, "standard": 1200, "high": 2400}
    )
    allowed_dev_origins: tuple[str, ...] = (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    )
    rate_limit_window_s: int = 60
    rate_limit_max_requests: int = 240
    keep_job_logs: bool = True

    # --- derived paths -------------------------------------------------
    @property
    def db_path(self) -> Path:
        return self.data_dir / "mathmotion.db"

    @property
    def logs_dir(self) -> Path:
        return self.data_dir / "logs"

    @property
    def jobs_dir(self) -> Path:
        return self.data_dir / "jobs"

    @property
    def sources_dir(self) -> Path:
        return self.data_dir / "sources"

    @property
    def run_state_path(self) -> Path:
        return self.data_dir / "run-state.json"

    @property
    def prompts_dir(self) -> Path:
        return self.repo_root / "prompts"

    @property
    def examples_dir(self) -> Path:
        return self.prompts_dir / "examples"

    @property
    def schema_dir(self) -> Path:
        return self.repo_root / "schema"

    @property
    def frontend_dist(self) -> Path:
        return self.repo_root / "frontend" / "dist"

    @property
    def allowed_origins(self) -> tuple[str, ...]:
        """CORS origins: the Vite dev server plus the served app itself."""
        served = (
            f"http://127.0.0.1:{self.port}",
            f"http://localhost:{self.port}",
            f"http://[::1]:{self.port}",
        )
        return tuple(dict.fromkeys((*self.allowed_dev_origins, *served)))

    def ensure_directories(self) -> None:
        for path in (self.data_dir, self.logs_dir, self.jobs_dir, self.sources_dir):
            path.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_env(cls) -> Settings:
        data_dir = _env_path("MATHMOTION_DATA_DIR") or (REPO_ROOT / "data")
        output_dir = _env_path("MATHMOTION_OUTPUT_DIR") or (REPO_ROOT / "output")
        return cls(
            data_dir=data_dir,
            default_output_dir=output_dir,
            host=os.environ.get("MATHMOTION_HOST", "127.0.0.1"),
            port=_env_int("MATHMOTION_PORT", 8765),
            max_concurrent_renders=max(1, _env_int("MATHMOTION_MAX_RENDERS", 1)),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()
