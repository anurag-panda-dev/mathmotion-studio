"""Examples corpus check: every shipped example must validate with zero errors.

This is the guard ``docs/ROADMAP.md`` asks for: the examples double as a
regression corpus, so a parser/validation change that breaks a shipped
lesson fails here first.
"""

from __future__ import annotations

import pytest

from app.validation.pipeline import validate_path


def test_examples_directory_exists(examples_dir):
    assert examples_dir.is_dir(), "prompts/examples/ is part of the installation"


def _lesson_paths(examples_dir):
    """Lesson files only — README.md documents the folder, it is not a scene."""
    return sorted(p for p in examples_dir.glob("*.md") if p.name != "README.md")


def test_every_example_validates_with_zero_errors(examples_dir):
    paths = _lesson_paths(examples_dir)
    assert paths, "expected at least one example lesson"
    failures: list[str] = []
    for path in paths:
        report, document = validate_path(path, verify=True)
        if report.errors:
            rendered = "; ".join(f"{e.category}: {e.message}" for e in report.errors[:4])
            failures.append(f"{path.name}: {rendered}")
        if document is None:
            failures.append(f"{path.name}: no typed document produced")
    assert not failures, "examples must all be error-free:\n" + "\n".join(failures)


def test_examples_have_no_warnings_that_indicate_broken_puzzles(examples_dir):
    """Warnings are allowed, but an example should not trip structural ones."""
    structural = {"duplicate_id", "unknown_target", "kind_mismatch", "color_unknown"}
    bad: list[str] = []
    for path in _lesson_paths(examples_dir):
        report, _ = validate_path(path, verify=False)
        for w in report.warnings:
            if w.category in structural:
                bad.append(f"{path.name}: {w.category}: {w.message}")
    assert not bad, "\n".join(bad)


@pytest.mark.parametrize(
    "name",
    [
        "pythagorean-theorem.md",
        "fractions-equivalent.md",
        "triangle-geometry.md",
        "linear-equations.md",
        "derivative-visualization.md",
    ],
)
def test_documented_examples_exist(examples_dir, name):
    """The five lesson topics named in MASTER-PROMPT.md section 11 must ship."""
    assert (examples_dir / name).is_file(), f"{name} is documented as a shipped example"
