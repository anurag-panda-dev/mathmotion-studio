"""The trusted Manim component registry.

Every object kind and action in the Scene format maps 1:1 to a function in
this module. This is the *only* place scene data meets Manim: the compiler
emits a JSON payload (data, never code), and this registry — trusted,
developer-maintained source — turns that data into mobjects and
animations. No text from a scene.md file is ever interpolated into
executable Python; no ``eval``, no ``exec``, no dynamic imports.

Extensibility: add an object builder to ``OBJECT_BUILDERS`` or an action
planner to ``ACTION_PLANNERS`` — nothing else in the application changes.

This module imports Manim and is therefore only loaded by the render
subprocess (or by tests that skip when Manim is absent).
"""

from __future__ import annotations

import math
import shutil
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from manim import (
    DL,
    DOWN,
    DR,
    LEFT,
    RIGHT,
    UP,
    Arc,
    Arrow,
    Axes,
    Circle,
    Circumscribe,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    Indicate,
    Line,
    MathTex,
    NumberPlane,
    Polygon,
    Rectangle,
    Square,
    SurroundingRectangle,
    Text,
    Transform,
    VGroup,
    VMobject,
    Write,
)

from app.rendering.layouts import PALETTE_HEX, Theme, nice_step, resolve_color, value_to_x
from app.schemas.scene import OBJECT_PARAM_MODELS

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_LATEX_MISSING_MSG = (
    "This lesson asks for LaTeX rendering (renderer: latex) but LaTeX is "
    "not available on this machine. Install LaTeX, or change the object's "
    "renderer to 'auto' or 'text'."
)


def _latex_available() -> bool:
    """True when Manim's full LaTeX toolchain is on PATH.

    Manim compiles ``.tex`` by spawning ``latex`` and then ``dvisvgm``;
    both are optional dependencies (``diagnostics.check_latex`` reports them
    the same way). When either is missing, LaTeX typography must degrade to
    plain text *before* constructing Manim objects - a failure inside e.g.
    ``NumberPlane`` surfaces as ``FileNotFoundError`` mid-scene with no
    chance to recover (job e2a6f528..., scene 's3').
    """
    return shutil.which("latex") is not None and shutil.which("dvisvgm") is not None


def vec(xy: Any) -> np.ndarray:
    return np.array([float(xy[0]), float(xy[1]), 0.0])


def _label_text(content: str, font_size: int, color: str) -> Text:
    return Text(content, font_size=font_size, color=color)


def _perpendicular_label(line: Line, content: str, color: str, font_size: int = 26) -> Text:
    start, end = line.get_start(), line.get_end()
    delta = end - start
    length = float(np.linalg.norm(delta))
    perp = np.array([-delta[1], delta[0], 0.0]) if length else np.array([0.0, 1.0, 0.0])
    label = _label_text(content, font_size, color)
    label.move_to(line.get_center() + 0.22 * (perp / max(length, 1e-9)))
    return label


# ---------------------------------------------------------------------------
# Object builders — one per Scene format object kind
# ---------------------------------------------------------------------------


def _build_text(params: dict, theme: Theme) -> VMobject:
    p = OBJECT_PARAM_MODELS["text"].model_validate(params or {})
    color = resolve_color(p.color, theme)
    return Text(p.content, font_size=p.font_size, color=color).move_to(vec(p.position))


def _build_formula(params: dict, theme: Theme) -> VMobject:
    p = OBJECT_PARAM_MODELS["formula"].model_validate(params or {})
    color = resolve_color(p.color, theme)
    return _styled_content(p.content, p.renderer, p.font_size, color).move_to(vec(p.position))


def _build_equation(params: dict, theme: Theme) -> VMobject:
    p = OBJECT_PARAM_MODELS["equation"].model_validate(params or {})
    color = resolve_color(p.color, theme)
    return _styled_content(p.content, "auto", p.font_size, color).move_to(vec(p.position))


def _styled_content(content: str, renderer: str, font_size: int, color: str) -> VMobject:
    """LaTeX typography when requested/possible, honest fallback otherwise."""
    if renderer in ("auto", "latex"):
        if not _latex_available():
            # renderer == "latex": documented hard failure (the teacher asked
            # for LaTeX explicitly). renderer == "auto": documented graceful
            # degradation to Text (INSTALLATION.md) - no subprocess attempt.
            if renderer == "latex":
                raise RuntimeError(_LATEX_MISSING_MSG)
        else:
            try:
                return MathTex(content, font_size=font_size, color=color)
            except Exception as exc:  # noqa: BLE001 - any LaTeX failure surfaces here
                if renderer == "latex":
                    raise RuntimeError(_LATEX_MISSING_MSG) from exc
                # renderer == auto: the toolchain looked present but failed;
                # documented graceful degradation (INSTALLATION.md).
    return Text(content, font_size=font_size, color=color)


def _build_point(params: dict, theme: Theme) -> VMobject:
    p = OBJECT_PARAM_MODELS["point"].model_validate(params or {})
    color = resolve_color(p.color, theme) or PALETTE_HEX["violet"]
    if not p.color:
        color = PALETTE_HEX["violet"]
    dot = Dot(point=vec(p.position), radius=p.radius, color=color)
    if p.label:
        directions = {"up": UP, "down": DOWN, "left": LEFT, "right": RIGHT}
        label = _label_text(p.label, 24, color).next_to(dot, directions[p.label_direction], buff=0.15)
        return VGroup(dot, label)
    return dot


def _build_segment(params: dict, theme: Theme, stroke: int = 4) -> VMobject:
    p = OBJECT_PARAM_MODELS["segment"].model_validate(params or {})
    color = resolve_color(p.color, theme)
    line = Line(vec(p.start), vec(p.end), color=color)
    line.set_stroke(width=p.stroke_width or stroke)
    if p.label:
        return VGroup(line, _perpendicular_label(line, p.label, color))
    return line


def _build_line(params: dict, theme: Theme) -> VMobject:
    p = OBJECT_PARAM_MODELS["line"].model_validate(params or {})
    color = resolve_color(p.color, theme)
    start, end = vec(p.start), vec(p.end)
    delta = end - start
    norm = float(np.linalg.norm(delta))
    if norm < 1e-9:  # pragma: no cover - degenerate input passes schema
        raise ValueError("a line needs two distinct points")
    unit = delta / norm
    far = 100.0  # extends past every frame; the camera clips
    line = Line(start - far * unit, end + far * unit, color=color)
    line.set_stroke(width=p.stroke_width)
    if p.label:
        return VGroup(line, _perpendicular_label(line, p.label, color))
    return line


def _build_ray(params: dict, theme: Theme) -> VMobject:
    p = OBJECT_PARAM_MODELS["ray"].model_validate(params or {})
    color = resolve_color(p.color, theme)
    start, end = vec(p.start), vec(p.end)
    delta = end - start
    norm = float(np.linalg.norm(delta))
    if norm < 1e-9:  # pragma: no cover - degenerate input passes schema
        raise ValueError("a ray needs two distinct points")
    unit = delta / norm
    ray = Line(start, end + 100.0 * unit, color=color)
    ray.set_stroke(width=p.stroke_width)
    if p.label:
        return VGroup(ray, _perpendicular_label(ray, p.label, color))
    return ray


def _build_angle(params: dict, theme: Theme) -> VMobject:
    p = OBJECT_PARAM_MODELS["angle"].model_validate(params or {})
    color = resolve_color(p.color, theme) or PALETTE_HEX["violet"]
    if not p.color:
        color = PALETTE_HEX["violet"]
    sweep = math.radians(p.end_angle - p.start_angle)
    arc = Arc(
        radius=p.radius,
        arc_center=vec(p.vertex),
        start_angle=math.radians(p.start_angle),
        angle=sweep,
        color=color,
    )
    arc.set_stroke(width=4)
    if p.label:
        mid = math.radians((p.start_angle + p.end_angle) / 2)
        pos = vec(p.vertex) + (p.radius + 0.25) * np.array(
            [math.cos(mid), math.sin(mid), 0.0]
        )
        label = _label_text(p.label, 24, color).move_to(pos)
        return VGroup(arc, label)
    return arc


def _vertex_labels(vertices: list, labels: list[str], color: str) -> list[Text]:
    if not labels:
        return []
    centroid = np.mean([vec(v) for v in vertices], axis=0)
    out: list[Text] = []
    for vertex, label in zip(vertices, labels, strict=False):
        if not label:  # empty string = no label at this vertex (spec §6.1)
            continue
        pos = vec(vertex)
        direction = pos - centroid
        norm = float(np.linalg.norm(direction))
        direction = direction / norm if norm > 1e-9 else np.array([0.0, 1.0, 0.0])
        text = _label_text(label, 26, color)
        text.move_to(pos + 0.3 * direction)
        out.append(text)
    return out


def _polygon(vertices: list, color: str, fill_opacity: float, stroke_width: float) -> Polygon:
    poly = Polygon(*[vec(v) for v in vertices])
    poly.set_fill(color, opacity=fill_opacity)
    poly.set_stroke(color=color, width=stroke_width)
    return poly


def _build_triangle(params: dict, theme: Theme) -> VMobject:
    p = OBJECT_PARAM_MODELS["triangle"].model_validate(params or {})
    color = resolve_color(p.color, theme)
    poly = _polygon(list(p.vertices), color, p.fill_opacity, p.stroke_width)
    labels = _vertex_labels(list(p.vertices), list(p.labels), color)
    return VGroup(poly, *labels) if labels else poly


def _build_circle(params: dict, theme: Theme) -> VMobject:
    p = OBJECT_PARAM_MODELS["circle"].model_validate(params or {})
    color = resolve_color(p.color, theme)
    circle = Circle(radius=p.radius)
    circle.set_fill(color, opacity=p.fill_opacity)
    circle.set_stroke(color=color, width=p.stroke_width)
    circle.move_to(vec(p.center))
    return circle


def _build_polygon(params: dict, theme: Theme) -> VMobject:
    p = OBJECT_PARAM_MODELS["polygon"].model_validate(params or {})
    color = resolve_color(p.color, theme)
    poly = _polygon(list(p.vertices), color, p.fill_opacity, p.stroke_width)
    labels = _vertex_labels(list(p.vertices), list(p.labels), color)
    return VGroup(poly, *labels) if labels else poly


def _build_square(params: dict, theme: Theme) -> VMobject:
    p = OBJECT_PARAM_MODELS["square"].model_validate(params or {})
    color = resolve_color(p.color, theme)
    shape = Square(side_length=p.side)
    shape.set_fill(color, opacity=p.fill_opacity)
    shape.set_stroke(color=color, width=p.stroke_width)
    shape.rotate(math.radians(p.angle)).move_to(vec(p.origin))
    return shape


def _build_rectangle(params: dict, theme: Theme) -> VMobject:
    p = OBJECT_PARAM_MODELS["rectangle"].model_validate(params or {})
    color = resolve_color(p.color, theme)
    shape = Rectangle(width=p.width, height=p.height)
    shape.set_fill(color, opacity=p.fill_opacity)
    shape.set_stroke(color=color, width=p.stroke_width)
    shape.rotate(math.radians(p.angle)).move_to(vec(p.origin))
    return shape


def _build_vector(params: dict, theme: Theme) -> VMobject:
    p = OBJECT_PARAM_MODELS["vector"].model_validate(params or {})
    color = resolve_color(p.color, theme) or PALETTE_HEX["violet"]
    if not p.color:
        color = PALETTE_HEX["violet"]
    arrow = Arrow(vec(p.start), vec(p.end), buff=0, color=color, stroke_width=p.stroke_width)
    if p.label:
        return VGroup(arrow, _perpendicular_label(arrow, p.label, color))
    return arrow


def _build_axes(params: dict, theme: Theme) -> VMobject:
    p = OBJECT_PARAM_MODELS["axes"].model_validate(params or {})
    x_min, x_max = float(p.x_range[0]), float(p.x_range[1])
    y_min, y_max = float(p.y_range[0]), float(p.y_range[1])
    x_step = nice_step(x_max - x_min)
    y_step = nice_step(y_max - y_min)
    x_range = [x_min, x_max, x_step]
    y_range = [y_min, y_max, y_step]
    axis_config = {
        "color": theme.ink,
        "include_numbers": p.include_numbers,
        "font_size": 24,
        "decimal_number_config": {"num_decimal_places": 0},
    }
    if not _latex_available():
        # Manim's default tick labels are MathTex, which spawns `latex`.
        # Without the toolchain that is a fatal FileNotFoundError inside
        # NumberPlane/Axes (nothing to catch there), so tick numbers become
        # plain Text - the documented optional-LaTeX fallback.
        # Text is an SVGMobject, so DecimalNumber's font_size assignment
        # rescales it exactly like the MathTex default.
        axis_config["label_constructor"] = Text
    if p.grid:
        plane = NumberPlane(
            x_range=x_range,
            y_range=y_range,
            axis_config=axis_config,
            background_line_style={
                "stroke_color": PALETTE_HEX["gray"],
                "stroke_width": 1,
                "stroke_opacity": 0.35,
            },
        )
        axes = plane
    else:
        axes = Axes(x_range=x_range, y_range=y_range, axis_config=axis_config)
    group = VGroup(axes)
    if p.x_label:
        group.add(_label_text(p.x_label, 26, theme.ink).next_to(axes.x_axis, DOWN, buff=0.35))
    if p.y_label:
        y_text = _label_text(p.y_label, 26, theme.ink)
        y_text.rotate(math.pi / 2).next_to(axes.y_axis, LEFT, buff=0.35)
        group.add(y_text)
    return group


def _sample_function(
    expression: str, domain: tuple[float, float], samples: int
) -> list[tuple[float, float]]:
    """Sample a validated expression on [a, b]; undefined points become NaN."""
    from app.validation.expressions import evaluate_numeric

    a, b = float(domain[0]), float(domain[1])
    if b < a:
        a, b = b, a
    xs = np.linspace(a, b, max(2, samples))
    out: list[tuple[float, float]] = []
    for x in xs:
        try:
            y = evaluate_numeric(expression, {"x": float(x)})
        except (ValueError, ZeroDivisionError, OverflowError):
            y = float("nan")
        out.append((float(x), y))
    return out


def _build_function_graph(params: dict, theme: Theme, axes: Axes) -> VMobject:
    p = OBJECT_PARAM_MODELS["function_graph"].model_validate(params or {})
    x_min, x_max = axes.x_axis.x_min, axes.x_axis.x_max
    domain = p.domain or (float(x_min), float(x_max))
    color = resolve_color(p.color, theme)
    if not p.color:
        color = PALETTE_HEX["violet"]
    samples = _sample_function(p.expression, (domain[0], domain[1]), p.samples)

    group = VGroup()
    run: list[tuple[float, float]] = []
    for x, y in samples:
        if math.isfinite(y):
            run.append((x, y))
            continue
        if len(run) >= 2:
            group.add(_polyline(axes, run, color, p.stroke_width))
        run = []
    if len(run) >= 2:
        group.add(_polyline(axes, run, color, p.stroke_width))
    return group


def _polyline(axes: Axes, points: list[tuple[float, float]], color: str, width: float) -> VMobject:
    line = VMobject()
    line.set_points_as_corners([axes.c2p(x, y) for x, y in points])
    line.set_stroke(color=color, width=width)
    return line


def _build_area_fill(params: dict, theme: Theme, axes: Axes) -> VMobject:
    p = OBJECT_PARAM_MODELS["area_fill"].model_validate(params or {})
    color = resolve_color(p.color, theme)
    if not p.color:
        color = PALETTE_HEX["violet"]
    samples = _sample_function(p.expression, (p.domain[0], p.domain[1]), 400)
    points = [axes.c2p(x, y) for x, y in samples if math.isfinite(y)]
    if len(points) < 2:
        raise ValueError("area_fill has no finite values over its domain")
    a_x, b_x = float(p.domain[0]), float(p.domain[1])
    boundary = [axes.c2p(a_x, 0.0), *points, axes.c2p(b_x, 0.0)]
    fill = Polygon(*boundary)
    fill.set_fill(color, opacity=p.fill_opacity)
    fill.set_stroke(width=0)
    return fill


def _build_number_line(params: dict, theme: Theme, frame: tuple[float, float, float, float]) -> VMobject:
    p = OBJECT_PARAM_MODELS["number_line"].model_validate(params or {})
    color = resolve_color(p.color, theme)
    vmin, vmax = float(p.range[0]), float(p.range[1])
    if vmax < vmin:
        vmin, vmax = vmax, vmin
    x0 = value_to_x(vmin, vmin, vmax, frame)
    x1 = value_to_x(vmax, vmin, vmax, frame)
    baseline = Line([x0, 0, 0], [x1, 0, 0], color=color)
    baseline.set_stroke(width=3)
    group = VGroup(baseline)

    first = math.ceil(vmin / p.step)
    last = math.floor(vmax / p.step)
    tick_values = [k * p.step for k in range(first, last + 1)][:80]
    for value in tick_values:
        x = value_to_x(value, vmin, vmax, frame)
        tick = Line([x, 0, 0], [x, -0.16, 0], color=color)
        tick.set_stroke(width=2)
        group.add(tick)
        number = _label_text(f"{value:g}", 20, color).next_to(tick, DOWN, buff=0.08)
        group.add(number)

    for marker in p.markers:
        x = value_to_x(float(marker.value), vmin, vmax, frame)
        marker_color = resolve_color(marker.color, theme) or PALETTE_HEX["violet"]
        if not marker.color:
            marker_color = PALETTE_HEX["violet"]
        dot = Dot([x, 0, 0], radius=0.09, color=marker_color)
        group.add(dot)
        caption = marker.label if marker.label else f"{marker.value:g}"
        group.add(_label_text(caption, 22, marker_color).next_to(dot, UP, buff=0.15))
    if p.label:
        group.add(_label_text(p.label, 24, color).next_to(baseline, DOWN, buff=0.55))
    return group


def _build_fraction(params: dict, theme: Theme) -> VMobject:
    p = OBJECT_PARAM_MODELS["fraction"].model_validate(params or {})
    color = resolve_color(p.color, theme)
    numerator = _label_text(p.numerator, p.font_size, color)
    denominator = _label_text(p.denominator, p.font_size, color)
    width = max(numerator.width, denominator.width, 0.5) + 0.2
    bar = Line([-width / 2, 0, 0], [width / 2, 0, 0], color=color)
    bar.set_stroke(width=3)
    numerator.next_to(bar, UP, buff=0.06)
    denominator.next_to(bar, DOWN, buff=0.06)
    group = VGroup(numerator, bar, denominator).move_to(vec(p.position))
    if p.label:
        group.add(_label_text(p.label, 26, color).next_to(group, RIGHT, buff=0.3))
    return group


ObjectBuilder = Callable[[dict, Theme], VMobject]

# Simple builders: (params, theme) -> mobject, no scene context needed.
# Graph kinds (function_graph, area_fill) and number_line need scene
# context (a built Axes mobject / the frame) and are dispatched by
# build_object directly.
OBJECT_BUILDERS: dict[str, ObjectBuilder] = {
    "text": _build_text,
    "formula": _build_formula,
    "equation": _build_equation,
    "point": _build_point,
    "segment": _build_segment,
    "line": _build_line,
    "ray": _build_ray,
    "angle": _build_angle,
    "triangle": _build_triangle,
    "circle": _build_circle,
    "polygon": _build_polygon,
    "square": _build_square,
    "rectangle": _build_rectangle,
    "vector": _build_vector,
    "axes": _build_axes,
    "fraction": _build_fraction,
}

# Kinds whose builders need the scene's built Axes mobject.
GRAPH_KINDS = ("function_graph", "area_fill")


def build_object(
    obj: dict,
    theme: Theme,
    frame: tuple[float, float, float, float],
    axes: Axes | None = None,
) -> VMobject:
    """Build one mobject from validated scene data.

    ``axes`` must be the Axes mobject built from the same scene's axes
    object when ``obj`` is a graph kind (the runtime builds axes first —
    see ``build_scene_objects``).
    """
    kind = obj.get("kind")
    params = obj.get("params") or {}
    if kind in GRAPH_KINDS:
        if axes is None:
            raise ValueError(f"{kind} requires an axes object in the same scene")
        if kind == "function_graph":
            return _build_function_graph(params, theme, axes)
        return _build_area_fill(params, theme, axes)
    if kind == "number_line":
        return _build_number_line(params, theme, frame)
    builder = OBJECT_BUILDERS.get(kind)
    if builder is None:
        raise ValueError(f"unsupported object kind {kind!r}")
    return builder(params, theme)


def build_scene_objects(
    scene_objects: dict[str, dict], theme: Theme, frame: tuple[float, float, float, float]
) -> dict[str, VMobject]:
    """Two-pass build: axes first so graph kinds can reference them.

    Scene validation guarantees a scene containing graph kinds also
    contains exactly one axes object (SCENE_FORMAT_SPEC.md), so the first
    axes built is the one handed to graph builders.
    """
    built: dict[str, VMobject] = {}
    axes_mobject: Axes | None = None
    for oid, obj in scene_objects.items():
        if obj.get("kind") == "axes":
            mobject = build_object(obj, theme, frame)
            built[oid] = mobject
            if axes_mobject is None:
                # unwrap the VGroup(_build_axes returns) to the Axes itself
                candidate = mobject.submobjects[0] if mobject.submobjects else mobject
                if isinstance(candidate, Axes):
                    axes_mobject = candidate
    for oid, obj in scene_objects.items():
        if oid in built:
            continue
        built[oid] = build_object(obj, theme, frame, axes=axes_mobject)
    return built


# ---------------------------------------------------------------------------
# Action planners — one per Scene format action
# ---------------------------------------------------------------------------


@dataclass
class ActionPlan:
    """What the runtime should do for one action."""

    kind: str  # "add" | "play" | "wait" | "skip"
    animations: list = field(default_factory=list)
    add_mobjects: list = field(default_factory=list)
    run_time: float = 0.0
    wait_s: float = 0.0
    note: str = ""


def _on_screen_targets(act, objects, on_screen) -> tuple[list[VMobject], list[str]]:
    raw = act.get("target")
    names = [raw] if isinstance(raw, str) else list(raw or [])
    found = [on_screen[n] for n in names if n in on_screen]
    missing = [n for n in names if n not in on_screen]
    return found, missing


def plan_create(act, objects, on_screen, theme, duration):  # noqa: ANN001, ANN202
    names = [act["target"]] if isinstance(act.get("target"), str) else list(act.get("target") or [])
    fresh = [objects[n] for n in names if n in objects and n not in on_screen]
    already = [n for n in names if n in on_screen]
    if not fresh:
        return ActionPlan("skip", note=f"create skipped; already on screen: {', '.join(already)}")
    for n in names:
        if n in objects:
            on_screen[n] = objects[n]
    if duration and duration > 0:
        return ActionPlan("play", animations=[FadeIn(m) for m in fresh], run_time=duration)
    return ActionPlan("add", add_mobjects=fresh)


def plan_write(act, objects, on_screen, theme, duration):  # noqa: ANN001, ANN202
    found, missing = _on_screen_targets(act, objects, on_screen)
    if missing or not found:
        name = (missing or [act.get("target")])[0]
        if name in objects:
            found = [objects[name]]
            on_screen[name] = objects[name]
        else:
            return ActionPlan("skip", note=f"write skipped; unknown object {name}")
    return ActionPlan("play", animations=[Write(m) for m in found], run_time=duration or 2.0)


def plan_fade_in(act, objects, on_screen, theme, duration):  # noqa: ANN001, ANN202
    names = [act["target"]] if isinstance(act.get("target"), str) else list(act.get("target") or [])
    mobjects = []
    for n in names:
        if n in on_screen:
            mobjects.append(on_screen[n])
        elif n in objects:
            on_screen[n] = objects[n]
            mobjects.append(objects[n])
    if not mobjects:
        return ActionPlan("skip", note="fade_in skipped; nothing to show")
    return ActionPlan("play", animations=[FadeIn(m) for m in mobjects], run_time=duration or 1.0)


def plan_fade_out(act, objects, on_screen, theme, duration):  # noqa: ANN001, ANN202
    found, missing = _on_screen_targets(act, objects, on_screen)
    if not found:
        return ActionPlan("skip", note=f"fade_out skipped; not on screen: {', '.join(missing)}")
    for n in ([act["target"]] if isinstance(act.get("target"), str) else act.get("target") or []):
        on_screen.pop(n, None)
    return ActionPlan("play", animations=[FadeOut(m) for m in found], run_time=duration or 1.0)


def plan_transform(act, objects, on_screen, theme, duration):  # noqa: ANN001, ANN202
    target_name, into_name = act.get("target"), act.get("into")
    if target_name not in on_screen:
        return ActionPlan("skip", note=f"transform skipped; {target_name} is not on screen")
    if into_name not in objects:
        return ActionPlan("skip", note=f"transform skipped; {into_name} is not declared")
    target, into = on_screen[target_name], objects[into_name]
    on_screen[target_name] = target
    on_screen[into_name] = target  # after the morph they are visually the same object
    return ActionPlan("play", animations=[Transform(target, into)], run_time=duration or 1.0)


def plan_move(act, objects, on_screen, theme, duration):  # noqa: ANN001, ANN202
    found, missing = _on_screen_targets(act, objects, on_screen)
    if not found:
        return ActionPlan("skip", note=f"move skipped; not on screen: {', '.join(missing)}")
    to = act.get("to") or [0, 0]
    return ActionPlan(
        "play",
        animations=[m.animate.move_to(vec(to)) for m in found],
        run_time=duration or 1.0,
    )


def plan_rotate(act, objects, on_screen, theme, duration):  # noqa: ANN001, ANN202
    found, missing = _on_screen_targets(act, objects, on_screen)
    if not found:
        return ActionPlan("skip", note=f"rotate skipped; not on screen: {', '.join(missing)}")
    return ActionPlan(
        "play",
        animations=[m.animate.rotate(math.radians(float(act.get("degrees", 0)))) for m in found],
        run_time=duration or 1.0,
    )


def plan_scale(act, objects, on_screen, theme, duration):  # noqa: ANN001, ANN202
    found, missing = _on_screen_targets(act, objects, on_screen)
    if not found:
        return ActionPlan("skip", note=f"scale skipped; not on screen: {', '.join(missing)}")
    factor = float(act.get("factor", 1.0))
    return ActionPlan(
        "play",
        animations=[m.animate.scale(factor) for m in found],
        run_time=duration or 1.0,
    )


def plan_indicate(act, objects, on_screen, theme, duration):  # noqa: ANN001, ANN202
    found, missing = _on_screen_targets(act, objects, on_screen)
    if not found:
        return ActionPlan("skip", note=f"indicate skipped; not on screen: {', '.join(missing)}")
    style = act.get("style", "pulse")
    animations = []
    for m in found:
        if style == "highlight":
            animations.append(Indicate(m, color=PALETTE_HEX["amber"], scale_factor=1.12))
        elif style == "underline":
            box = SurroundingRectangle(m, color=PALETTE_HEX["amber"], buff=0.12)
            underline = Line(box.get_corner(DL), box.get_corner(DR), color=PALETTE_HEX["amber"])
            underline.set_stroke(width=4)
            animations.append(Create(underline))
        else:
            animations.append(Indicate(m))
    return ActionPlan("play", animations=animations, run_time=duration or 1.0)


def plan_circumscribe(act, objects, on_screen, theme, duration):  # noqa: ANN001, ANN202
    found, missing = _on_screen_targets(act, objects, on_screen)
    if not found:
        return ActionPlan("skip", note=f"circumscribe skipped; not on screen: {', '.join(missing)}")
    color = resolve_color(act.get("color"), theme)
    return ActionPlan(
        "play",
        animations=[Circumscribe(m, color=color, run_time=duration or 1.0) for m in found],
        run_time=duration or 1.0,
    )


def plan_draw_border(act, objects, on_screen, theme, duration):  # noqa: ANN001, ANN202
    found, missing = _on_screen_targets(act, objects, on_screen)
    if not found:
        return ActionPlan("skip", note=f"draw_border skipped; not on screen: {', '.join(missing)}")
    color = resolve_color(act.get("color"), theme)
    return ActionPlan(
        "play",
        animations=[Create(SurroundingRectangle(m, color=color, buff=0.15)) for m in found],
        run_time=duration or 1.0,
    )


def plan_recolor(act, objects, on_screen, theme, duration):  # noqa: ANN001, ANN202
    found, missing = _on_screen_targets(act, objects, on_screen)
    if not found:
        return ActionPlan("skip", note=f"recolor skipped; not on screen: {', '.join(missing)}")
    color = resolve_color(act.get("color"), theme)
    return ActionPlan(
        "play",
        animations=[m.animate.set_color(color) for m in found],
        run_time=duration or 1.0,
    )


def plan_wait(act, objects, on_screen, theme, duration):  # noqa: ANN001, ANN202
    return ActionPlan("wait", wait_s=duration or 1.0)


def plan_arrange(act, objects, on_screen, theme, duration):  # noqa: ANN001, ANN202
    found, missing = _on_screen_targets(act, objects, on_screen)
    if len(found) < 2:
        return ActionPlan("skip", note=f"arrange skipped; not enough on-screen targets ({', '.join(missing)})")
    layout = act.get("layout", "row")
    direction = {"row": RIGHT, "column": DOWN, "grid": RIGHT}[layout]
    group = VGroup(*found)
    if layout == "grid":
        animate = group.animate.arrange_in_grid(buff=float(act.get("gap", 0.5)))
    else:
        animate = group.animate.arrange(direction, buff=float(act.get("gap", 0.5)))
    if act.get("to"):
        animate = animate.move_to(vec(act["to"]))
    return ActionPlan("play", animations=[animate], run_time=duration or 1.0)


ACTION_PLANNERS: dict[str, Callable[..., ActionPlan]] = {
    "create": plan_create,
    "write": plan_write,
    "fade_in": plan_fade_in,
    "fade_out": plan_fade_out,
    "transform": plan_transform,
    "move": plan_move,
    "rotate": plan_rotate,
    "scale": plan_scale,
    "indicate": plan_indicate,
    "circumscribe": plan_circumscribe,
    "draw_border": plan_draw_border,
    "recolor": plan_recolor,
    "wait": plan_wait,
    "arrange": plan_arrange,
    # reveal is expanded into per-target creates by the runtime before planning
}


def plan_action(act, objects, on_screen, theme, duration) -> ActionPlan:  # noqa: ANN001
    name = act.get("action")
    planner = ACTION_PLANNERS.get(name)
    if planner is None:
        return ActionPlan("skip", note=f"unknown action {name!r}")
    return planner(act, objects, on_screen, theme, duration)
