"""Render job lifecycle tests: queueing, honest failure without Manim, recovery."""

from __future__ import annotations

import time


def _import_lesson(client, valid_markdown) -> str:
    return client.post(
        "/api/v1/lessons", json={"markdown": valid_markdown, "filename": "a.md"}
    ).json()["lesson_id"]


def _wait_terminal(client, job_id: str, timeout: float = 30.0) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        job = client.get(f"/api/v1/jobs/{job_id}").json()
        if job["status"] in ("completed", "failed", "cancelled"):
            return job
        time.sleep(0.25)
    raise AssertionError(f"job {job_id} did not settle in {timeout}s: {job}")


def test_create_job_requires_valid_lesson(client, valid_markdown):
    lesson_id = _import_lesson(client, valid_markdown)
    r = client.post(f"/api/v1/lessons/{lesson_id}/jobs", json={"quality": "preview"})
    assert r.status_code == 202
    job = r.json()
    assert job["status"] == "queued"
    assert job["settings"]["quality"] == "preview"


def test_job_settles_honestly_without_manim(client, valid_markdown):
    """Without Manim installed the job must fail with a clear, honest reason."""
    lesson_id = _import_lesson(client, valid_markdown)
    job_id = client.post(
        f"/api/v1/lessons/{lesson_id}/jobs", json={"quality": "preview"}
    ).json()["job_id"]
    job = _wait_terminal(client, job_id)

    # Either Manim is genuinely absent (honest failure) or it rendered
    # (completed). Never stuck, never fabricated progress.
    assert job["status"] in ("failed", "completed")
    if job["status"] == "failed":
        assert job["error_summary"], "a failed job must explain itself"
        assert job["technical_detail"], "a failed job must attach detail"
        assert job["progress"] is None
    else:
        assert job["output_path"]


def test_job_logs_are_available(client, valid_markdown):
    lesson_id = _import_lesson(client, valid_markdown)
    job_id = client.post(
        f"/api/v1/lessons/{lesson_id}/jobs", json={"quality": "preview"}
    ).json()["job_id"]
    _wait_terminal(client, job_id)
    logs = client.get(f"/api/v1/jobs/{job_id}/logs").json()
    assert logs["job_id"] == job_id
    assert isinstance(logs["truncated"], bool)


def test_cancel_queued_job(client, valid_markdown):
    lesson_id = _import_lesson(client, valid_markdown)
    job_id = client.post(
        f"/api/v1/lessons/{lesson_id}/jobs", json={"quality": "preview"}
    ).json()["job_id"]
    r = client.post(f"/api/v1/jobs/{job_id}/cancel")
    assert r.status_code == 200
    assert r.json()["status"] in ("cancelled", "cancelling", "failed", "completed")


def test_retry_only_for_failed_or_cancelled(client, valid_markdown):
    lesson_id = _import_lesson(client, valid_markdown)
    job_id = client.post(
        f"/api/v1/lessons/{lesson_id}/jobs", json={"quality": "preview"}
    ).json()["job_id"]
    job = _wait_terminal(client, job_id)
    if job["status"] == "failed":
        retry = client.post(f"/api/v1/jobs/{job_id}/retry")
        assert retry.status_code == 202
        assert retry.json()["attempt"] >= 2
    else:  # Manim present: a completed job cannot be retried
        assert client.post(f"/api/v1/jobs/{job_id}/retry").status_code == 409


def test_video_endpoints_404_without_output(client, valid_markdown):
    lesson_id = _import_lesson(client, valid_markdown)
    job_id = client.post(
        f"/api/v1/lessons/{lesson_id}/jobs", json={"quality": "preview"}
    ).json()["job_id"]
    _wait_terminal(client, job_id)
    assert client.get(f"/api/v1/media/{job_id}/video").status_code == 404
    assert client.get(f"/api/v1/media/{job_id}/download").status_code == 404


def test_job_404_for_unknown_id(client):
    assert client.get("/api/v1/jobs/nope").status_code == 404
    assert client.get("/api/v1/jobs/nope/logs").status_code == 404


def test_restart_recovery_marks_active_jobs_interrupted(db, settings):
    """A restart must never mark an in-flight job completed."""
    import asyncio

    from app.rendering.worker import RenderWorker

    lesson_id = db.create_lesson(
        filename="a.md", markdown="# x", report=None, summary=None
    )
    running = db.create_job(lesson_id=lesson_id, quality="preview", aspect_ratio="16:9", frame_rate=15)
    queued = db.create_job(lesson_id=lesson_id, quality="preview", aspect_ratio="16:9", frame_rate=15)
    db.update_job(running, status="rendering", phase="Rendering")

    async def _start_worker():
        worker = RenderWorker(settings, db)
        await worker.start()
        await worker.stop()

    asyncio.run(_start_worker())

    assert db.get_job(running)["status"] == "failed"
    assert "interrupted" in (db.get_job(running)["error_summary"] or "").lower()
    # queued jobs are re-enqueued, not failed
    assert db.get_job(queued)["status"] == "queued"
