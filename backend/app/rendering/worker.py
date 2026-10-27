"""Subprocess render worker (stages 12-14): bounded, cancellable, restart-safe.

Renders never run on the FastAPI event loop: each job is a child process
(``python -m manim render ...``) driven by :class:`RenderWorker`, which runs
a bounded number of jobs concurrently (``Settings.max_concurrent_renders``).

Honesty rules (``MASTER-PROMPT.md`` section 8):

* progress is ``None``/indeterminate — Manim's CLI does not expose a
  machine-readable percentage, so none is fabricated;
* a job only reaches ``completed`` after the output file is found, is
  non-empty, and is readable;
* a restart marks in-flight jobs ``failed`` with an explicit
  "interrupted" reason, never ``completed``.

The worker subprocesses get ``app`` on ``PYTHONPATH`` via the repository's
``backend/`` directory and run with the *same* interpreter as the backend
(:data:`sys.executable`), so Manim is looked up in the virtual environment
the backend itself runs in.
"""

from __future__ import annotations

import asyncio
import os
import shutil
import sys
from pathlib import Path
from typing import Any

from app.core.config import BACKEND_ROOT, Settings
from app.core.logging import get_logger
from app.rendering.compiler import compile_document
from app.rendering.layouts import RenderPlan
from app.schemas.scene import QUALITIES
from app.storage import files
from app.storage.database import Database, now_iso
from app.validation.pipeline import validate_bytes

log = get_logger("render.worker")

# Job lifecycle states this worker moves through (MASTER-PROMPT.md section 8).
STATE_QUEUED = "queued"
STATE_VALIDATING = "validating"
STATE_PREPARING = "preparing"
STATE_RENDERING = "rendering"
STATE_POSTPROCESSING = "postprocessing"
STATE_COMPLETED = "completed"
STATE_FAILED = "failed"
STATE_CANCELLING = "cancelling"
STATE_CANCELLED = "cancelled"

ACTIVE_STATES = (
    STATE_QUEUED, STATE_VALIDATING, STATE_PREPARING,
    STATE_RENDERING, STATE_POSTPROCESSING, STATE_CANCELLING,
)

# Teacher-facing failure summaries keyed by a stable reason code.
_FAILURE_SUMMARY = {
    "validation": "The lesson failed validation, so it was not rendered.",
    "compile": "The scene could not be generated from the lesson.",
    "manim_missing": "Manim is not installed, so videos cannot be rendered yet.",
    "render": "Manim could not render this scene.",
    "timeout": "Rendering took too long and was stopped.",
    "no_output": "The render finished but produced no video file.",
    "interrupted": "This render was interrupted when the application closed.",
    "cancelled": "This render was cancelled.",
}


class RenderWorker:
    """Asyncio-driven queue of subprocess renders with bounded concurrency."""

    def __init__(self, settings: Settings, db: Database) -> None:
        self.settings = settings
        self.db = db
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._tasks: list[asyncio.Task] = []
        self._procs: dict[str, asyncio.subprocess.Process] = {}
        self._cancel_requested: set[str] = set()
        self._running = False

    # --- lifecycle -------------------------------------------------------
    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        recovered = self.db.recover_interrupted_jobs()
        if recovered:
            log.warning("marked %d interrupted job(s) as failed at startup", recovered)
        self._requeue_persisted()
        for i in range(self.settings.max_concurrent_renders):
            self._tasks.append(asyncio.create_task(self._consumer(i), name=f"render-{i}"))
        log.info("render worker started with %d consumer(s)", len(self._tasks))

    def _requeue_persisted(self) -> None:
        """Re-enqueue jobs that were queued when the backend stopped."""
        for job in self.db.list_jobs(limit=500):
            if job["status"] == STATE_QUEUED:
                self._queue.put_nowait(job["job_id"])

    async def stop(self) -> None:
        self._running = False
        for job_id, proc in list(self._procs.items()):
            self._terminate(proc)
            log.info("terminated render subprocess for job %s on shutdown", job_id)
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        self._procs.clear()

    # --- public API ------------------------------------------------------
    def submit(self, job_id: str) -> None:
        self._queue.put_nowait(job_id)

    async def cancel(self, job_id: str) -> str:
        """Request cancellation; returns the job's state after the request."""
        job = self.db.get_job(job_id)
        if job is None:
            return "unknown"
        status = job["status"]
        if status in (STATE_COMPLETED, STATE_FAILED, STATE_CANCELLED):
            return status
        self._cancel_requested.add(job_id)
        if status == STATE_QUEUED:
            # Not started yet: settle it immediately, the consumer will skip it.
            self.db.update_job(
                job_id, status=STATE_CANCELLED, phase="Cancelled",
                finished_at=now_iso(),
            )
            return STATE_CANCELLED
        self.db.update_job(job_id, status=STATE_CANCELLING, phase="Cancelling")
        proc = self._procs.get(job_id)
        if proc is not None:
            self._terminate(proc)
        return STATE_CANCELLING

    # --- internals -------------------------------------------------------
    async def _consumer(self, index: int) -> None:
        while True:
            job_id = await self._queue.get()
            try:
                await self._run_job(job_id)
            except asyncio.CancelledError:
                raise
            except Exception:  # noqa: BLE001 - a crash must not kill the consumer
                log.exception("render job %s crashed the consumer path", job_id)
                self._fail(job_id, "render", detail="Unexpected worker error; see backend.log.")
            finally:
                self._queue.task_done()

    def _cancelling(self, job_id: str) -> bool:
        return job_id in self._cancel_requested or (
            (job := self.db.get_job(job_id)) is not None
            and job["status"] == STATE_CANCELLING
        )

    def _set(self, job_id: str, status: str, phase: str, **fields: Any) -> None:
        self.db.update_job(job_id, status=status, phase=phase, **fields)

    def _fail(self, job_id: str, reason: str, *, detail: str | None = None, **fields: Any) -> None:
        self._cancel_requested.discard(job_id)
        self.db.update_job(
            job_id,
            status=STATE_FAILED,
            phase="Failed",
            error_summary=_FAILURE_SUMMARY.get(reason, "Rendering failed."),
            technical_detail=detail,
            finished_at=now_iso(),
            progress=None,
            determinate=0,
            **fields,
        )
        log.info("job %s failed (%s): %s", job_id, reason, detail or "")

    async def _run_job(self, job_id: str) -> None:
        job = self.db.get_job(job_id)
        if job is None or job["status"] not in (STATE_QUEUED, STATE_VALIDATING):
            return  # cancelled while queued, or already handled
        if self._cancelling(job_id):
            self._mark_cancelled(job_id)
            return

        lesson = self.db.get_lesson(job["lesson_id"])
        if lesson is None:
            self._fail(job_id, "validation", detail="The lesson no longer exists.")
            return

        # --- stage 10-11: validate + generate (trusted path) --------------
        self._set(job_id, STATE_VALIDATING, "Validating", started_at=now_iso())
        try:
            source = files.read_source(self.settings, job["lesson_id"])
        except (FileNotFoundError, OSError) as exc:
            self._fail(job_id, "validation", detail=f"Lesson source unreadable: {exc}")
            return

        report, document = await asyncio.to_thread(
            validate_bytes, source.encode("utf-8"), filename=lesson["filename"], verify=True
        )
        if document is None or report.errors:
            first = report.errors[0].message if report.errors else "unknown error"
            self._fail(
                job_id, "validation",
                detail=f"{len(report.errors)} validation error(s); first: {first}",
            )
            return

        quality = self._quality_for(job)
        aspect = job.get("aspect_ratio") or lesson.get("aspect_ratio") or "16:9"
        self._set(job_id, STATE_PREPARING, "Generating scene")
        try:
            compiled = await asyncio.to_thread(
                compile_document, document, aspect_ratio=aspect, quality=quality
            )
        except Exception as exc:  # noqa: BLE001 - surface as an honest failure
            self._fail(job_id, "compile", detail=f"{type(exc).__name__}: {exc}")
            return

        job_path = files.job_dir(self.settings, job_id)
        gen_path = files.write_generated_scene(self.settings, job_id, compiled.source)
        files.append_log(
            self.settings, job_id,
            f"[{now_iso()}] prepared {compiled.scene_count} scene(s), "
            f"{compiled.plan.resolution[0]}x{compiled.plan.resolution[1]}@"
            f"{compiled.plan.frame_rate}fps -> {gen_path.name}\n",
        )

        # --- stage 12: sandboxed subprocess render -------------------------
        if self._cancelling(job_id):
            self._mark_cancelled(job_id)
            return
        self._set(job_id, STATE_RENDERING, "Rendering", determinate=0, progress=None)

        result = await self._render_subprocess(job_id, gen_path, job_path, compiled.plan)
        if result == "cancelled":
            self._mark_cancelled(job_id)
            return
        if result is not None:  # an honest failure reason
            return

        # --- stage 13-14: verify, publish, complete ------------------------
        if self._cancelling(job_id):
            self._mark_cancelled(job_id)
            return
        self._set(job_id, STATE_POSTPROCESSING, "Verifying output")
        mp4 = self._find_output(job_path)
        if mp4 is None:
            self._fail(
                job_id, "no_output",
                detail="Manim exited successfully but no .mp4 was produced; see the render log.",
            )
            return
        try:
            out_dir = self._output_dir()
            published = files.publish_output(
                self.settings, out_dir, lesson["title"], job_id, mp4
            )
        except (OSError, ValueError) as exc:
            self._fail(job_id, "no_output", detail=f"Could not publish the video: {exc}")
            return

        files.cleanup_job_workdir(self.settings, job_id)
        self._cancel_requested.discard(job_id)
        self.db.update_job(
            job_id, status=STATE_COMPLETED, phase="Completed",
            output_path=str(published), finished_at=now_iso(),
            progress=1.0, determinate=1, error_summary=None, technical_detail=None,
        )
        self.db.touch_last_render(job["lesson_id"])
        files.append_log(self.settings, job_id, f"[{now_iso()}] completed -> {published.name}\n")
        log.info("job %s completed: %s", job_id, published)

    def _quality_for(self, job: dict[str, Any]) -> str:
        quality = job.get("quality") or "standard"
        return quality if quality in QUALITIES else "standard"

    def _output_dir(self) -> Path:
        """Configured output directory (settings table overrides the default)."""
        stored = self.db.get_settings().get("output_dir")
        if isinstance(stored, str) and stored.strip():
            return Path(stored).expanduser()
        return self.settings.default_output_dir

    async def _render_subprocess(
        self, job_id: str, gen_path: Path, job_path: Path, plan: RenderPlan
    ) -> str | None:
        """Run Manim as a child process. Returns None on success, else a reason."""
        if shutil.which("ffmpeg") is None:
            self._fail(
                job_id, "manim_missing",
                detail="FFmpeg was not found on PATH; Manim needs it to encode video.",
            )
            return "manim_missing"
        try:
            import manim  # noqa: F401 - availability probe in the backend env
        except ImportError:
            self._fail(
                job_id, "manim_missing",
                detail="Manim is not installed in the virtual environment "
                       "(install backend/requirements-render.txt).",
            )
            return "manim_missing"

        cmd = [
            sys.executable, "-m", "manim", "render",
            "--resolution", plan.resolution_flag(),
            "--frame_rate", str(plan.frame_rate),
            "--media_dir", str(job_path / "media"),
            "--disable_caching", "--flush_cache",
            "--progress_bar", "none",
            str(gen_path), "Lesson",
        ]
        env = dict(os.environ)
        env["PYTHONPATH"] = str(BACKEND_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        env.setdefault("PYTHONUTF8", "1")

        quality = plan.quality
        timeout = self.settings.render_timeout_s.get(quality, 1200)
        files.append_log(
            self.settings, job_id,
            f"[{now_iso()}] $ {' '.join(cmd[:8])} ... (timeout {timeout}s)\n",
        )

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(job_path),
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
        except OSError as exc:
            self._fail(job_id, "manim_missing", detail=f"Could not start Manim: {exc}")
            return "manim_missing"

        self._procs[job_id] = proc
        try:
            timed_out = await self._pump(job_id, proc, timeout)
        finally:
            self._procs.pop(job_id, None)

        if self._cancelling(job_id):
            return "cancelled"
        if timed_out:
            self._fail(
                job_id, "timeout",
                detail=f"Rendering exceeded the {timeout}s limit for {quality} quality "
                       "and was stopped.",
            )
            return "timeout"
        if proc.returncode != 0:
            self._fail(
                job_id, "render",
                detail=f"Manim exited with code {proc.returncode}. See the render log.",
            )
            return "render"
        return None

    async def _pump(
        self, job_id: str, proc: asyncio.subprocess.Process, timeout: int
    ) -> bool:
        """Stream child output to the job log; enforce timeout + cancellation.

        Returns True when the process was stopped for exceeding ``timeout``.
        """
        assert proc.stdout is not None
        deadline = asyncio.get_running_loop().time() + timeout
        while True:
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                self._terminate(proc)
                files.append_log(self.settings, job_id, "[worker] render timed out\n")
                return True
            try:
                line = await asyncio.wait_for(
                    proc.stdout.readline(), timeout=min(remaining, 2.0)
                )
            except TimeoutError:
                if self._cancelling(job_id):
                    self._terminate(proc)
                    files.append_log(self.settings, job_id, "[worker] render cancelled\n")
                    return False
                continue
            if not line:  # EOF
                await proc.wait()
                return False
            files.append_log(
                self.settings, job_id, line.decode("utf-8", errors="replace")
            )
            if self._cancelling(job_id):
                self._terminate(proc)
                files.append_log(self.settings, job_id, "[worker] render cancelled\n")
                return False

    def _terminate(self, proc: asyncio.subprocess.Process) -> None:
        try:
            proc.terminate()
        except ProcessLookupError:  # pragma: no cover - already exited
            return

    def _mark_cancelled(self, job_id: str) -> None:
        self._cancel_requested.discard(job_id)
        self.db.update_job(
            job_id, status=STATE_CANCELLED, phase="Cancelled",
            finished_at=now_iso(), progress=None, determinate=0,
        )
        files.append_log(self.settings, job_id, f"[{now_iso()}] cancelled\n")

    def _find_output(self, job_path: Path) -> Path | None:
        """Newest non-empty .mp4 under the job's media directory."""
        media = job_path / "media"
        if not media.is_dir():
            return None
        candidates = [
            p for p in media.rglob("*.mp4")
            if p.is_file() and p.stat().st_size > 0 and not p.name.endswith(".partial")
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda p: p.stat().st_mtime)


__all__ = [
    "ACTIVE_STATES", "RenderPlan", "RenderWorker",
    "STATE_CANCELLED", "STATE_CANCELLING", "STATE_COMPLETED",
    "STATE_FAILED", "STATE_POSTPROCESSING", "STATE_PREPARING",
    "STATE_QUEUED", "STATE_RENDERING", "STATE_VALIDATING",
]
