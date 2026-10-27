"""Render job endpoints: create, status, logs, cancel, retry."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import DatabaseDep, SettingsDep, WorkerDep
from app.api.serializers import job_to_model
from app.core.errors import ConflictError, NotFoundError, UnprocessableError
from app.rendering.worker import RenderWorker
from app.schemas.api import (
    CancelResponse,
    CreateJobRequest,
    JobListResponse,
    JobStatusModel,
    LogsResponse,
)
from app.schemas.scene import FRAMES, QUALITIES, QUALITY_FRAME_RATES
from app.storage import files
from app.storage.database import Database

router = APIRouter(tags=["jobs"])


def _job_or_404(db: Database, job_id: str) -> dict:
    job = db.get_job(job_id)
    if job is None:
        raise NotFoundError("That render job was not found.")
    return job


def _lesson_valid_for_render(db: Database, lesson: dict) -> None:
    if lesson.get("valid") != 1:
        raise UnprocessableError(
            "This lesson has validation errors, so it cannot be rendered.",
            code="lesson_invalid",
            detail="Fix the errors listed on the lesson page, then try again.",
        )


@router.post("/lessons/{lesson_id}/jobs", response_model=JobStatusModel, status_code=202)
def create_job(
    lesson_id: str,
    body: CreateJobRequest,
    db=DatabaseDep,
    worker: RenderWorker = WorkerDep,
) -> dict:
    """Queue a render job for a valid lesson."""
    lesson = db.get_lesson(lesson_id)
    if lesson is None:
        raise NotFoundError("That lesson was not found.")
    _lesson_valid_for_render(db, lesson)

    quality = body.quality or db.get_settings().get("default_quality") or "standard"
    if quality not in QUALITIES:
        quality = "standard"
    aspect = body.aspect_ratio or lesson.get("aspect_ratio") or "16:9"
    if aspect not in FRAMES:
        aspect = "16:9"

    job_id = db.create_job(
        lesson_id=lesson_id,
        quality=quality,
        aspect_ratio=aspect,
        frame_rate=QUALITY_FRAME_RATES[quality],
    )
    worker.submit(job_id)
    job = _job_or_404(db, job_id)
    return job_to_model(job, lesson_title=lesson.get("title")).model_dump()


@router.get("/jobs", response_model=JobListResponse)
def list_jobs(lesson_id: str | None = None, db=DatabaseDep) -> dict:
    jobs = db.list_jobs(lesson_id=lesson_id, limit=200)
    return {
        "jobs": [
            job_to_model(
                j,
                lesson_title=(db.get_lesson(j["lesson_id"]) or {}).get("title"),
            ).model_dump()
            for j in jobs
        ]
    }


@router.get("/jobs/{job_id}", response_model=JobStatusModel)
def job_status(job_id: str, db=DatabaseDep) -> dict:
    job = _job_or_404(db, job_id)
    lesson = db.get_lesson(job["lesson_id"]) or {}
    output_url = f"/api/v1/media/{job_id}/video" if job.get("output_path") else None
    return job_to_model(job, lesson_title=lesson.get("title"), output_url=output_url).model_dump()


@router.get("/jobs/{job_id}/logs", response_model=LogsResponse)
def job_logs(job_id: str, settings=SettingsDep, db=DatabaseDep) -> dict:
    _job_or_404(db, job_id)
    text, truncated = files.read_logs(settings, job_id)
    return {"job_id": job_id, "logs": text, "truncated": truncated}


@router.post("/jobs/{job_id}/cancel", response_model=CancelResponse)
async def cancel_job(
    job_id: str, db=DatabaseDep, worker: RenderWorker = WorkerDep
) -> dict:
    _job_or_404(db, job_id)  # 404 guard before cancelling
    status = await worker.cancel(job_id)
    if status == "unknown":  # pragma: no cover - row vanished mid-request
        raise NotFoundError("That render job was not found.")
    return {"job_id": job_id, "status": status}


@router.post("/jobs/{job_id}/retry", response_model=JobStatusModel, status_code=202)
def retry_job(
    job_id: str,
    db=DatabaseDep,
    worker: RenderWorker = WorkerDep,
) -> dict:
    """Re-queue a failed or cancelled job with the same settings."""
    job = _job_or_404(db, job_id)
    if job["status"] not in ("failed", "cancelled"):
        raise ConflictError(
            "Only failed or cancelled jobs can be retried.",
            detail=f"Job is currently {job['status']}.",
        )
    lesson = db.get_lesson(job["lesson_id"])
    if lesson is None:
        raise NotFoundError("The lesson for this job no longer exists.")
    _lesson_valid_for_render(db, lesson)

    new_id = db.create_job(
        lesson_id=job["lesson_id"],
        quality=job["quality"],
        aspect_ratio=job["aspect_ratio"],
        frame_rate=int(job["frame_rate"] or 30),
    )
    db.update_job(new_id, attempt=int(job.get("attempt") or 1) + 1)
    worker.submit(new_id)
    return job_to_model(_job_or_404(db, new_id), lesson_title=lesson.get("title")).model_dump()
