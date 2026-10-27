"""Lesson history: import, list, detail, source update, deletion."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import DatabaseDep, RateLimitDep, SettingsDep
from app.api.serializers import (
    job_to_model,
    lesson_to_list_item,
    loads_or_none,
    report_dict_to_model,
    report_to_model,
)
from app.core.errors import NotFoundError, PayloadTooLargeError
from app.core.security import safe_filename
from app.schemas.api import (
    ImportResponse,
    LessonDetail,
    LessonListItem,
    SourceUpdateRequest,
    ValidateRequest,
)
from app.storage import files
from app.storage.database import Database
from app.validation.pipeline import validate_source

router = APIRouter(tags=["lessons"])


def _get_lesson_or_404(db: Database, lesson_id: str) -> dict:
    lesson = db.get_lesson(lesson_id)
    if lesson is None:
        raise NotFoundError("That lesson was not found.")
    return lesson


@router.post("/lessons", response_model=ImportResponse, status_code=201)
def import_lesson(
    body: ValidateRequest,
    settings=SettingsDep,
    db=DatabaseDep,
    _: None = RateLimitDep,
) -> dict:
    """Validate and store a scene.md file as a lesson.

    Import succeeds even with errors (the teacher may be iterating), but the
    stored record carries the full report so rendering stays blocked.
    """
    raw_chars = len(body.markdown)
    if raw_chars > settings.max_paste_chars:
        raise PayloadTooLargeError(
            "The scene file is too large to import.",
            detail=f"{raw_chars} characters; limit is {settings.max_paste_chars}.",
        )
    filename = safe_filename(body.filename or "scene.md")
    report, _document = validate_source(
        body.markdown, filename=filename, verify=body.verify, settings=settings
    )
    lesson_id = db.create_lesson(
        filename=filename,
        markdown=body.markdown,
        report=_report_dict(report),
        summary=report.summary,
    )
    files.write_source(settings, lesson_id, body.markdown)
    return {
        "lesson_id": lesson_id,
        "filename": filename,
        "report": report_to_model(report).model_dump(),
    }


def _report_dict(report) -> dict:  # noqa: ANN001, ANN201
    return {
        "valid": report.ok,
        "schema_version": report.schema_version,
        "errors": [i.as_dict() for i in report.errors],
        "warnings": [i.as_dict() for i in report.warnings],
        "verification": [v.as_dict() for v in report.verification],
        "summary": report.summary,
    }


@router.get("/lessons", response_model=list[LessonListItem])
def list_lessons(
    search: str = "",
    sort: str = "created_desc",
    topic: str = "",
    grade: str = "",
    db=DatabaseDep,
) -> list[dict]:
    rows = db.list_lessons(search=search, sort=sort, topic=topic, grade=grade)
    out: list[dict] = []
    for row in rows:
        jobs = db.list_jobs(lesson_id=row["lesson_id"], limit=100)
        out.append(
            lesson_to_list_item(row, job_count=len(jobs)).model_dump()
        )
    return out


@router.get("/lessons/{lesson_id}", response_model=LessonDetail)
def get_lesson(lesson_id: str, settings=SettingsDep, db=DatabaseDep) -> dict:
    lesson = _get_lesson_or_404(db, lesson_id)
    item = lesson_to_list_item(lesson, job_count=len(db.list_jobs(lesson_id=lesson_id)))
    try:
        markdown = files.read_source(settings, lesson_id)
    except (FileNotFoundError, OSError):
        markdown = ""
    jobs = [
        job_to_model(j, lesson_title=lesson.get("title")).model_dump()
        for j in db.list_jobs(lesson_id=lesson_id)
    ]
    return {
        **item.model_dump(),
        "markdown": markdown,
        "report": report_dict_to_model(loads_or_none(lesson.get("last_report"))),
        "summary": loads_or_none(lesson.get("last_summary")),
        "jobs": jobs,
    }


@router.patch("/lessons/{lesson_id}/source", response_model=ImportResponse)
def update_source(
    lesson_id: str,
    body: SourceUpdateRequest,
    settings=SettingsDep,
    db=DatabaseDep,
    _: None = RateLimitDep,
) -> dict:
    """Replace a lesson's markdown and re-run validation."""
    lesson = _get_lesson_or_404(db, lesson_id)
    raw_chars = len(body.markdown)
    if raw_chars > settings.max_paste_chars:
        raise PayloadTooLargeError(
            "The scene file is too large.",
            detail=f"{raw_chars} characters; limit is {settings.max_paste_chars}.",
        )
    report, _document = validate_source(
        body.markdown, filename=lesson["filename"], verify=True, settings=settings
    )
    db.update_lesson_source(lesson_id, _report_dict(report), report.summary)
    files.write_source(settings, lesson_id, body.markdown)
    return {
        "lesson_id": lesson_id,
        "filename": lesson["filename"],
        "report": report_to_model(report).model_dump(),
    }


@router.delete("/lessons/{lesson_id}", status_code=204)
def delete_lesson(lesson_id: str, settings=SettingsDep, db=DatabaseDep) -> None:
    """Delete a lesson, its source, and its per-job directories."""
    _get_lesson_or_404(db, lesson_id)
    for job in db.list_jobs(lesson_id=lesson_id):
        files.delete_job_dir(settings, job["job_id"])
    files.delete_source(settings, lesson_id)
    db.delete_lesson(lesson_id)
