"""Video streaming and download endpoints.

Paths are resolved strictly inside the configured output directory via
:func:`app.core.security.safe_join`; the API never accepts an arbitrary
filesystem path from the client (``MASTER-PROMPT.md`` section 9).
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.api.deps import DatabaseDep, SettingsDep
from app.core.config import Settings
from app.core.errors import NotFoundError
from app.storage import files
from app.storage.database import Database

router = APIRouter(tags=["media"])

_VIDEO_TYPES = {".mp4": "video/mp4", ".webm": "video/webm", ".mov": "video/quicktime"}


def _output_for_job(db: Database, settings: Settings, job_id: str) -> Path:
    job = db.get_job(job_id)
    if job is None:
        raise NotFoundError("That render job was not found.")
    stored = job.get("output_path")
    if not stored:
        raise NotFoundError("This job has no finished video yet.")
    path = Path(stored)
    out_dir = settings.default_output_dir
    stored_setting = db.get_settings().get("output_dir")
    if isinstance(stored_setting, str) and stored_setting.strip():
        out_dir = Path(stored_setting).expanduser()
    # Confine to the output directory regardless of what the row claims.
    resolved = files.resolve_output_file(out_dir, path.name)
    if not resolved.is_file():
        raise NotFoundError("The video file is no longer on disk.")
    return resolved


@router.get("/media/{job_id}/video")
def stream_video(job_id: str, settings=SettingsDep, db=DatabaseDep) -> FileResponse:
    """Stream a finished render (used by the in-app player)."""
    path = _output_for_job(db, settings, job_id)
    media_type = _VIDEO_TYPES.get(path.suffix.lower(), "video/mp4")
    return FileResponse(path, media_type=media_type, filename=path.name)


@router.get("/media/{job_id}/download")
def download_video(job_id: str, settings=SettingsDep, db=DatabaseDep) -> FileResponse:
    """Download a finished render as a file attachment."""
    path = _output_for_job(db, settings, job_id)
    return FileResponse(
        path,
        media_type=_VIDEO_TYPES.get(path.suffix.lower(), "video/mp4"),
        filename=path.name,
        content_disposition_type="attachment",
    )
