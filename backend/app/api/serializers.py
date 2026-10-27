"""Record -> API model mappers (one place, so routers stay thin)."""

from __future__ import annotations

import json
from typing import Any

from app.schemas.api import (
    JobStatusModel,
    LessonListItem,
    RenderSettingsModel,
    SceneSummary,
    ValidationReportResponse,
    VerificationResultModel,
)
from app.validation.issues import ValidationReport


def report_to_model(report: ValidationReport) -> ValidationReportResponse:
    return ValidationReportResponse(
        valid=report.ok,
        schema_version=report.schema_version,
        errors=[i.as_dict() for i in report.errors],
        warnings=[i.as_dict() for i in report.warnings],
        verification=[v.as_dict() for v in report.verification],
        summary=SceneSummary(**report.summary) if report.summary else None,
    )


def report_dict_to_model(data: dict[str, Any] | None) -> ValidationReportResponse | None:
    """Rehydrate a report previously stored as JSON in SQLite."""
    if not data:
        return None
    return ValidationReportResponse(
        valid=bool(data.get("valid", not data.get("errors"))),
        schema_version=data.get("schema_version"),
        errors=data.get("errors", []),
        warnings=data.get("warnings", []),
        verification=[VerificationResultModel(**v) for v in data.get("verification", [])],
        summary=SceneSummary(**data["summary"]) if data.get("summary") else None,
    )


def job_to_model(
    job: dict[str, Any], *, lesson_title: str | None = None, output_url: str | None = None
) -> JobStatusModel:
    determinate = bool(job.get("determinate"))
    progress = job.get("progress")
    return JobStatusModel(
        job_id=job["job_id"],
        lesson_id=job["lesson_id"],
        lesson_title=lesson_title,
        status=job["status"],
        progress=progress if determinate else None,
        determinate=determinate,
        phase=job.get("phase") or "",
        settings=RenderSettingsModel(
            quality=job.get("quality") or "standard",
            aspect_ratio=job.get("aspect_ratio") or "16:9",
            frame_rate=int(job.get("frame_rate") or 30),
        ),
        output_path=job.get("output_path"),
        output_url=output_url,
        error_summary=job.get("error_summary"),
        technical_detail=job.get("technical_detail"),
        attempt=int(job.get("attempt") or 1),
        created_at=job.get("created_at") or "",
        started_at=job.get("started_at"),
        finished_at=job.get("finished_at"),
    )


def _bool_or_none(value: Any) -> bool | None:
    if value is None:
        return None
    return bool(value)


def lesson_to_list_item(lesson: dict[str, Any], *, job_count: int = 0) -> LessonListItem:
    return LessonListItem(
        lesson_id=lesson["lesson_id"],
        title=lesson.get("title") or "",
        topic=lesson.get("topic") or "",
        grade=lesson.get("grade") or "",
        language=lesson.get("language") or "",
        schema_version=lesson.get("schema_version"),
        filename=lesson.get("filename") or "scene.md",
        valid=_bool_or_none(lesson.get("valid")),
        error_count=int(lesson.get("error_count") or 0),
        warning_count=int(lesson.get("warning_count") or 0),
        duration_minutes=lesson.get("duration_minutes"),
        aspect_ratio=lesson.get("aspect_ratio"),
        created_at=lesson.get("created_at") or "",
        updated_at=lesson.get("updated_at") or "",
        last_render_at=lesson.get("last_render_at"),
        job_count=job_count,
    )


def loads_or_none(raw: str | None) -> Any:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:  # pragma: no cover - corrupt row
        return None
