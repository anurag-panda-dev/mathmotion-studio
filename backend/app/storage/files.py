"""Filesystem storage: sources, per-job directories, logs, and MP4 output.

Path safety rules (``MASTER-PROMPT.md`` section 12):

* every path derived from untrusted content goes through
  :func:`app.core.security.safe_slug` / :func:`app.core.security.safe_join`;
* deletions are confined to the application directories (``data/`` and the
  configured ``output/``) — never outside;
* large binaries never enter SQLite.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from app.core.config import Settings
from app.core.security import safe_join, safe_slug

# --- lesson sources --------------------------------------------------------

def source_path(settings: Settings, lesson_id: str) -> Path:
    return safe_join(settings.sources_dir, f"{lesson_id}.md")


def write_source(settings: Settings, lesson_id: str, markdown: str) -> Path:
    path = source_path(settings, lesson_id)
    path.write_text(markdown, encoding="utf-8")
    return path


def read_source(settings: Settings, lesson_id: str) -> str:
    path = source_path(settings, lesson_id)
    if not path.is_file():
        raise FileNotFoundError(f"source not found for lesson {lesson_id}")
    return path.read_text(encoding="utf-8")


def delete_source(settings: Settings, lesson_id: str) -> None:
    path = source_path(settings, lesson_id)
    if path.is_file():
        path.unlink()


# --- per-job directories ---------------------------------------------------

def job_dir(settings: Settings, job_id: str, *, create: bool = True) -> Path:
    path = safe_join(settings.jobs_dir, job_id)
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def write_generated_scene(settings: Settings, job_id: str, source: str) -> Path:
    directory = job_dir(settings, job_id)
    path = directory / "generated_scene.py"
    path.write_text(source, encoding="utf-8")
    return path


def append_log(settings: Settings, job_id: str, text: str) -> None:
    if not text:
        return
    directory = job_dir(settings, job_id)
    with (directory / "job.log").open("a", encoding="utf-8") as fh:
        fh.write(text)


def read_logs(settings: Settings, job_id: str, *, max_bytes: int = 256 * 1024) -> tuple[str, bool]:
    """Return ``(log_text, truncated)`` — newest content, bounded size."""
    path = safe_join(settings.jobs_dir, job_id) / "job.log"
    if not path.is_file():
        return "", False
    data = path.read_bytes()
    if len(data) > max_bytes:
        return data[-max_bytes:].decode("utf-8", errors="replace"), True
    return data.decode("utf-8", errors="replace"), False


def cleanup_job_workdir(settings: Settings, job_id: str, *, keep_logs: bool = True) -> None:
    """Remove render intermediates; keep generated code and logs for diagnosis."""
    directory = settings.jobs_dir / job_id
    if not directory.is_dir():
        return
    for child in directory.iterdir():
        if child.name == "media":
            shutil.rmtree(child, ignore_errors=True)
        elif child.name.endswith((".partial", ".tmp")):
            child.unlink(missing_ok=True)


def delete_job_dir(settings: Settings, job_id: str) -> None:
    directory = settings.jobs_dir / job_id
    if directory.is_dir():
        shutil.rmtree(directory, ignore_errors=True)


# --- output ----------------------------------------------------------------

def publish_output(
    settings: Settings, output_dir: Path, lesson_title: str, job_id: str, source_mp4: Path
) -> Path:
    """Copy a verified render result to the output directory, safely named."""
    if not source_mp4.is_file() or source_mp4.stat().st_size == 0:
        raise ValueError("render produced no usable video file")
    slug = safe_slug(lesson_title, fallback="lesson")
    name = f"{slug}-{job_id[:8]}.mp4"
    target_dir = output_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    target = safe_join(target_dir, name)
    shutil.copyfile(source_mp4, target)
    return target


def resolve_output_file(output_dir: Path, filename: str) -> Path:
    """Resolve a filename inside the output directory (traversal-proof)."""
    return safe_join(output_dir, filename)


def open_in_explorer(path: Path) -> bool:
    """Open a folder in the OS file manager (Windows-first, honest failure)."""
    import os
    import sys

    if not path.exists():
        return False
    try:
        if sys.platform == "win32":
            os.startfile(str(path))  # noqa: S606 - fixed verb on a validated directory
            return True
        if sys.platform == "darwin":  # pragma: no cover
            import subprocess

            subprocess.run(["open", str(path)], check=False)
            return True
        return False  # pragma: no cover - Linux desktops vary
    except OSError:
        return False
