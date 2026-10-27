"""Schema documentation and example scene endpoints."""

from __future__ import annotations

import json
import re
from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import get_app_settings
from app.core.config import SCENE_FORMAT_VERSION, Settings
from app.core.errors import NotFoundError
from app.core.security import safe_join
from app.schemas.api import (
    ExampleContentResponse,
    ExampleListItem,
    ExampleListResponse,
    SchemaReferenceResponse,
)
from app.schemas.scene import ACTIONS, FRAMES, OBJECT_KINDS, PALETTE

router = APIRouter(tags=["reference"])

_EXAMPLE_NAME = re.compile(r"^[a-z0-9][a-z0-9._-]*\.md$")


def _load_schema(settings: Settings, name: str) -> dict[str, Any]:
    path = safe_join(settings.schema_dir, name)
    if not path.is_file():
        raise NotFoundError("The schema file is missing from this installation.")
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _front_matter_field(markdown: str, key: str) -> str:
    """Best-effort scalar read from the YAML front matter (display only)."""
    in_fm = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped == "---":
            if in_fm:
                break
            in_fm = True
            continue
        if in_fm and stripped.startswith(f"{key}:"):
            return stripped.split(":", 1)[1].strip().strip("\"'")
    return ""


@router.get("/reference/schema", response_model=SchemaReferenceResponse)
def schema_reference(settings: Settings = Depends(get_app_settings)) -> dict:
    """The frozen Scene format reference the frontend renders as help text."""
    return {
        "scene_format_version": SCENE_FORMAT_VERSION,
        "specification": "prompts/SCENE_FORMAT_SPEC.md",
        "object_kinds": list(OBJECT_KINDS),
        "actions": list(ACTIONS),
        "colors": sorted(PALETTE),
        "frames": {k: list(v) for k, v in FRAMES.items()},
        "lesson_schema": _load_schema(settings, "lesson-metadata-v1.schema.json"),
        "scene_schema": _load_schema(settings, "scene-v1.schema.json"),
    }


@router.get("/reference/examples", response_model=ExampleListResponse)
def list_examples(settings: Settings = Depends(get_app_settings)) -> dict:
    examples_dir = settings.examples_dir
    if not examples_dir.is_dir():
        return {"examples": []}
    items: list[ExampleListItem] = []
    for path in sorted(examples_dir.glob("*.md")):
        if not _EXAMPLE_NAME.match(path.name):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:  # pragma: no cover - unreadable file
            continue
        items.append(
            ExampleListItem(
                name=path.name,
                title=_front_matter_field(text, "title") or path.stem,
                topic=_front_matter_field(text, "topic"),
                grade=_front_matter_field(text, "grade"),
                size_bytes=path.stat().st_size,
            )
        )
    return {"examples": items}


@router.get("/reference/examples/{name}", response_model=ExampleContentResponse)
def get_example(name: str, settings: Settings = Depends(get_app_settings)) -> dict:
    if not _EXAMPLE_NAME.match(name):
        raise NotFoundError("No example with that name.")
    path = safe_join(settings.examples_dir, name)
    if not path.is_file():
        raise NotFoundError("No example with that name.")
    return {"name": name, "markdown": path.read_text(encoding="utf-8")}
