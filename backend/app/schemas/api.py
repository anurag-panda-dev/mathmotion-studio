"""Typed request/response models for the ``/api/v1`` HTTP surface."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.scene import AspectRatio

Quality = Literal["preview", "standard", "high"]


class StrictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class ErrorBody(BaseModel):
    code: str
    message: str
    request_id: str = "-"
    detail: Any | None = None


class ErrorEnvelope(BaseModel):
    error: ErrorBody


# ---------------------------------------------------------------------------
# Health & diagnostics
# ---------------------------------------------------------------------------

class DependencyStatus(BaseModel):
    name: str
    available: bool
    version: str | None = None
    detail: str | None = None
    required_for: str


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    version: str
    scene_format_version: str
    python: str
    dependencies: list[DependencyStatus]
    frontend_built: bool
    directories: dict[str, str]


class DiagnosticsResponse(BaseModel):
    health: HealthResponse
    storage: dict[str, int]
    render_concurrency: int
    rate_limit: dict[str, int]
    job_counts: dict[str, int]


# ---------------------------------------------------------------------------
# Prompt generator
# ---------------------------------------------------------------------------

ExplanationStyle = Literal[
    "intuitive", "step-by-step", "visual proof", "worked example", "revision"
]


class PromptRequest(StrictRequest):
    topic: str = Field(min_length=3, max_length=200)
    grade: str = Field(min_length=1, max_length=24)
    branch: str | None = Field(default=None, max_length=60)
    language: str = Field(default="en", min_length=2, max_length=40)
    style: ExplanationStyle = "intuitive"
    duration: int = Field(default=5, ge=1, le=60)
    aspect_ratio: AspectRatio = "16:9"
    difficulty: Literal["basic", "standard", "advanced"] = "standard"
    colors: str | None = Field(default=None, max_length=200)
    include_recap: bool = True
    include_practice: bool = True
    include_voiceover: bool = True
    additional: str | None = Field(default=None, max_length=1000)


class PromptResponse(BaseModel):
    prompt: str
    compact_prompt: str
    filename: str
    char_count: int
    compact_char_count: int
    compact_reduced_percent: float


# ---------------------------------------------------------------------------
# Render jobs (declared before lessons: LessonDetail embeds job status)
# ---------------------------------------------------------------------------

JobState = Literal[
    "queued", "validating", "preparing", "rendering", "postprocessing",
    "completed", "failed", "cancelling", "cancelled",
]

ACTIVE_STATES = (
    "queued", "validating", "preparing", "rendering", "postprocessing", "cancelling",
)


class RenderSettingsModel(BaseModel):
    quality: Quality = "standard"
    aspect_ratio: AspectRatio = "16:9"
    frame_rate: int = 30


class CreateJobRequest(StrictRequest):
    quality: Quality | None = None
    aspect_ratio: AspectRatio | None = None


class JobStatusModel(BaseModel):
    job_id: str
    lesson_id: str
    lesson_title: str | None = None
    status: JobState
    progress: float | None = None
    determinate: bool = False
    phase: str
    settings: RenderSettingsModel
    output_path: str | None = None
    output_url: str | None = None
    error_summary: str | None = None
    technical_detail: str | None = None
    attempt: int = 1
    created_at: str
    started_at: str | None = None
    finished_at: str | None = None


class JobListResponse(BaseModel):
    jobs: list[JobStatusModel]


class LogsResponse(BaseModel):
    job_id: str
    logs: str
    truncated: bool = False


class CancelResponse(BaseModel):
    job_id: str
    status: JobState


# ---------------------------------------------------------------------------
# Scene validation & import
# ---------------------------------------------------------------------------

class ValidationIssueModel(BaseModel):
    severity: Literal["error", "warning"]
    category: str
    message: str
    scene: str | None = None
    path: str | None = None
    line: int | None = None
    suggestion: str | None = None


class VerificationResultModel(BaseModel):
    id: str
    kind: Literal["numeric", "symbolic"]
    description: str
    status: Literal["passed", "failed", "unavailable"]
    message: str
    expected: float
    actual: float | None = None


class SceneTimelineEntry(BaseModel):
    id: str
    title: str
    type: str
    duration_s: float
    narration: str | None = None
    object_count: int = 0
    action_count: int = 0
    formulas: list[str] = Field(default_factory=list)


class SceneSummary(BaseModel):
    title: str
    topic: str
    grade: str
    language: str
    duration_minutes: float
    aspect_ratio: AspectRatio
    theme: str
    objectives: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    recap: str | None = None
    practice_questions: list[str] = Field(default_factory=list)
    scenes: list[SceneTimelineEntry] = Field(default_factory=list)
    total_duration_s: float = 0
    object_count: int = 0
    action_count: int = 0


class ValidationReportResponse(BaseModel):
    valid: bool
    schema_version: str | None = None
    errors: list[ValidationIssueModel] = Field(default_factory=list)
    warnings: list[ValidationIssueModel] = Field(default_factory=list)
    verification: list[VerificationResultModel] = Field(default_factory=list)
    summary: SceneSummary | None = None


class ValidateRequest(StrictRequest):
    markdown: str = Field(min_length=1)
    filename: str | None = None
    verify: bool = True


class ImportResponse(BaseModel):
    lesson_id: str
    filename: str
    report: ValidationReportResponse


class SourceUpdateRequest(StrictRequest):
    markdown: str = Field(min_length=1)


# ---------------------------------------------------------------------------
# Lessons
# ---------------------------------------------------------------------------

class LessonListItem(BaseModel):
    lesson_id: str
    title: str
    topic: str
    grade: str
    language: str
    schema_version: str | None
    filename: str
    valid: bool | None
    error_count: int
    warning_count: int
    duration_minutes: float | None
    aspect_ratio: str | None
    created_at: str
    updated_at: str
    last_render_at: str | None
    job_count: int = 0


class LessonDetail(LessonListItem):
    markdown: str
    report: ValidationReportResponse | None = None
    summary: SceneSummary | None = None
    jobs: list[JobStatusModel] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

class AppSettingsModel(BaseModel):
    output_dir: str
    default_quality: Quality = "standard"
    default_aspect_ratio: AspectRatio = "16:9"
    theme: Literal["light", "dark", "system"] = "system"
    language: str = "en"


class AppSettingsPatch(StrictRequest):
    output_dir: str | None = Field(default=None, max_length=300)
    default_quality: Quality | None = None
    default_aspect_ratio: AspectRatio | None = None
    theme: Literal["light", "dark", "system"] | None = None
    language: str | None = Field(default=None, min_length=2, max_length=40)


# ---------------------------------------------------------------------------
# Examples & schema reference
# ---------------------------------------------------------------------------

class ExampleListItem(BaseModel):
    name: str
    title: str
    topic: str
    grade: str
    size_bytes: int


class ExampleListResponse(BaseModel):
    examples: list[ExampleListItem]


class ExampleContentResponse(BaseModel):
    name: str
    markdown: str


class SchemaReferenceResponse(BaseModel):
    scene_format_version: str
    specification: str
    object_kinds: list[str]
    actions: list[str]
    colors: list[str]
    frames: dict[str, list[float]]
    lesson_schema: dict[str, Any]
    scene_schema: dict[str, Any]
