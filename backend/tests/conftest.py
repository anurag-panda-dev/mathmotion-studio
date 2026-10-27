"""Shared pytest fixtures: isolated app + database per test module."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = REPO_ROOT / "prompts" / "examples"
PYTHAGOREAN = EXAMPLES_DIR / "pythagorean-theorem.md"


@pytest.fixture()
def settings(tmp_path, monkeypatch):
    """Process-level Settings rooted at a temp directory (never the real data/)."""
    from app.core.config import Settings

    data = tmp_path / "data"
    output = tmp_path / "output"
    monkeypatch.setenv("MATHMOTION_DATA_DIR", str(data))
    monkeypatch.setenv("MATHMOTION_OUTPUT_DIR", str(output))
    s = Settings.from_env()
    s.ensure_directories()
    return s


@pytest.fixture()
def db(settings):
    from app.storage.database import Database

    database = Database(settings.db_path)
    database.init()
    return database


@pytest.fixture()
def client(settings):
    """TestClient over a real app instance (lifespan runs the worker)."""
    from fastapi.testclient import TestClient

    from app.main import create_app

    app = create_app(settings)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def valid_markdown() -> str:
    return PYTHAGOREAN.read_text(encoding="utf-8")


@pytest.fixture()
def examples_dir() -> Path:
    return EXAMPLES_DIR
