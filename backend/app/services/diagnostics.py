"""Dependency health checks and storage accounting for the Settings page.

Answers honestly: an unavailable optional dependency (LaTeX, or Manim
itself before rendering is set up) is reported as *unavailable* with the
feature it affects — never as an error, never faked as installed.
"""

from __future__ import annotations

import importlib.util
import platform
import shutil
import subprocess
import sys
from importlib import metadata
from pathlib import Path

from app.core.config import APP_VERSION, SCENE_FORMAT_VERSION, Settings

_REQUIRED_FOR = {
    "manim": "rendering animations",
    "ffmpeg": "producing MP4 video (used by Manim)",
    "latex": "high-quality LaTeX typography for formula objects (optional)",
}


def _package_version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def check_manim() -> dict[str, object]:
    available = importlib.util.find_spec("manim") is not None
    return {
        "name": "manim",
        "available": available,
        "version": _package_version("manim") if available else None,
        "detail": None if available else "Manim is not installed in the virtual environment.",
        "required_for": _REQUIRED_FOR["manim"],
    }


def check_ffmpeg() -> dict[str, object]:
    path = shutil.which("ffmpeg")
    version = None
    if path:
        try:
            out = subprocess.run(
                [path, "-version"], capture_output=True, text=True, timeout=10, check=False
            )
            version = (out.stdout or "").splitlines()[0] if out.stdout else None
        except (OSError, subprocess.SubprocessError):  # pragma: no cover
            version = None
    return {
        "name": "ffmpeg",
        "available": path is not None,
        "version": version,
        "detail": None if path else "FFmpeg was not found on PATH.",
        "required_for": _REQUIRED_FOR["ffmpeg"],
    }


def check_latex() -> dict[str, object]:
    path = shutil.which("latex")
    detail = None
    if path:
        dvisvgm = shutil.which("dvisvgm")
        if dvisvgm is None:
            detail = "latex was found but dvisvgm is missing; MathTex may fail."
    else:
        detail = "LaTeX is not installed (optional — text fallback is used)."
    return {
        "name": "latex",
        "available": path is not None,
        "version": None,
        "detail": detail,
        "required_for": _REQUIRED_FOR["latex"],
    }


def dependency_statuses() -> list[dict[str, object]]:
    return [check_manim(), check_ffmpeg(), check_latex()]


def health_payload(settings: Settings) -> dict[str, object]:
    deps = dependency_statuses()
    return {
        "status": "ok" if all(d["available"] or d["name"] == "latex" for d in deps) else "degraded",
        "version": APP_VERSION,
        "scene_format_version": SCENE_FORMAT_VERSION,
        "python": platform.python_version(),
        "dependencies": deps,
        "frontend_built": (settings.frontend_dist / "index.html").is_file(),
        "directories": {
            "data": str(settings.data_dir),
            "output": str(settings.default_output_dir),
            "logs": str(settings.logs_dir),
            "repo": str(settings.repo_root),
        },
    }


def directory_size(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    for item in path.rglob("*"):
        try:
            if item.is_file():
                total += item.stat().st_size
        except OSError:  # pragma: no cover - files can vanish mid-walk
            continue
    return total


def storage_payload(settings: Settings) -> dict[str, int]:
    return {
        "data_bytes": directory_size(settings.data_dir),
        "output_bytes": directory_size(settings.default_output_dir),
        "total_bytes": directory_size(settings.data_dir) + directory_size(settings.default_output_dir),
    }


def python_executable() -> str:
    return sys.executable
