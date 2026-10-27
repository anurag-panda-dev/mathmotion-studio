"""The scene.md validation pipeline (stages 1-9 of the application flow).

Implements *exactly* the rules of the reference validator
(``tools/validate_scene.py``) — structural enforcement runs against the
same JSON Schema files with the same ``jsonschema`` machinery, so the two
cannot drift. The application adds on top:

* stage 5's typed view — Pydantic models built once structure passes;
* stage 9 — optional mathematical verification, reported separately;
* a scene-plan summary for the review page.

Errors block; warnings never do. Unsupported instructions are reported,
never silently dropped (``prompts/SCENE_VALIDATION_RULES.md``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from pydantic import ValidationError as PydanticValidationError

from app.core.config import SCENE_FORMAT_VERSION, Settings, get_settings
from app.parser.markdown import (
    SceneBlockSource,
    decode_bytes,
    find_line,
    parse_markdown,
)
from app.schemas.scene import FRAMES, GRAPH_KINDS, PALETTE, TEXT_KINDS, SceneDocument
from app.validation.expressions import check_expression
from app.validation.issues import ValidationReport
from app.validation.verify import run_verification

_schema_cache: dict[str, dict[str, Any]] = {}


def _load_schema(settings: Settings, name: str) -> dict[str, Any]:
    if name not in _schema_cache:
        path = settings.schema_dir / name
        import json

        with path.open(encoding="utf-8") as fh:
            _schema_cache[name] = json.load(fh)
    return _schema_cache[name]


def default_duration(scene: dict[str, Any]) -> float:
    """Estimated scene length: latest action end + 1.5 s tail (reference behavior)."""
    cursor = 0.0
    for act in scene.get("actions", []) or []:
        if not isinstance(act, dict):
            continue
        start = act.get("at", cursor)
        dur = act.get("duration", 2.0 if act.get("action") == "write" else 1.0)
        try:
            cursor = max(cursor, float(start) + float(dur))
        except (TypeError, ValueError):
            continue
    return round(cursor + 1.5, 2)


def validate_bytes(raw: bytes, *, filename: str, verify: bool = True) -> tuple[ValidationReport, SceneDocument | None]:
    """Stage 1-2: size and encoding, then hand off to :func:`validate_source`."""
    report = ValidationReport(filename=filename)
    size_issue = None
    from app.parser.markdown import check_size  # local import keeps module deps flat

    size_issue = check_size(len(raw))
    if size_issue is not None:
        report.errors.append(size_issue)
        return report, None
    text, enc_issue = decode_bytes(raw)
    if enc_issue is not None:
        report.errors.append(enc_issue)
        return report, None
    assert text is not None
    return validate_source(text, filename=filename, verify=verify, nbytes=len(raw))


def validate_source(
    text: str,
    *,
    filename: str = "scene.md",
    verify: bool = True,
    nbytes: int | None = None,
    settings: Settings | None = None,
) -> tuple[ValidationReport, SceneDocument | None]:
    """Run stages 2-9 on decoded text. Returns ``(report, document)``.

    ``document`` is ``None`` unless the file passed with zero errors.
    """
    settings = settings or get_settings()
    report = ValidationReport(filename=filename)

    if nbytes is None:
        nbytes = len(text.encode("utf-8"))
    if nbytes > 512 * 1024:
        report.error(
            "file_too_large",
            f"file is {nbytes} bytes; limit is {512 * 1024} bytes",
            suggestion="Split the lesson into smaller scenes or remove unused content.",
        )
        return report, None

    # --- stages 2-4: encoding (caller), front matter split, safe YAML ----
    parsed = parse_markdown(text)
    for issue in parsed.issues:
        (report.errors if issue.severity == "error" else report.warnings).append(issue)
    if parsed.front_matter is None:
        return report, None

    meta = parsed.front_matter

    # --- stage 5: schema version -----------------------------------------
    report.schema_version = str(meta.get("schema_version")) if meta.get("schema_version") is not None else None
    if meta.get("schema_version") not in (None, SCENE_FORMAT_VERSION):
        report.error(
            "schema_version",
            f"schema_version {meta.get('schema_version')!r} is not supported; "
            f"this application implements {SCENE_FORMAT_VERSION}",
            line=2,
            suggestion="Regenerate the scene with a current prompt template.",
        )
        return report, None

    # --- stage 6: lesson metadata schema ----------------------------------
    meta_schema = _load_schema(settings, "lesson-metadata-v1.schema.json")
    scene_schema = _load_schema(settings, "scene-v1.schema.json")

    for issue in sorted(Draft202012Validator(meta_schema).iter_errors(meta), key=lambda e: list(e.path)):
        report.error(
            "schema",
            issue.message,
            path="$." + ".".join(map(str, issue.path)) if issue.path else "$",
            suggestion="Compare with the field reference in SCENE_FORMAT_SPEC.md section 3.",
        )

    # --- stage 7: scene block schema --------------------------------------
    seen_scene_ids: set[str] = set()
    ratio = (meta.get("lesson") or {}).get("aspect_ratio", "16:9")
    xmin, xmax, ymin, ymax = FRAMES.get(ratio, FRAMES["16:9"])

    parsed_blocks = [b for b in parsed.blocks]
    if not parsed_blocks and not any(i.category == "yaml_syntax" for i in report.errors):
        report.error(
            "empty_scene",
            "file contains no ```scene blocks",
            suggestion="The lesson needs at least one scene block.",
        )

    doc_blocks: list[dict[str, Any]] = []

    for block in parsed_blocks:
        if block.doc is None:
            continue  # yaml_syntax error already recorded by the parser
        doc = block.doc
        sid = doc.get("id", "?")
        for issue in sorted(Draft202012Validator(scene_schema).iter_errors(doc), key=lambda e: list(e.path)):
            path_str = "$." + ".".join(map(str, issue.path)) if issue.path else "$"
            report.error(
                "schema",
                issue.message,
                scene=sid if isinstance(sid, str) else None,
                path=path_str,
                line=find_line(block.source, block.start_line, str(issue.path[0])) if issue.path else block.start_line + 1,
                suggestion="Compare with SCENE_FORMAT_SPEC.md sections 4-6.",
            )
        if not isinstance(sid, str):
            continue
        if sid in seen_scene_ids:
            report.error(
                "duplicate_id",
                f"scene id '{sid}' is used more than once",
                scene=sid,
                line=block.start_line + 1,
                suggestion="Give each scene a unique id.",
            )
        seen_scene_ids.add(sid)
        doc_blocks.append(doc)

        _check_semantics(report, block, doc, sid, (xmin, xmax, ymin, ymax), ratio)

    # --- stage 8: reference & expression checks on verification -----------
    if isinstance(meta, dict):
        for assertion in meta.get("verification", []) or []:
            if not isinstance(assertion, dict):
                continue
            subs = assertion.get("subs") if isinstance(assertion.get("subs"), dict) else {}
            msg = check_expression(str(assertion.get("expression", "")), set(subs or {}))
            if msg:
                report.error(
                    "unsafe_expression",
                    f"verification '{assertion.get('id')}': {msg}",
                    path=f"verification.{assertion.get('id')}",
                    suggestion="Use only the math grammar from SCENE_FORMAT_SPEC.md section 7.4.",
                )

    # --- stage 9: mathematical verification (reported separately) ---------
    if verify and not report.errors:
        report.verification = run_verification(meta)

    # --- typed document (stage 5's Pydantic view) -------------------------
    document: SceneDocument | None = None
    if not report.errors:
        try:
            document = SceneDocument(
                front_matter=meta, scenes=doc_blocks, prose=parsed.prose
            )
        except PydanticValidationError as exc:  # pragma: no cover - jsonschema precedes
            for err in exc.errors():
                report.error(
                    "schema",
                    str(err["msg"]),
                    path="$." + ".".join(str(p) for p in err["loc"]),
                    suggestion="Compare with SCENE_FORMAT_SPEC.md sections 4-6.",
                )

    # --- scene plan summary for the review page ---------------------------
    if _front_matter_ok(meta):
        report.summary = build_summary(meta, parsed_blocks)

    return report, document


def _front_matter_ok(meta: Any) -> bool:
    return isinstance(meta, dict) and isinstance(meta.get("lesson"), dict) and bool(meta.get("schema_version"))


def _check_semantics(
    report: ValidationReport,
    block: SceneBlockSource,
    doc: dict[str, Any],
    sid: str,
    frame: tuple[float, float, float, float],
    ratio: str,
) -> None:
    """Stage 7-8: reference checks, colors, positions, timing, expressions."""
    src, base_line = block.source, block.start_line
    xmin, xmax, ymin, ymax = frame

    objects = {
        o.get("id"): o
        for o in doc.get("objects") or []
        if isinstance(o, dict) and isinstance(o.get("id"), str)
    }
    actions = [a for a in doc.get("actions") or [] if isinstance(a, dict)]

    if doc.get("objects") and not actions:
        report.error(
            "empty_scene",
            "scene declares objects but has no actions",
            scene=sid,
            line=base_line + 1,
            suggestion="Add at least one action, e.g. '- action: create'.",
        )

    declared_ids = [o.get("id") for o in objects.values()]
    if len(declared_ids) != len(set(declared_ids)):
        report.error(
            "duplicate_id",
            "object ids must be unique within a scene",
            scene=sid,
            line=base_line + 1,
            suggestion="Rename the repeated object id.",
        )

    referenced: set[str] = set()
    for act in actions:
        name = act.get("action")
        tgt = act.get("target")
        targets = [tgt] if isinstance(tgt, str) else (tgt if isinstance(tgt, list) else [])
        for t in targets:
            if not isinstance(t, str):
                continue
            referenced.add(t)
            if t not in objects:
                report.error(
                    "unknown_target",
                    f"action '{name}' targets unknown object '{t}'",
                    scene=sid,
                    path="actions[].target",
                    line=find_line(src, base_line, str(t)),
                    suggestion="Declare the object in 'objects' or fix the id.",
                )
            elif name == "write" and objects[t].get("kind") not in TEXT_KINDS:
                report.error(
                    "kind_mismatch",
                    f"'write' requires a text, formula, or equation object; "
                    f"'{t}' is a {objects[t].get('kind')}",
                    scene=sid,
                    line=find_line(src, base_line, str(t)),
                    suggestion="Use 'create' for this object, or change the object kind.",
                )
        if name == "transform":
            into = act.get("into")
            if isinstance(into, str) and into not in objects:
                report.error(
                    "unknown_target",
                    f"transform target '{into}' is not declared in objects",
                    scene=sid,
                    line=find_line(src, base_line, str(into)),
                    suggestion="Declare the destination object in 'objects'.",
                )
            elif isinstance(into, str):
                referenced.add(into)
                if into in [a.get("target") for a in actions if a.get("action") == "create"]:
                    report.warn(
                        "transform_target",
                        f"'{into}' is both a transform destination and explicitly created; "
                        "transform destinations should stay hidden until the transform",
                        scene=sid,
                        suggestion="Remove the create action for the transform destination.",
                    )

    for obj in objects.values():
        params = obj.get("params") or {}
        if not isinstance(params, dict):
            params = {}
        kind = obj.get("kind")
        if kind in GRAPH_KINDS and not any(o.get("kind") == "axes" for o in objects.values()):
            report.error(
                "kind_mismatch",
                f"'{kind}' object '{obj.get('id')}' requires an 'axes' object in the same scene",
                scene=sid,
                suggestion="Add an object with kind: axes.",
            )
        expr = params.get("expression")
        if isinstance(expr, str):
            msg = check_expression(expr, {"x"} if kind in GRAPH_KINDS else set())
            if msg:
                report.error(
                    "unsafe_expression",
                    f"expression {expr!r}: {msg}",
                    scene=sid,
                    line=find_line(src, base_line, expr),
                    suggestion="Use only the math grammar from SCENE_FORMAT_SPEC.md section 7.4.",
                )
        col = params.get("color")
        if isinstance(col, str) and not col.startswith("#") and col not in PALETTE:
            report.error(
                "color_unknown",
                f"unknown color '{col}'",
                scene=sid,
                suggestion=f"Use a palette name ({', '.join(sorted(PALETTE))}) or #RRGGBB.",
            )
        if obj.get("id") not in referenced and not any(
            isinstance(a.get("into"), str) and a["into"] == obj.get("id") for a in actions
        ):
            report.warn(
                "unused_object",
                f"object '{obj.get('id')}' is never used by any action",
                scene=sid,
                suggestion="Remove it or add an action that uses it.",
            )

    for act in actions:
        col = act.get("color")
        if isinstance(col, str) and not col.startswith("#") and col not in PALETTE:
            report.error("color_unknown", f"unknown color '{col}'", scene=sid,
                         suggestion="Use a documented palette color or #RRGGBB.")

    _check_positions(report, sid, doc, src, base_line, (xmin, xmax, ymin, ymax), ratio)

    declared_dur = doc.get("duration")
    est = default_duration(doc)
    if isinstance(declared_dur, (int, float)) and actions and est > declared_dur + 5:
        report.error(
            "timing_overflow",
            f"actions run to about {est}s but the scene declares {declared_dur}s",
            scene=sid,
            suggestion="Increase 'duration' or tighten the action timing.",
        )
    if isinstance(declared_dur, (int, float)) and declared_dur < est - 5:
        report.warn(
            "timing_tight",
            f"declared duration {declared_dur}s is much shorter than the estimated {est}s",
            scene=sid,
            suggestion="Consider raising 'duration' for better pacing.",
        )


POSITION_KEYS = ("position", "center", "origin", "start", "end", "vertex", "to")


def _check_positions(
    report: ValidationReport,
    scene_id: str,
    node: Any,
    src: str,
    base_line: int,
    frame: tuple[float, float, float, float],
    ratio: str,
) -> None:
    xmin, xmax, ymin, ymax = frame
    if isinstance(node, dict):
        for key in POSITION_KEYS:
            val = node.get(key)
            if (
                isinstance(val, list)
                and len(val) == 2
                and all(isinstance(v, (int, float)) for v in val)
            ):
                x, y = val
                if not (xmin <= x <= xmax and ymin <= y <= ymax):
                    report.warn(
                        "out_of_frame",
                        f"position {[x, y]} lies outside the {ratio} frame "
                        f"(x {xmin}..{xmax}, y {ymin}..{ymax}); it will be clipped",
                        scene=scene_id,
                        line=find_line(src, base_line, f"{key}:"),
                        suggestion="Move the object inside the frame or change the aspect ratio.",
                    )
        for val in node.values():
            _check_positions(report, scene_id, val, src, base_line, frame, ratio)
    elif isinstance(node, list):
        for item in node:
            _check_positions(report, scene_id, item, src, base_line, frame, ratio)


def build_summary(meta: dict[str, Any], blocks: list[SceneBlockSource]) -> dict[str, Any]:
    """Scene-plan summary shown on the review page (raw-dict based, tolerant)."""
    lesson = meta.get("lesson") or {}
    scenes: list[dict[str, Any]] = []
    total = 0.0
    object_count = 0
    action_count = 0

    for block in blocks:
        doc = block.doc or {}
        duration = doc.get("duration")
        if not isinstance(duration, (int, float)):
            duration = default_duration(doc)
        duration = float(duration)
        total += duration
        objects = [o for o in (doc.get("objects") or []) if isinstance(o, dict)]
        actions = [a for a in (doc.get("actions") or []) if isinstance(a, dict)]
        object_count += len(objects)
        action_count += len(actions)
        formulas: list[str] = []
        for obj in objects:
            params = obj.get("params") or {}
            if not isinstance(params, dict):
                continue
            if obj.get("kind") in ("formula", "equation") and isinstance(params.get("content"), str):
                formulas.append(params["content"])
            elif obj.get("kind") == "fraction":
                num, den = params.get("numerator"), params.get("denominator")
                if isinstance(num, str) and isinstance(den, str):
                    formulas.append(f"{num}/{den}")
        scenes.append(
            {
                "id": str(doc.get("id", "?")),
                "title": str(doc.get("title", "")),
                "type": str(doc.get("type", "")),
                "duration_s": duration,
                "narration": str(doc["narration"]) if isinstance(doc.get("narration"), str) else None,
                "object_count": len(objects),
                "action_count": len(actions),
                "formulas": formulas,
            }
        )

    def _str_list(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(v) for v in value if isinstance(v, (str, int, float))]

    return {
        "title": str(lesson.get("title", "")),
        "topic": str(lesson.get("topic", "")),
        "grade": str(lesson.get("grade", "")),
        "language": str(lesson.get("language", "")),
        "duration_minutes": float(lesson.get("duration_minutes", 5) or 5),
        "aspect_ratio": str(lesson.get("aspect_ratio", "16:9")),
        "theme": str(lesson.get("theme", "midnight")),
        "objectives": _str_list(meta.get("objectives")),
        "prerequisites": _str_list(meta.get("prerequisites")),
        "recap": str(meta["recap"]) if isinstance(meta.get("recap"), str) else None,
        "practice_questions": _str_list(meta.get("practice_questions")),
        "scenes": scenes,
        "total_duration_s": round(total, 2),
        "object_count": object_count,
        "action_count": action_count,
    }


def validate_path(path: Path, *, verify: bool = True) -> tuple[ValidationReport, SceneDocument | None]:
    """Convenience wrapper used by tests and the examples corpus check."""
    raw = path.read_bytes()
    return validate_bytes(raw, filename=path.name, verify=verify)
