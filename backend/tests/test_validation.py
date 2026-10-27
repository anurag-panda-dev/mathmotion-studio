"""Validation pipeline tests: parity rules, categories, verification, summary."""

from __future__ import annotations

from app.validation.pipeline import default_duration, validate_source


def _scene(body: str) -> str:
    """Wrap scene-block YAML in a minimal valid document."""
    return (
        "---\nschema_version: '1.0'\nlesson:\n  title: T\n  topic: t\n"
        "  grade: '8'\n  language: en\n---\n\n```scene\n" + body + "\n```\n"
    )


def test_valid_document_passes_with_zero_errors(valid_markdown):
    report, document = validate_source(valid_markdown, filename="pythagorean-theorem.md")
    assert report.ok, [e.message for e in report.errors]
    assert document is not None
    assert len(document.scenes) == 4


def test_missing_front_matter_is_error():
    report, document = validate_source("# just markdown\n")
    assert document is None
    assert report.errors[0].category == "missing_front_matter"


def test_bare_ai_file_imports_with_zero_errors(valid_markdown):
    """The ideal AI response (bare file, per the prompt contract) imports clean.

    This is the path the copied prompt promises: no wrapper, no commentary,
    front matter on line 1. Verified against the reference validator too
    (tools/validate_scene.py exits 0 on the same content - the examples corpus
    is its regression suite).
    """
    report, document = validate_source(valid_markdown, filename="scene.md")
    assert report.ok, [e.message for e in report.errors]
    assert document is not None


def test_ai_commentary_prefix_is_rejected_not_misparsed(valid_markdown):
    """A chatty prefix ("Here is your scene.md:") is a blocking error with a fix.

    Errors block imports; the teacher must be told exactly how to recover
    (prompts/AI_COMPATIBILITY.md section 2 row 1). Mirrors the reference
    validator, which reports the same missing_front_matter error.
    """
    report, document = validate_source("Here is your scene.md:\n\n" + valid_markdown)
    assert document is None
    assert report.errors[0].category == "missing_front_matter"
    assert "first line" in (report.errors[0].suggestion or "")


def test_ai_outer_fence_wrapper_is_rejected(valid_markdown):
    """Outer ```markdown fence + chatter -> one clear error, never a crash."""
    wrapped = "Sure! Here is the file:\n\n```markdown\n" + valid_markdown + "\n```\n"
    report, document = validate_source(wrapped)
    assert document is None
    assert report.errors[0].category == "missing_front_matter"


def test_ai_yaml_fences_report_empty_scene(valid_markdown):
    """```yaml instead of ```scene -> empty_scene (blocks; reference agrees)."""
    report, document = validate_source(valid_markdown.replace("```scene", "```yaml"))
    assert document is None
    assert any(e.category == "empty_scene" for e in report.errors)


def test_unsupported_schema_version():
    text = "---\nschema_version: '9.9'\nlesson:\n  title: T\n---\n\n```scene\nid: s1\n```\n"
    report, document = validate_source(text)
    assert document is None
    assert any(e.category == "schema_version" for e in report.errors)


def test_language_full_name_is_valid():
    """Generated files write the language in full (``English``), not as ``en``.

    The prompt template substitutes the teacher's input verbatim (default
    ``English``), so full names are the common case and must validate.
    BCP-47 tags stay valid for older files - see the tag test below.
    """
    text = _scene(
        "id: s1\ntitle: T\ntype: intro\nobjects: []\n"
        "actions:\n  - { action: wait, at: 0, duration: 1 }"
    ).replace("language: en", "language: English")
    report, document = validate_source(text)
    assert report.ok, [e.message for e in report.errors]
    assert document is not None


def test_language_bcp47_tag_still_valid():
    """Tags (``en``, ``pt-BR``) remain valid - older scene.md files must import."""
    text = _scene(
        "id: s1\ntitle: T\ntype: intro\nobjects: []\n"
        "actions:\n  - { action: wait, at: 0, duration: 1 }"
    )
    report, document = validate_source(text)
    assert report.ok, [e.message for e in report.errors]
    assert document is not None


def test_language_rejects_numeric_or_empty():
    """A missing or non-language value is a schema error, never a crash."""
    for bad in ("12", ""):
        text = _scene(
            "id: s1\ntitle: T\ntype: intro\nobjects: []\n"
            "actions:\n  - { action: wait, at: 0, duration: 1 }"
        ).replace("language: en", f"language: '{bad}'")
        report, _ = validate_source(text)
        assert not report.ok
        assert any(e.category == "schema" for e in report.errors)


def test_duplicate_scene_id():
    text = (
        "---\nschema_version: '1.0'\nlesson:\n  title: T\n  topic: t\n"
        "  grade: '8'\n  language: en\n---\n\n"
        "```scene\nid: s1\ntitle: One\ntype: intro\nobjects: []\n"
        "actions:\n  - { action: wait, at: 0, duration: 1 }\n```\n\n"
        "```scene\nid: s1\ntitle: Two\ntype: intro\nobjects: []\n"
        "actions:\n  - { action: wait, at: 0, duration: 1 }\n```\n"
    )
    report, _ = validate_source(text)
    assert any(e.category == "duplicate_id" for e in report.errors)


def test_unknown_target_is_error():
    text = _scene(
        "id: s1\ntitle: T\ntype: intro\nobjects: []\n"
        "actions:\n  - { action: create, target: ghost, at: 0 }"
    )
    report, _ = validate_source(text)
    assert any(e.category == "unknown_target" for e in report.errors)


def test_write_requires_text_kind():
    text = _scene(
        "id: s1\ntitle: T\ntype: intro\n"
        "objects:\n  - id: dot\n    kind: point\n    params:\n      position: [0, 0]\n"
        "actions:\n  - { action: write, target: dot, at: 0 }"
    )
    report, _ = validate_source(text)
    assert any(e.category == "kind_mismatch" and "write" in e.message for e in report.errors)


def test_graph_kind_requires_axes():
    text = _scene(
        "id: s1\ntitle: T\ntype: intro\n"
        "objects:\n"
        "  - id: g\n    kind: function_graph\n    params:\n      expression: 'x**2'\n"
        "actions:\n  - { action: create, target: g, at: 0 }"
    )
    report, _ = validate_source(text)
    assert any("axes" in e.message for e in report.errors)


def test_unknown_color_is_error():
    text = _scene(
        "id: s1\ntitle: T\ntype: intro\n"
        "objects:\n  - id: t1\n    kind: text\n    params:\n"
        "      content: Hi\n      color: magenta\n"
        "actions:\n  - { action: create, target: t1, at: 0 }"
    )
    report, _ = validate_source(text)
    assert any(e.category == "color_unknown" for e in report.errors)


def test_unsafe_expression_is_error():
    text = _scene(
        "id: s1\ntitle: T\ntype: intro\n"
        "objects:\n"
        "  - id: ax\n    kind: axes\n"
        "  - id: g\n    kind: function_graph\n    params:\n"
        "      expression: '__import__(\"os\").system(\"x\")'\n"
        "actions:\n  - { action: create, target: ax, at: 0 }\n"
        "  - { action: create, target: g, at: 1 }"
    )
    report, _ = validate_source(text)
    assert any(e.category == "unsafe_expression" for e in report.errors)


def test_out_of_frame_is_warning_not_error():
    text = _scene(
        "id: s1\ntitle: T\ntype: intro\n"
        "objects:\n  - id: t1\n    kind: text\n    params:\n"
        "      content: Hi\n      position: [9, 9]\n"
        "actions:\n  - { action: create, target: t1, at: 0 }"
    )
    report, _ = validate_source(text)
    assert report.ok
    assert any(w.category == "out_of_frame" for w in report.warnings)


def test_unused_object_is_warning():
    text = _scene(
        "id: s1\ntitle: T\ntype: intro\n"
        "objects:\n  - id: used\n    kind: text\n    params:\n      content: A\n"
        "  - id: unused\n    kind: text\n    params:\n      content: B\n"
        "actions:\n  - { action: create, target: used, at: 0 }"
    )
    report, _ = validate_source(text)
    assert report.ok
    assert any(w.category == "unused_object" for w in report.warnings)


def test_timing_overflow_is_error():
    text = _scene(
        "id: s1\ntitle: T\ntype: intro\nduration: 2\nobjects: []\n"
        "actions:\n  - { action: wait, at: 0, duration: 60 }"
    )
    report, _ = validate_source(text)
    assert any(e.category == "timing_overflow" for e in report.errors)


def test_default_duration_matches_reference_semantics():
    actions = [
        {"action": "create", "target": "a", "at": 0, "duration": 2},
        {"action": "write", "target": "a", "at": 5},  # write default 2.0
        {"action": "wait", "at": 8, "duration": 2},
    ]
    # max end = 8 + 2 = 10; + 1.5 tail = 11.5
    assert default_duration({"actions": actions}) == 11.5


def test_summary_has_scenes_and_totals(valid_markdown):
    report, _ = validate_source(valid_markdown)
    assert report.summary is not None
    assert report.summary["object_count"] > 0
    assert len(report.summary["scenes"]) == 4
    assert report.summary["total_duration_s"] > 0


def test_verification_runs_and_passes_on_example(valid_markdown):
    report, _ = validate_source(valid_markdown, verify=True)
    assert report.verification, "example declares verification assertions"
    assert all(v.status == "passed" for v in report.verification), [
        (v.id, v.message) for v in report.verification
    ]
