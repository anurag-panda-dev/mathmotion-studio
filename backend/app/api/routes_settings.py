"""Application settings: retrieval, updates, and safe output-folder opening."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter

from app.api.deps import DatabaseDep, SettingsDep
from app.core.config import Settings
from app.core.errors import UnprocessableError
from app.schemas.api import AppSettingsModel, AppSettingsPatch
from app.storage import files
from app.storage.database import Database

router = APIRouter(tags=["settings"])


def _current(db: Database, settings: Settings) -> dict:
    stored = db.get_settings()
    output_dir = stored.get("output_dir") or str(settings.default_output_dir)
    return {
        "output_dir": output_dir,
        "default_quality": stored.get("default_quality", "standard"),
        "default_aspect_ratio": stored.get("default_aspect_ratio", "16:9"),
        "theme": stored.get("theme", "system"),
        "language": stored.get("language", "English"),
    }


@router.get("/settings", response_model=AppSettingsModel)
def get_settings_endpoint(db=DatabaseDep, settings=SettingsDep) -> dict:
    return _current(db, settings)


@router.patch("/settings", response_model=AppSettingsModel)
def update_settings(
    body: AppSettingsPatch, db=DatabaseDep, settings=SettingsDep
) -> dict:
    """Persist teacher preferences (never mutates process state)."""
    updates = body.model_dump(exclude_none=True)
    if "output_dir" in updates:
        candidate = Path(updates["output_dir"]).expanduser()
        try:
            candidate.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise UnprocessableError(
                "That output folder could not be created or is not writable.",
                code="output_dir_invalid",
                detail=str(exc),
            ) from exc
        updates["output_dir"] = str(candidate.resolve())
    for key, value in updates.items():
        db.set_setting(key, value)
    return _current(db, settings)


@router.post("/settings/open-output")
def open_output(db=DatabaseDep, settings=SettingsDep) -> dict:
    """Open the output folder in the OS file manager (honest failure)."""
    stored = db.get_settings().get("output_dir")
    target = Path(stored).expanduser() if isinstance(stored, str) and stored.strip() else settings.default_output_dir
    target.mkdir(parents=True, exist_ok=True)
    opened = files.open_in_explorer(target)
    return {
        "opened": opened,
        "path": str(target),
        "detail": None if opened else "Could not open a file manager for this folder.",
    }
