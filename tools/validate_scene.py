#!/usr/bin/env python3
"""Reference validator for the MathMotion Studio scene format v1.0.

Status: schema tooling, not the application. The MathMotion Studio backend is
not yet implemented (see docs/ROADMAP.md). This script validates scene.md
files against the canonical specification in prompts/SCENE_FORMAT_SPEC.md and
the JSON schemas in schema/. The future backend parser will implement the same
rules; this tool exists so documentation, prompt templates, and example scenes
can be verified today.

Usage:
    python tools/validate_scene.py <file.md> [--json] [--quiet]
    python tools/validate_scene.py --version

Exit codes: 0 = valid (warnings allowed), 1 = errors found, 2 = usage error.

Requirements: Python 3.11+, pyyaml, jsonschema (draft 2020-12).
The expression safety check uses an ast allowlist; it never calls eval().
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft202012Validator
except ImportError as exc:  # pragma: no cover
    print(f"Missing dependency: {exc}. Install with: pip install pyyaml jsonschema", file=sys.stderr)
    sys.exit(2)

SCHEMA_VERSION = "1.0"
MAX_FILE_BYTES = 512 * 1024
PALETTE = {
    "navy", "violet", "ivory", "white", "black", "gray",
    "red", "green", "blue", "amber", "teal", "pink",
}
FRAMES = {"16:9": (-7.0, 7.0, -4.0, 4.0), "9:16": (-4.0, 4.0, -7.0, 7.0), "1:1": (-4.5, 4.5, -4.5, 4.5)}
TEXT_KINDS = {"text", "formula", "equation"}
GRAPH_KINDS = {"function_graph", "area_fill"}
ALLOWED_FUNCS = {
    "sin", "cos", "tan", "asin", "acos", "atan", "sqrt", "abs", "ln", "log",
    "log10", "exp", "floor", "ceil", "round", "min", "max",
}
ALLOWED_CONSTS = {"pi", "e"}


@dataclass
class Issue:
    severity: str  # "error" | "warning"
    category: str
    message: str
    scene: str | None = None
    path: str | None = None
    line: int | None = None
    suggestion: str | None = None


@dataclass
class Report:
    file: str
    schema_version: str | None = None
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def load_schema(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def find_line(block_src: str, block_start_line: int, needle: str) -> int | None:
    """Best-effort line lookup for a key/value fragment inside a block."""
    for i, line in enumerate(block_src.splitlines()):
        if needle in line:
            return block_start_line + i
    return None


def check_expression(expr: str, allowed_vars: set[str]) -> str | None:
    """Validate a math expression against the restricted grammar.

    Returns an error message, or None if the expression is acceptable.
    """
    try:
        tree = ast.parse(expr.replace("^", "**"), mode="eval")
    except SyntaxError as exc:
        return f"not parseable as a math expression (syntax error at column {exc.colno})"

    # Function names appear as ast.Name children of their Call node; pre-collect
    # them so allowlisted calls don't trip the unknown-identifier check. The Call
    # branch below still rejects non-allowlisted functions (walk is BFS, so the
    # Call node is always validated before its children).
    called = {
        n.func.id
        for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Expression):
            continue
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                return f"disallowed literal {node.value!r}"
            continue
        if isinstance(node, ast.Name):
            if node.id in allowed_vars or node.id in ALLOWED_CONSTS or node.id in called:
                continue
            return f"unknown identifier '{node.id}' (allowed: {', '.join(sorted(allowed_vars | ALLOWED_CONSTS))})"
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)):
            continue
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            continue
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in ALLOWED_FUNCS:
                name = node.func.id if isinstance(node.func, ast.Name) else "complex expression"
                return f"function '{name}' is not in the allowlist ({', '.join(sorted(ALLOWED_FUNCS))})"
            if node.keywords:
                return "keyword arguments are not allowed"
            continue
        if isinstance(node, (ast.Load, ast.Param)):
            continue
        if isinstance(node, (ast.operator, ast.unaryop)):
            # Op-type children are validated by their parent nodes above
            # (walk visits parents before children), so reaching here means
            # the parent already passed the allowlist.
            continue
        return f"disallowed syntax: {type(node).__name__}"
    return None


def default_duration(scene: dict) -> float:
    cursor = 0.0
    for act in scene.get("actions", []):
        start = act.get("at", cursor)
        dur = act.get("duration", 2.0 if act.get("action") == "write" else 1.0)
        cursor = max(cursor, start + dur)
    return round(cursor + 1.5, 2)


def validate(path: Path) -> Report:
    report = Report(file=str(path))
    err = report.errors.append
    warn = report.warnings.append

    raw = path.read_bytes()
    if len(raw) > MAX_FILE_BYTES:
        err(Issue("error", "file_too_large", f"file is {len(raw)} bytes; limit is {MAX_FILE_BYTES} bytes",
                  suggestion="Split the lesson into smaller scenes or remove unused content."))
        return report
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        err(Issue("error", "encoding", f"file is not valid UTF-8: {exc}", suggestion="Re-save the file as UTF-8."))
        return report

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        err(Issue("error", "missing_front_matter", "file must start with YAML front matter delimited by '---'",
                  line=1, suggestion="Ask the AI to produce the file with '---' on the first line."))
        return report
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        err(Issue("error", "missing_front_matter", "closing '---' delimiter of the front matter is missing",
                  suggestion="Ask the AI to close the front matter block."))
        return report

    fm_src = "\n".join(lines[1:end])
    body_lines = lines[end + 1:]
    body_start = end + 2  # 1-based line number of first body line

    try:
        meta = yaml.safe_load(fm_src) or {}
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        err(Issue("error", "yaml_syntax", f"front matter is not valid YAML: {getattr(exc, 'problem', exc)}",
                  line=(mark.line + 2) if mark else 2, suggestion="Check quoting and indentation."))
        return report

    meta_schema = load_schema(Path(__file__).resolve().parent.parent / "schema" / "lesson-metadata-v1.schema.json")
    scene_schema = load_schema(Path(__file__).resolve().parent.parent / "schema" / "scene-v1.schema.json")

    report.schema_version = str(meta.get("schema_version")) if isinstance(meta, dict) else None
    if isinstance(meta, dict) and meta.get("schema_version") not in (None, SCHEMA_VERSION):
        err(Issue("error", "schema_version",
                  f"schema_version {meta.get('schema_version')!r} is not supported; this validator implements {SCHEMA_VERSION}",
                  line=2, suggestion="Regenerate the scene with a current prompt template."))
        return report

    for issue in sorted(Draft202012Validator(meta_schema).iter_errors(meta), key=lambda e: list(e.path)):
        err(Issue("error", "schema", issue.message,
                  path="$." + ".".join(map(str, issue.path)) if issue.path else "$",
                  suggestion="Compare with the field reference in SCENE_FORMAT_SPEC.md section 3."))

    # --- scene blocks -----------------------------------------------------
    blocks: list[tuple[dict, str, int]] = []
    in_block = False
    buf: list[str] = []
    start_line = 0
    for i, line in enumerate(body_lines, start=body_start):
        stripped = line.strip()
        if not in_block and stripped.startswith("```scene"):
            in_block, buf, start_line = True, [], i
            continue
        if in_block and stripped == "```":
            in_block = False
            src = "\n".join(buf)
            try:
                doc = yaml.safe_load(src)
            except yaml.YAMLError as exc:
                mark = getattr(exc, "problem_mark", None)
                err(Issue("error", "yaml_syntax", f"scene block is not valid YAML: {getattr(exc, 'problem', exc)}",
                          line=(start_line + 1 + mark.line) if mark else start_line + 1,
                          suggestion="Check quoting, indentation, and colons inside strings."))
                continue
            if not isinstance(doc, dict):
                err(Issue("error", "schema", "scene block must be a YAML mapping", line=start_line + 1))
                continue
            blocks.append((doc, src, start_line))
            continue
        if in_block:
            buf.append(line)
    if in_block:
        err(Issue("error", "yaml_syntax", "unterminated ```scene block", line=start_line,
                  suggestion="Every ```scene block must be closed with ```."))

    if not blocks:
        err(Issue("error", "empty_scene", "file contains no ```scene blocks",
                  suggestion="The lesson needs at least one scene block."))

    seen_scene_ids: set[str] = set()
    theme = (meta.get("lesson") or {}).get("theme", "midnight") if isinstance(meta, dict) else "midnight"
    ratio = (meta.get("lesson") or {}).get("aspect_ratio", "16:9") if isinstance(meta, dict) else "16:9"
    xmin, xmax, ymin, ymax = FRAMES.get(ratio, FRAMES["16:9"])

    def check_positions(scene_id: str, node, src: str, base_line: int) -> None:
        if isinstance(node, dict):
            for key in ("position", "center", "origin", "start", "end", "vertex", "to"):
                val = node.get(key)
                if (isinstance(val, list) and len(val) == 2
                        and all(isinstance(v, (int, float)) for v in val)):
                    x, y = val
                    if not (xmin <= x <= xmax and ymin <= y <= ymax):
                        warn(Issue("warning", "out_of_frame",
                                   f"position {[x, y]} lies outside the {ratio} frame (x {xmin}..{xmax}, y {ymin}..{ymax}); it will be clipped",
                                   scene=scene_id, line=find_line(src, base_line, f"{key}:"),
                                   suggestion="Move the object inside the frame or change the aspect ratio."))
            for val in node.values():
                check_positions(scene_id, val, src, base_line)
        elif isinstance(node, list):
            for item in node:
                check_positions(scene_id, item, src, base_line)

    for doc, src, base_line in blocks:
        sid = doc.get("id", "?")
        for issue in sorted(Draft202012Validator(scene_schema).iter_errors(doc), key=lambda e: list(e.path)):
            path_str = "$." + ".".join(map(str, issue.path)) if issue.path else "$"
            err(Issue("error", "schema", issue.message, scene=sid if isinstance(sid, str) else None,
                      path=path_str, line=find_line(src, base_line, str(issue.path[0])) if issue.path else base_line + 1,
                      suggestion="Compare with SCENE_FORMAT_SPEC.md sections 4-6."))
        if not isinstance(sid, str):
            continue
        if sid in seen_scene_ids:
            err(Issue("error", "duplicate_id", f"scene id '{sid}' is used more than once", scene=sid,
                      line=base_line + 1, suggestion="Give each scene a unique id."))
        seen_scene_ids.add(sid)

        objects = {o.get("id"): o for o in doc.get("objects", []) if isinstance(o, dict) and isinstance(o.get("id"), str)}
        actions = [a for a in doc.get("actions", []) if isinstance(a, dict)]
        if doc.get("objects") and not actions:
            err(Issue("error", "empty_scene", "scene declares objects but has no actions",
                      scene=sid, line=base_line + 1, suggestion="Add at least one action, e.g. '- action: create'."))
        declared_ids = [o.get("id") for o in objects.values()]
        if len(declared_ids) != len(set(declared_ids)):
            err(Issue("error", "duplicate_id", "object ids must be unique within a scene", scene=sid, line=base_line + 1))

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
                    err(Issue("error", "unknown_target", f"action '{name}' targets unknown object '{t}'",
                              scene=sid, path=f"actions[].target", line=find_line(src, base_line, f"{t}"),
                              suggestion="Declare the object in 'objects' or fix the id."))
                elif name == "write" and objects[t].get("kind") not in TEXT_KINDS:
                    err(Issue("error", "kind_mismatch", f"'write' requires a text, formula, or equation object; '{t}' is a {objects[t].get('kind')}",
                              scene=sid, line=find_line(src, base_line, f"{t}"),
                              suggestion="Use 'create' for this object, or change the object kind."))
            if name == "transform":
                into = act.get("into")
                if isinstance(into, str) and into not in objects:
                    err(Issue("error", "unknown_target", f"transform target '{into}' is not declared in objects",
                              scene=sid, line=find_line(src, base_line, str(into)),
                              suggestion="Declare the destination object in 'objects'."))
                elif isinstance(into, str):
                    referenced.add(into)
                    if into in [a.get("target") for a in actions if a.get("action") == "create"]:
                        warn(Issue("warning", "transform_target",
                                   f"'{into}' is both a transform destination and explicitly created; transform destinations should stay hidden until the transform",
                                   scene=sid, suggestion="Remove the create action for the transform destination."))
            for key in ("expression",):
                if isinstance(act.get(key), str):
                    pass  # actions carry no expressions in v1
        for obj in objects.values():
            params = obj.get("params") or {}
            kind = obj.get("kind")
            if kind in GRAPH_KINDS and not any(o.get("kind") == "axes" for o in objects.values()):
                err(Issue("error", "kind_mismatch", f"'{kind}' object '{obj.get('id')}' requires an 'axes' object in the same scene",
                          scene=sid, suggestion="Add an object with kind: axes."))
            expr = params.get("expression")
            if isinstance(expr, str):
                msg = check_expression(expr, {"x"} if kind in GRAPH_KINDS else set())
                if msg:
                    err(Issue("error", "unsafe_expression", f"expression {expr!r}: {msg}",
                              scene=sid, line=find_line(src, base_line, expr),
                              suggestion="Use only the math grammar from SCENE_FORMAT_SPEC.md section 7.4."))
            col = params.get("color")
            if isinstance(col, str) and not col.startswith("#") and col not in PALETTE:
                err(Issue("error", "color_unknown", f"unknown color '{col}'", scene=sid,
                          suggestion=f"Use a palette name ({', '.join(sorted(PALETTE))}) or #RRGGBB."))
            if obj.get("id") not in referenced and not any(
                    isinstance(a.get("into"), str) and a["into"] == obj.get("id") for a in actions):
                warn(Issue("warning", "unused_object", f"object '{obj.get('id')}' is never used by any action",
                           scene=sid, suggestion="Remove it or add an action that uses it."))
        for act in actions:
            col = act.get("color")
            if isinstance(col, str) and not col.startswith("#") and col not in PALETTE:
                err(Issue("error", "color_unknown", f"unknown color '{col}'", scene=sid))

        check_positions(sid, doc, src, base_line)

        declared_dur = doc.get("duration")
        est = default_duration(doc)
        if isinstance(declared_dur, (int, float)) and actions and est > declared_dur + 5:
            err(Issue("error", "timing_overflow",
                      f"actions run to about {est}s but the scene declares {declared_dur}s",
                      scene=sid, suggestion="Increase 'duration' or tighten the action timing."))
        if isinstance(declared_dur, (int, float)) and declared_dur < est - 5:
            warn(Issue("warning", "timing_tight",
                       f"declared duration {declared_dur}s is much shorter than the estimated {est}s",
                       scene=sid, suggestion="Consider raising 'duration' for better pacing."))

    # --- verification assertions -----------------------------------------
    if isinstance(meta, dict):
        for v in meta.get("verification", []) or []:
            if not isinstance(v, dict):
                continue
            subs = {k: val for k, val in (v.get("subs") or {}).items()} if isinstance(v.get("subs"), dict) else {}
            msg = check_expression(str(v.get("expression", "")), set(subs))
            if msg:
                err(Issue("error", "unsafe_expression", f"verification '{v.get('id')}': {msg}",
                          path=f"verification.{v.get('id')}"))
    return report


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles
    except (AttributeError, ValueError):  # pragma: no cover
        pass
    parser = argparse.ArgumentParser(description="Validate a MathMotion Studio scene.md file.")
    parser.add_argument("file", nargs="?", help="path to a scene.md file")
    parser.add_argument("--json", action="store_true", help="emit a JSON report")
    parser.add_argument("--quiet", action="store_true", help="suppress per-issue output; only set the exit code")
    parser.add_argument("--version", action="store_true", help="print the implemented scene format version")
    args = parser.parse_args(argv)

    if args.version:
        print(f"scene-format {SCHEMA_VERSION}")
        return 0
    if not args.file:
        parser.print_usage()
        return 2
    path = Path(args.file)
    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    report = validate(path)
    if args.json:
        print(json.dumps(asdict(report), indent=2))
    elif not args.quiet:
        label = "VALID" if report.ok else "INVALID"
        print(f"{label}  {report.file}  (schema {report.schema_version or 'n/a'})")
        for issue in report.errors + report.warnings:
            loc = f"{issue.scene or '-'}.{issue.path or '-'}" if (issue.scene or issue.path) else "-"
            line = f":{issue.line}" if issue.line else ""
            print(f"  [{issue.severity.upper():7}] {issue.category}  {loc}{line}")
            print(f"            {issue.message}")
            if issue.suggestion:
                print(f"            hint: {issue.suggestion}")
        print(f"  {len(report.errors)} error(s), {len(report.warnings)} warning(s)")
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
