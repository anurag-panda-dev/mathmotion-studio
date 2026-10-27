"""Compiler tests: trusted generation, data-not-code embedding, render plans."""

from __future__ import annotations

import py_compile
import tempfile
from pathlib import Path

from app.rendering.compiler import compile_document
from app.rendering.layouts import build_render_plan
from app.validation.pipeline import validate_source


def _document(valid_markdown):
    report, document = validate_source(valid_markdown)
    assert document is not None, [e.message for e in report.errors]
    return document


def test_compile_produces_importable_source(valid_markdown, settings):
    compiled = compile_document(_document(valid_markdown), quality="preview")
    assert "class Lesson(Scene)" in compiled.source
    assert "PAYLOAD = json.loads(" in compiled.source
    assert compiled.scene_count == 4
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "generated_scene.py"
        path.write_text(compiled.source, encoding="utf-8")
        # py_compile catches syntax errors without importing Manim.
        py_compile.compile(str(path), doraise=True)


def test_compiled_payload_is_data_not_code(valid_markdown):
    """Scene text must appear only inside the JSON literal, never as code."""
    document = _document(valid_markdown)
    compiled = compile_document(document)
    # The known title appears in the payload; the code around it must not
    # reference it as an identifier or statement.
    assert "The Pythagorean Theorem" in compiled.source
    source_without_literal = compiled.source.split("PAYLOAD = json.loads(", 1)[0]
    assert "Pythagorean" not in source_without_literal
    # No eval/exec anywhere in generated code.
    assert "eval(" not in compiled.source
    assert "exec(" not in compiled.source


def test_compile_hostile_string_stays_inside_literal(valid_markdown):
    """A payload value that looks like code must not escape the literal."""
    document = _document(valid_markdown)
    # Inject a hostile-looking title through the typed model.
    object.__setattr__(document.front_matter.lesson, "title", 'x"); import os; ("')
    compiled = compile_document(document)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "generated_scene.py"
        path.write_text(compiled.source, encoding="utf-8")
        py_compile.compile(str(path), doraise=True)  # still valid Python
    assert 'import os' in compiled.source  # present, but only as data text


def test_render_plan_matches_spec_frames():
    plan = build_render_plan("16:9", "standard")
    assert plan.frame == (-7.0, 7.0, -4.0, 4.0)
    assert plan.resolution == (1260, 720)
    assert plan.frame_rate == 30

    portrait = build_render_plan("9:16", "preview")
    assert portrait.frame == (-4.0, 4.0, -7.0, 7.0)
    assert portrait.resolution == (480, 840)

    square = build_render_plan("1:1", "high")
    assert square.frame == (-4.5, 4.5, -4.5, 4.5)
    assert square.resolution == (1080, 1080)


def test_resolution_pixel_ratio_matches_frame_ratio():
    from app.schemas.scene import FRAMES, QUALITIES, RESOLUTIONS

    for (ratio, quality), (w, h) in RESOLUTIONS.items():
        xmin, xmax, ymin, ymax = FRAMES[ratio]
        frame_ratio = (xmax - xmin) / (ymax - ymin)
        assert abs(w / h - frame_ratio) < 1e-6, f"{ratio}/{quality} pixel ratio drifts"
        assert quality in QUALITIES


def test_compile_embeds_frame_geometry_in_source(valid_markdown):
    compiled = compile_document(_document(valid_markdown), aspect_ratio="9:16", quality="preview")
    assert "manim_config.frame_height = 14.0" in compiled.source
    assert "manim_config.frame_width = 8.0" in compiled.source
    assert "manim_config.pixel_width = 480" in compiled.source
    assert "manim_config.pixel_height = 840" in compiled.source
    assert compiled.plan.frame_rate == 15
