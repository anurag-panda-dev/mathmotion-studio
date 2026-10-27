"""Prompt generation endpoint (External-AI prompt assembly)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import RateLimitDep, get_app_settings
from app.core.config import Settings
from app.schemas.api import PromptRequest, PromptResponse
from app.services.prompt_generator import PromptInputs, generate_prompt

router = APIRouter(tags=["prompt"])


@router.post("/prompt", response_model=PromptResponse)
def create_prompt(
    body: PromptRequest,
    settings: Settings = Depends(get_app_settings),
    _: None = RateLimitDep,
) -> dict:
    """Assemble the full and compact External-AI prompts from teacher inputs.

    The application never calls an AI itself; it produces the prompt the
    teacher carries to whichever External AI they choose.
    """
    inputs = PromptInputs(
        topic=body.topic,
        grade=body.grade,
        branch=body.branch,
        language=body.language,
        style=body.style,
        duration=body.duration,
        aspect_ratio=body.aspect_ratio,
        difficulty=body.difficulty,
        colors=body.colors,
        include_recap=body.include_recap,
        include_practice=body.include_practice,
        include_voiceover=body.include_voiceover,
        additional=body.additional,
    )
    return generate_prompt(inputs, settings)
