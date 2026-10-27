"""Scene validation endpoint (dry-run check without importing a lesson)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import RateLimitDep, get_app_settings
from app.api.serializers import report_to_model
from app.core.config import Settings
from app.core.errors import PayloadTooLargeError
from app.schemas.api import ValidateRequest, ValidationReportResponse
from app.validation.pipeline import validate_source

router = APIRouter(tags=["scenes"])


@router.post("/scenes/validate", response_model=ValidationReportResponse)
def validate_scene(
    body: ValidateRequest,
    settings: Settings = Depends(get_app_settings),
    _: None = RateLimitDep,
) -> dict:
    """Validate pasted scene.md content without saving it.

    Errors and warnings are returned separately; the lesson is not stored.
    """
    raw_chars = len(body.markdown)
    if raw_chars > settings.max_paste_chars:
        raise PayloadTooLargeError(
            "The pasted scene is too large to check in one request.",
            detail=f"{raw_chars} characters; limit is {settings.max_paste_chars}.",
        )
    report, _document = validate_source(
        body.markdown,
        filename=body.filename or "scene.md",
        verify=body.verify,
        settings=settings,
    )
    return report_to_model(report).model_dump()
