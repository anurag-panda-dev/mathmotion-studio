"""SQLite persistence: lessons, render jobs, and settings.

Metadata only — videos, logs, and generated code stay on the filesystem
(``docs/DATA_MODEL.md`` section 6). WAL mode plus a busy timeout keeps the
API threadpool and the render worker safe on one process.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_SCHEMA = """
CREATE TABLE IF NOT EXISTS lessons (
    lesson_id       TEXT PRIMARY KEY,
    filename        TEXT NOT NULL,
    title           TEXT NOT NULL DEFAULT '',
    topic           TEXT NOT NULL DEFAULT '',
    grade           TEXT NOT NULL DEFAULT '',
    language        TEXT NOT NULL DEFAULT '',
    schema_version  TEXT,
    duration_minutes REAL,
    aspect_ratio    TEXT,
    theme           TEXT,
    valid           INTEGER,
    error_count     INTEGER NOT NULL DEFAULT 0,
    warning_count   INTEGER NOT NULL DEFAULT 0,
    last_report     TEXT,
    last_summary    TEXT,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL,
    last_render_at  TEXT
);

CREATE TABLE IF NOT EXISTS render_jobs (
    job_id           TEXT PRIMARY KEY,
    lesson_id        TEXT NOT NULL REFERENCES lessons(lesson_id) ON DELETE CASCADE,
    status           TEXT NOT NULL,
    phase            TEXT NOT NULL DEFAULT '',
    progress         REAL,
    determinate      INTEGER NOT NULL DEFAULT 0,
    quality          TEXT NOT NULL,
    aspect_ratio     TEXT NOT NULL,
    frame_rate       INTEGER NOT NULL DEFAULT 30,
    output_path      TEXT,
    error_summary    TEXT,
    technical_detail TEXT,
    attempt          INTEGER NOT NULL DEFAULT 1,
    created_at       TEXT NOT NULL,
    started_at       TEXT,
    finished_at      TEXT,
    updated_at       TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_jobs_lesson ON render_jobs(lesson_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON render_jobs(status);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def new_id() -> str:
    return uuid.uuid4().hex


class Database:
    """Thin, thread-safe SQLite facade for the local application."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            conn = sqlite3.connect(self.path, timeout=30)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA busy_timeout=5000")
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    def init(self) -> None:
        with self.connect() as conn:
            conn.executescript(_SCHEMA)

    # --- lessons ---------------------------------------------------------
    def create_lesson(
        self,
        *,
        filename: str,
        markdown: str,
        report: dict[str, Any] | None,
        summary: dict[str, Any] | None,
    ) -> str:
        lesson_id = new_id()
        ts = now_iso()
        title = (summary or {}).get("title") or _title_from_markdown(markdown)
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO lessons (
                    lesson_id, filename, title, topic, grade, language, schema_version,
                    duration_minutes, aspect_ratio, theme, valid, error_count,
                    warning_count, last_report, last_summary, created_at, updated_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    lesson_id,
                    filename,
                    title,
                    (summary or {}).get("topic", ""),
                    (summary or {}).get("grade", ""),
                    (summary or {}).get("language", ""),
                    (report or {}).get("schema_version"),
                    (summary or {}).get("duration_minutes"),
                    (summary or {}).get("aspect_ratio"),
                    (summary or {}).get("theme"),
                    None
                    if report is None
                    else (1 if report.get("valid") else 0),
                    len((report or {}).get("errors", [])),
                    len((report or {}).get("warnings", [])),
                    json.dumps(report) if report is not None else None,
                    json.dumps(summary) if summary is not None else None,
                    ts,
                    ts,
                ),
            )
        return lesson_id

    def update_lesson_source(
        self, lesson_id: str, report: dict[str, Any] | None, summary: dict[str, Any] | None
    ) -> bool:
        summary = summary or {}
        with self.connect() as conn:
            cur = conn.execute(
                """
                UPDATE lessons SET
                    title=?, topic=?, grade=?, language=?, schema_version=?,
                    duration_minutes=?, aspect_ratio=?, theme=?, valid=?,
                    error_count=?, warning_count=?, last_report=?, last_summary=?,
                    updated_at=?
                WHERE lesson_id=?
                """,
                (
                    summary.get("title") or "",
                    summary.get("topic", ""),
                    summary.get("grade", ""),
                    summary.get("language", ""),
                    (report or {}).get("schema_version"),
                    summary.get("duration_minutes"),
                    summary.get("aspect_ratio"),
                    summary.get("theme"),
                    None if report is None else (1 if report.get("valid") else 0),
                    len((report or {}).get("errors", [])),
                    len((report or {}).get("warnings", [])),
                    json.dumps(report) if report is not None else None,
                    json.dumps(summary) if summary is not None else None,
                    now_iso(),
                    lesson_id,
                ),
            )
            return cur.rowcount > 0

    def get_lesson(self, lesson_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM lessons WHERE lesson_id=?", (lesson_id,)).fetchone()
        return _row_to_dict(row) if row else None

    def list_lessons(
        self,
        *,
        search: str = "",
        sort: str = "created_desc",
        topic: str = "",
        grade: str = "",
    ) -> list[dict[str, Any]]:
        order = {
            "created_desc": "created_at DESC",
            "created_asc": "created_at ASC",
            "title_asc": "title COLLATE NOCASE ASC",
            "title_desc": "title COLLATE NOCASE DESC",
        }.get(sort, "created_at DESC")
        sql = "SELECT * FROM lessons"
        clauses: list[str] = []
        params: list[Any] = []
        if search:
            clauses.append("(title LIKE ? OR topic LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
        if topic:
            clauses.append("topic LIKE ?")
            params.append(f"%{topic}%")
        if grade:
            clauses.append("grade = ?")
            params.append(grade)
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += f" ORDER BY {order}"
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_row_to_dict(r) for r in rows]

    def delete_lesson(self, lesson_id: str) -> bool:
        with self.connect() as conn:
            cur = conn.execute("DELETE FROM lessons WHERE lesson_id=?", (lesson_id,))
            return cur.rowcount > 0

    def touch_last_render(self, lesson_id: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE lessons SET last_render_at=? WHERE lesson_id=?",
                (now_iso(), lesson_id),
            )

    # --- render jobs -----------------------------------------------------
    def create_job(
        self, *, lesson_id: str, quality: str, aspect_ratio: str, frame_rate: int
    ) -> str:
        job_id = new_id()
        ts = now_iso()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO render_jobs (
                    job_id, lesson_id, status, phase, quality, aspect_ratio,
                    frame_rate, attempt, created_at, updated_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?)
                """,
                (job_id, lesson_id, "queued", "Queued", quality, aspect_ratio,
                 frame_rate, 1, ts, ts),
            )
        return job_id

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM render_jobs WHERE job_id=?", (job_id,)).fetchone()
        return _row_to_dict(row) if row else None

    def list_jobs(self, *, lesson_id: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        with self.connect() as conn:
            if lesson_id:
                rows = conn.execute(
                    "SELECT * FROM render_jobs WHERE lesson_id=? ORDER BY created_at DESC LIMIT ?",
                    (lesson_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM render_jobs ORDER BY created_at DESC LIMIT ?", (limit,)
                ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def update_job(self, job_id: str, **fields: Any) -> None:
        if not fields:
            return
        fields["updated_at"] = now_iso()
        cols = ", ".join(f"{k}=?" for k in fields)
        with self.connect() as conn:
            conn.execute(
                f"UPDATE render_jobs SET {cols} WHERE job_id=?",
                (*fields.values(), job_id),
            )

    def job_counts(self) -> dict[str, int]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT status, COUNT(*) AS n FROM render_jobs GROUP BY status"
            ).fetchall()
        return {r["status"]: r["n"] for r in rows}

    def recover_interrupted_jobs(self) -> int:
        """Mark in-flight jobs left active by a restart as failed (never 'completed').

        Only states that were actively being worked are interrupted: a job that
        was merely ``queued`` never started, so it is left alone and re-enqueued
        by the render worker instead of being failed.
        """
        in_flight = (
            "validating", "preparing", "rendering", "postprocessing", "cancelling"
        )
        ts = now_iso()
        with self.connect() as conn:
            cur = conn.execute(
                f"""
                UPDATE render_jobs
                SET status='failed', phase='Interrupted',
                    error_summary='This render was interrupted when the application closed.',
                    technical_detail='Job was in an active state at backend startup and was failed explicitly.',
                    finished_at=?, updated_at=?
                WHERE status IN ({",".join("?" * len(in_flight))})
                """,
                (ts, ts, *in_flight),
            )
            return cur.rowcount

    # --- settings --------------------------------------------------------
    def get_settings(self) -> dict[str, Any]:
        with self.connect() as conn:
            rows = conn.execute("SELECT key, value FROM settings").fetchall()
        out: dict[str, Any] = {}
        for row in rows:
            try:
                out[row["key"]] = json.loads(row["value"])
            except json.JSONDecodeError:  # pragma: no cover - corrupt row
                out[row["key"]] = row["value"]
        return out

    def set_setting(self, key: str, value: Any) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, json.dumps(value)),
            )


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def _title_from_markdown(markdown: str) -> str:
    """Fallback title when front matter could not be parsed."""
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()[:140]
        if stripped:
            continue
    return "Untitled lesson"
