"""Trusted scene runtime — executes validated payload data as Manim animations.

This module is imported **only** by generated scene files inside the render
subprocess (or by Manim-aware tests). It receives the JSON payload embedded
in the generated file by :mod:`app.rendering.compiler` — data, never code —
and drives a Manim ``Scene`` through it:

* two-pass object construction (:func:`app.rendering.registry.build_scene_objects`);
* ``reveal`` expansion into staggered creates;
* absolute ``at`` sequencing with the same defaults the reference validator
  uses for duration estimation (``write`` -> 2 s, everything else -> 1 s);
* overlap batching: actions that start together play in one ``play(...)``;
* per-scene ``clear()`` so scenes never leak into each other.

No scene text is ever executed: expressions were validated against the
restricted grammar before compilation and are evaluated by walking a
validated AST (:mod:`app.validation.expressions`).
"""

from __future__ import annotations

from typing import Any

from manim import Scene

from app.rendering.layouts import Theme, resolve_theme
from app.rendering.registry import build_scene_objects, plan_action
from app.schemas.scene import FRAMES

# Beat of empty screen between scenes after the clear (seconds).
SCENE_GAP_S = 0.5

# Actions whose effective start times differ by less than this play together.
BATCH_EPSILON_S = 1e-6

DEFAULT_ACTION_DURATION = 1.0
WRITE_DURATION = 2.0
REVEAL_INTERVAL_S = 0.75


def default_duration(actions: list[dict], declared: float | None) -> float:
    """How long a scene plays: at least the action timeline, honoring a longer declared duration.

    ``estimate`` matches ``tools/validate_scene.py`` (latest action end + 1.5 s).
    A declared ``duration`` shorter than the estimate never truncates playback
    (the validation pipeline already reports that as ``timing_tight``); a
    longer one adds the pause the teacher asked for.
    """
    cursor = 0.0
    for act in actions:
        start = act.get("at", cursor)
        dur = act.get(
            "duration", WRITE_DURATION if act.get("action") == "write" else DEFAULT_ACTION_DURATION
        )
        try:
            cursor = max(cursor, float(start) + float(dur))
        except (TypeError, ValueError):
            continue
    estimate = round(cursor + 1.5, 2)
    if declared is None:
        return estimate
    return max(float(declared), estimate)


def _duration_of(act: dict) -> float:
    return float(
        act.get("duration", WRITE_DURATION if act.get("action") == "write" else DEFAULT_ACTION_DURATION)
    )


def _expand_reveal(act: dict, clock: float) -> list[dict]:
    """Turn a reveal action into staggered per-target creates."""
    interval = float(act.get("interval", REVEAL_INTERVAL_S) or REVEAL_INTERVAL_S)
    base = float(act.get("at", clock))
    raw = act.get("target")
    targets = [raw] if isinstance(raw, str) else list(raw or [])
    return [
        {
            "action": "create",
            "target": target,
            "at": round(base + k * interval, 6),
            "duration": interval,
        }
        for k, target in enumerate(targets)
    ]


def _execute(scene: Scene, plan, notes: list[str]) -> None:  # noqa: ANN001
    """Apply one ActionPlan to the scene (honest skips are logged, never silent)."""
    if plan.note:
        notes.append(plan.note)
    if plan.kind == "skip":
        return
    if plan.kind == "add":
        scene.add(*plan.add_mobjects)
        return
    if plan.kind == "wait":
        if plan.wait_s > 0:
            scene.wait(plan.wait_s)
        return
    # kind == "play"
    if plan.animations:
        scene.play(*plan.animations, run_time=max(plan.run_time, 0.01))


def build_scene(scene: Scene, payload: dict[str, Any]) -> None:
    """Play a whole compiled lesson payload on ``scene``."""
    lesson = payload.get("front_matter", {}).get("lesson", {})
    theme: Theme = resolve_theme(lesson.get("theme"))
    aspect_ratio = lesson.get("aspect_ratio", "16:9")
    frame = FRAMES.get(aspect_ratio, FRAMES["16:9"])
    scene.camera.background_color = theme.background

    blocks = payload.get("scenes", [])
    total = len(blocks)
    notes: list[str] = []

    for index, block in enumerate(blocks):
        if index > 0:
            scene.clear()
            if SCENE_GAP_S > 0:
                scene.wait(SCENE_GAP_S)
        try:
            _build_block(scene, block, theme, frame, notes)
        except Exception as exc:  # noqa: BLE001 - re-raised after an honest marker
            print(f"RUNTIME_ERROR: {exc}", flush=True)
            raise RuntimeError(
                f"scene '{block.get('id', index + 1)}' could not be rendered: {exc}"
            ) from exc
        print(f"[scene {index + 1}/{total}] {block.get('title', '')} done", flush=True)

    for note in notes:
        print(f"NOTE: {note}", flush=True)


def _build_block(
    scene: Scene,
    block: dict[str, Any],
    theme: Theme,
    frame: tuple[float, float, float, float],
    notes: list[str],
) -> None:
    objects = {
        o["id"]: o
        for o in (block.get("objects") or [])
        if isinstance(o, dict) and isinstance(o.get("id"), str)
    }
    mobjects = build_scene_objects(objects, theme, frame)
    on_screen: dict = {}

    actions = [a for a in (block.get("actions") or []) if isinstance(a, dict)]
    declared = block.get("duration")
    target_end = default_duration(
        actions, float(declared) if isinstance(declared, (int, float)) else None
    )

    clock = 0.0
    i = 0
    while i < len(actions):
        act = actions[i]
        if act.get("action") == "reveal":
            actions[i : i + 1] = _expand_reveal(act, clock)
            act = actions[i]

        try:
            start = float(act.get("at", clock))
        except (TypeError, ValueError):
            start = clock
        if start > clock + BATCH_EPSILON_S:
            scene.wait(start - clock)
            clock = start

        # Gather every following action that starts at (or before) this
        # instant so they play together in a single call.
        batch = [act]
        batch_end = clock + _duration_of(act)
        j = i + 1
        while j < len(actions):
            nxt = actions[j]
            if nxt.get("action") == "reveal":
                actions[j : j + 1] = _expand_reveal(nxt, clock)
                nxt = actions[j]
            try:
                nxt_start = float(nxt.get("at", batch_end))
            except (TypeError, ValueError):
                nxt_start = batch_end
            if nxt_start <= clock + BATCH_EPSILON_S:
                batch.append(nxt)
                batch_end = max(batch_end, clock + _duration_of(nxt))
                j += 1
            else:
                break

        for batched in batch:
            plan = plan_action(batched, mobjects, on_screen, theme, _duration_of(batched))
            _execute(scene, plan, notes)

        clock = batch_end
        i = j

    tail = target_end - clock
    if tail > BATCH_EPSILON_S:
        scene.wait(tail)
