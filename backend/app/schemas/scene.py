"""Pydantic v2 models for the Scene format v1.0 document.

These models are the *typed* representation of ``scene.md`` used by the
compiler and the API. Structural enforcement (string lengths, numeric
ranges, closed enums, ``additionalProperties: false``) is performed by the
JSON Schemas in ``schema/`` — the same files the reference validator uses —
so application parser and reference validator cannot drift apart by
construction (:mod:`app.validation.pipeline` runs both). The Pydantic layer
then guarantees the typed shape every downstream consumer relies on.

Canonical human-readable specification: ``prompts/SCENE_FORMAT_SPEC.md``.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SCENE_FORMAT_VERSION = "1.0"
SUPPORTED_SCHEMA_VERSIONS = ("1.0",)

SceneType = Literal["intro", "explanation", "worked_example", "proof", "recap", "practice"]
AspectRatio = Literal["16:9", "9:16", "1:1"]
Theme = Literal["midnight", "ivory"]
ColorName = Literal[
    "navy", "violet", "ivory", "white", "black", "gray",
    "red", "green", "blue", "amber", "teal", "pink",
]

OBJECT_KINDS = (
    "text", "formula", "equation", "point", "segment", "line", "ray",
    "angle", "triangle", "circle", "polygon", "square", "rectangle",
    "vector", "axes", "function_graph", "area_fill", "number_line", "fraction",
)

ACTIONS = (
    "create", "write", "fade_in", "fade_out", "transform", "move",
    "rotate", "scale", "indicate", "circumscribe", "draw_border",
    "recolor", "wait", "arrange", "reveal",
)

# Actions whose ``target`` must be a single object id.
SINGLE_TARGET_ACTIONS = frozenset(
    {"write", "transform", "move", "rotate", "scale", "indicate",
     "circumscribe", "draw_border", "recolor"}
)

# Actions that may take a list target.
MULTI_TARGET_ACTIONS = frozenset({"create", "fade_in", "fade_out", "arrange", "reveal"})

TEXT_KINDS = frozenset({"text", "formula", "equation"})
GRAPH_KINDS = frozenset({"function_graph", "area_fill"})

PALETTE = frozenset(
    {"navy", "violet", "ivory", "white", "black", "gray",
     "red", "green", "blue", "amber", "teal", "pink"}
)

# Visible frame per aspect ratio: (xmin, xmax, ymin, ymax).
FRAMES: dict[str, tuple[float, float, float, float]] = {
    "16:9": (-7.0, 7.0, -4.0, 4.0),
    "9:16": (-4.0, 4.0, -7.0, 7.0),
    "1:1": (-4.5, 4.5, -4.5, 4.5),
}

# Frame size (units) and pixel resolution per (aspect ratio, quality tier).
# Ratios match FRAMES exactly so pixels-per-unit is uniform on both axes.
RESOLUTIONS: dict[tuple[str, str], tuple[int, int]] = {
    ("16:9", "preview"): (840, 480),
    ("16:9", "standard"): (1260, 720),
    ("16:9", "high"): (1680, 960),
    ("9:16", "preview"): (480, 840),
    ("9:16", "standard"): (720, 1260),
    ("9:16", "high"): (1080, 1890),
    ("1:1", "preview"): (480, 480),
    ("1:1", "standard"): (720, 720),
    ("1:1", "high"): (1080, 1080),
}

QUALITY_FRAME_RATES: dict[str, int] = {"preview": 15, "standard": 30, "high": 60}
QUALITIES = ("preview", "standard", "high")

Frame = Literal["16:9", "9:16", "1:1"]


def _drop_none(obj: Any) -> Any:
    """Recursively remove keys whose value is ``None``.

    Pydantic's ``model_dump()`` materializes *absent* optional fields as
    ``None``. The reference validator and the render runtime read documents
    with a ``.get(key, default)`` idiom, which only falls back on absence —
    a materialized ``null`` would defeat every default (and ``float(None)``
    would raise). Dropping ``None`` restores the shape of the YAML the
    teacher actually wrote: absent stays absent. Lists keep their length
    (positional meaning), recursing into items only.
    """
    if isinstance(obj, dict):
        return {k: _drop_none(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_drop_none(v) for v in obj]
    return obj


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
# Front matter
# ---------------------------------------------------------------------------

class VerificationAssertion(StrictModel):
    id: Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]{0,39}$")]
    kind: Literal["numeric", "symbolic"]
    description: Annotated[str, Field(min_length=1, max_length=200)]
    expression: Annotated[str, Field(min_length=1, max_length=200)]
    expected: float
    tolerance: Annotated[float, Field(gt=0)] = 1e-9
    subs: dict[str, float] | None = None


class LessonInfo(StrictModel):
    title: Annotated[str, Field(min_length=1, max_length=140)]
    topic: Annotated[str, Field(min_length=1, max_length=140)]
    grade: Annotated[str, Field(min_length=1, max_length=24)]
    language: Annotated[
        str,
        Field(
            min_length=2,
            max_length=40,
            pattern=r"^(?:[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})?|[^0-9\s][^0-9]{1,39})$",
        ),
    ]
    duration_minutes: Annotated[float, Field(ge=1, le=60)] = 5
    aspect_ratio: AspectRatio = "16:9"
    theme: Theme = "midnight"


class FrontMatter(StrictModel):
    schema_version: Literal["1.0"]
    lesson: LessonInfo
    objectives: list[Annotated[str, Field(min_length=1, max_length=200)]] = Field(
        default_factory=list, max_length=10
    )
    prerequisites: list[Annotated[str, Field(min_length=1, max_length=200)]] = Field(
        default_factory=list, max_length=10
    )
    recap: Annotated[str, Field(min_length=1, max_length=1000)] | None = None
    practice_questions: list[Annotated[str, Field(min_length=1, max_length=300)]] = Field(
        default_factory=list, max_length=12
    )
    verification: list[VerificationAssertion] = Field(default_factory=list, max_length=10)

    @field_validator("verification")
    @classmethod
    def _unique_assertion_ids(cls, value: list[VerificationAssertion]) -> list[VerificationAssertion]:
        ids = [v.id for v in value]
        if len(ids) != len(set(ids)):
            raise ValueError("verification ids must be unique")
        return value


# ---------------------------------------------------------------------------
# Object parameters (19 kinds)
# ---------------------------------------------------------------------------

Position = tuple[float, float]
ValuePair = tuple[float, float]

Color = Annotated[str, Field(pattern=r"^(navy|violet|ivory|white|black|gray|red|green|blue|amber|teal|pink|#[0-9a-fA-F]{6})$")]
Label = Annotated[str, Field(min_length=0, max_length=40)]
StrokeWidth = Annotated[float, Field(ge=1, le=12)]
FillOpacity = Annotated[float, Field(ge=0, le=1)]
ExpressionStr = Annotated[str, Field(min_length=1, max_length=120)]


class TextParams(StrictModel):
    content: Annotated[str, Field(min_length=1, max_length=200)]
    font_size: Annotated[int, Field(ge=16, le=120)] = 36
    color: Color | None = None
    position: Position = (0.0, 0.0)


class FormulaParams(TextParams):
    renderer: Literal["auto", "text", "latex"] = "auto"
    font_size: Annotated[int, Field(ge=16, le=96)] = 44


class EquationParams(TextParams):
    content: Annotated[str, Field(min_length=3, max_length=200, pattern="=")]
    font_size: Annotated[int, Field(ge=16, le=96)] = 40


class PointParams(StrictModel):
    position: Position
    radius: Annotated[float, Field(ge=0.05, le=0.5)] = 0.12
    color: Color | None = None
    label: Label | None = None
    label_direction: Literal["up", "down", "left", "right"] = "up"


class SegmentParams(StrictModel):
    start: Position
    end: Position
    color: Color | None = None
    stroke_width: StrokeWidth = 4
    label: Label | None = None


class LineParams(SegmentParams):
    stroke_width: StrokeWidth = 3


class RayParams(SegmentParams):
    stroke_width: StrokeWidth = 3


class AngleParams(StrictModel):
    vertex: Position
    start_angle: Annotated[float, Field(ge=-360, le=360)]
    end_angle: Annotated[float, Field(ge=-360, le=360)]
    radius: Annotated[float, Field(ge=0.2, le=2)] = 0.8
    color: Color | None = None
    label: Label | None = None


class TriangleParams(StrictModel):
    vertices: tuple[Position, Position, Position]
    labels: list[Annotated[str, Field(min_length=0, max_length=40)]] = Field(
        default_factory=list, max_length=3
    )
    color: Color | None = None
    fill_opacity: FillOpacity = 0
    stroke_width: StrokeWidth = 4


class CircleParams(StrictModel):
    center: Position
    radius: Annotated[float, Field(ge=0.1, le=10)]
    color: Color | None = None
    fill_opacity: FillOpacity = 0
    stroke_width: StrokeWidth = 4


class PolygonParams(StrictModel):
    vertices: list[Position] = Field(min_length=3, max_length=12)
    labels: list[Annotated[str, Field(min_length=0, max_length=40)]] = Field(
        default_factory=list, max_length=12
    )
    color: Color | None = None
    fill_opacity: FillOpacity = 0
    stroke_width: StrokeWidth = 4


class SquareParams(StrictModel):
    origin: Position
    side: Annotated[float, Field(ge=0.1, le=10)]
    angle: Annotated[float, Field(ge=-360, le=360)] = 0
    color: Color | None = None
    fill_opacity: FillOpacity = 0
    stroke_width: StrokeWidth = 4


class RectangleParams(StrictModel):
    origin: Position
    width: Annotated[float, Field(ge=0.1, le=12)]
    height: Annotated[float, Field(ge=0.1, le=12)]
    angle: Annotated[float, Field(ge=-360, le=360)] = 0
    color: Color | None = None
    fill_opacity: FillOpacity = 0
    stroke_width: StrokeWidth = 4


class VectorParams(SegmentParams):
    color: Color | None = "violet"
    stroke_width: StrokeWidth = 4


class AxesParams(StrictModel):
    x_range: ValuePair = (-7.0, 7.0)
    y_range: ValuePair = (-4.0, 4.0)
    grid: bool = False
    include_numbers: bool = True
    x_label: Label | None = None
    y_label: Label | None = None


class FunctionGraphParams(StrictModel):
    expression: ExpressionStr
    domain: ValuePair | None = None
    color: Color | None = None
    stroke_width: StrokeWidth = 4
    samples: Annotated[int, Field(ge=20, le=2000)] = 400


class AreaFillParams(StrictModel):
    expression: ExpressionStr
    domain: ValuePair
    color: Color | None = None
    fill_opacity: Annotated[float, Field(ge=0, le=1)] = 0.35


class NumberLineMarker(StrictModel):
    value: float
    label: Label | None = None
    color: Color | None = None


class NumberLineParams(StrictModel):
    range: ValuePair
    step: Annotated[float, Field(ge=0.05, le=100)] = 1
    markers: list[NumberLineMarker] = Field(default_factory=list, max_length=12)
    color: Color | None = None
    label: Label | None = None


class FractionParams(StrictModel):
    numerator: Annotated[str, Field(min_length=1, max_length=12)]
    denominator: Annotated[str, Field(min_length=1, max_length=12)]
    font_size: Annotated[int, Field(ge=16, le=120)] = 48
    color: Color | None = None
    position: Position = (0.0, 0.0)
    label: Label | None = None


OBJECT_PARAM_MODELS: dict[str, type[StrictModel]] = {
    "text": TextParams,
    "formula": FormulaParams,
    "equation": EquationParams,
    "point": PointParams,
    "segment": SegmentParams,
    "line": LineParams,
    "ray": RayParams,
    "angle": AngleParams,
    "triangle": TriangleParams,
    "circle": CircleParams,
    "polygon": PolygonParams,
    "square": SquareParams,
    "rectangle": RectangleParams,
    "vector": VectorParams,
    "axes": AxesParams,
    "function_graph": FunctionGraphParams,
    "area_fill": AreaFillParams,
    "number_line": NumberLineParams,
    "fraction": FractionParams,
}

ParamsUnion = (
    TextParams | FormulaParams | EquationParams | PointParams | SegmentParams
    | LineParams | RayParams | AngleParams | TriangleParams | CircleParams
    | PolygonParams | SquareParams | RectangleParams | VectorParams | AxesParams
    | FunctionGraphParams | AreaFillParams | NumberLineParams | FractionParams
)


class SceneObject(StrictModel):
    id: Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]{0,39}$")]
    kind: Literal[
        "text", "formula", "equation", "point", "segment", "line", "ray",
        "angle", "triangle", "circle", "polygon", "square", "rectangle",
        "vector", "axes", "function_graph", "area_fill", "number_line", "fraction",
    ]
    params: ParamsUnion | None = None

    @model_validator(mode="before")
    @classmethod
    def _dispatch_params_by_kind(cls, data: Any) -> Any:
        """Validate ``params`` against the model for this object's ``kind``.

        The reference JSON Schema maps ``kind`` to its params shape via an
        ``if``/``then`` block (``schema/scene-v1.schema.json`` ``object``
        def). Validating the raw params dict here — before the union field is
        attempted — mirrors that contract exactly and yields a single precise
        error instead of one failure per union branch.
        """
        if not isinstance(data, dict):
            return data
        kind = data.get("kind")
        raw = data.get("params")
        model = OBJECT_PARAM_MODELS.get(kind) if isinstance(kind, str) else None
        if model is None or not isinstance(raw, dict):
            return data
        data = dict(data)
        data["params"] = model.model_validate(raw)
        return data

    def typed_params(self) -> StrictModel:
        """Return params coerced to this object kind's model."""
        if self.params is None:
            return OBJECT_PARAM_MODELS[self.kind]()
        model = OBJECT_PARAM_MODELS[self.kind]
        if isinstance(self.params, model):
            return self.params
        return model.model_validate(self.params.model_dump())


# ---------------------------------------------------------------------------
# Actions (15)
# ---------------------------------------------------------------------------

class _ActionBase(StrictModel):
    at: Annotated[float, Field(ge=0, le=600)] | None = None
    duration: Annotated[float, Field(ge=0.1, le=60)] | None = None


class CreateAction(_ActionBase):
    action: Literal["create"]
    target: str | list[str]


class WriteAction(_ActionBase):
    action: Literal["write"]
    target: str


class FadeInAction(_ActionBase):
    action: Literal["fade_in"]
    target: str | list[str]


class FadeOutAction(_ActionBase):
    action: Literal["fade_out"]
    target: str | list[str]


class TransformAction(_ActionBase):
    action: Literal["transform"]
    target: str
    into: Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]{0,39}$")]


class MoveAction(_ActionBase):
    action: Literal["move"]
    target: str
    to: Position


class RotateAction(_ActionBase):
    action: Literal["rotate"]
    target: str
    degrees: Annotated[float, Field(ge=-360, le=360)]


class ScaleAction(_ActionBase):
    action: Literal["scale"]
    target: str
    factor: Annotated[float, Field(ge=0.05, le=20)]


class IndicateAction(_ActionBase):
    action: Literal["indicate"]
    target: str
    style: Literal["pulse", "highlight", "underline"] = "pulse"


class CircumscribeAction(_ActionBase):
    action: Literal["circumscribe"]
    target: str
    color: Color | None = None


class DrawBorderAction(_ActionBase):
    action: Literal["draw_border"]
    target: str
    color: Color | None = None


class RecolorAction(_ActionBase):
    action: Literal["recolor"]
    target: str
    color: Color


class WaitAction(_ActionBase):
    action: Literal["wait"]
    duration: Annotated[float, Field(ge=0.1, le=60)] = 1.0


class ArrangeAction(_ActionBase):
    action: Literal["arrange"]
    target: Annotated[list[str], Field(min_length=2, max_length=24)]
    layout: Literal["row", "column", "grid"]
    gap: Annotated[float, Field(ge=0.1, le=5)] = 0.5
    to: Position | None = None


class RevealAction(_ActionBase):
    action: Literal["reveal"]
    target: Annotated[list[str], Field(min_length=1, max_length=24)]
    interval: Annotated[float, Field(ge=0.1, le=10)] = 0.75


ActionUnion = (
    CreateAction | WriteAction | FadeInAction | FadeOutAction | TransformAction
    | MoveAction | RotateAction | ScaleAction | IndicateAction
    | CircumscribeAction | DrawBorderAction | RecolorAction | WaitAction
    | ArrangeAction | RevealAction
)


# ---------------------------------------------------------------------------
# Scene block & document
# ---------------------------------------------------------------------------

class SceneBlock(StrictModel):
    id: Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]{0,39}$")]
    title: Annotated[str, Field(min_length=1, max_length=140)]
    type: SceneType
    duration: Annotated[float, Field(ge=0.5, le=300)] | None = None
    narration: Annotated[str, Field(min_length=1, max_length=2000)] | None = None
    objects: list[SceneObject] = Field(default_factory=list, max_length=40)
    actions: list[ActionUnion] = Field(default_factory=list, max_length=120)


class SceneDocument(StrictModel):
    """A fully parsed and structurally validated scene.md document."""

    front_matter: FrontMatter
    scenes: list[SceneBlock]
    prose: str = ""

    @property
    def lesson(self) -> LessonInfo:
        return self.front_matter.lesson

    def scene_by_id(self, scene_id: str) -> SceneBlock | None:
        for scene in self.scenes:
            if scene.id == scene_id:
                return scene
        return None

    def frame(self) -> tuple[float, float, float, float]:
        return FRAMES[self.lesson.aspect_ratio]

    def to_payload(self) -> dict[str, Any]:
        """JSON-safe payload embedded in generated Manim code.

        Optional fields that were *absent* in the source are dropped rather
        than emitted as ``null``: the reference validator and the render
        runtime both read these documents with a ``.get(key, default)`` idiom
        that only falls back on absence. Emitting a materialized ``null`` (an
        artifact of Pydantic's defaults, never present in valid YAML) would
        make ``float(act.get("duration", ...))`` see ``None`` and fail. Keeping
        the payload shaped like the source the teacher wrote preserves that
        contract exactly.
        """
        return {
            "front_matter": _drop_none(self.front_matter.model_dump(mode="json")),
            "scenes": [_drop_none(s.model_dump(mode="json")) for s in self.scenes],
        }
