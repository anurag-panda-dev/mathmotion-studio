# Changelog

All notable changes to MathMotion Studio's **released artifacts** are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/); versioning follows [SemVer](https://semver.org/).

**What has actually been released:** the **Scene format** — its specification, JSON schemas, reference validator, prompt templates, and example corpus — is the only artifact with a released version (v1.0, recorded below as `1.0.0`).

**What has not been released:** the MathMotion Studio *application* (launcher, backend, frontend, renderer) does not exist yet and has never shipped a release. There is no application version number, and none is invented here. Planned application work is tracked under [Unreleased](#unreleased) and sequenced in [ROADMAP.md](ROADMAP.md); product requirements are in [PRD.md](PRD.md).

Versioning note: the Scene format documents itself as **v1.0** using MAJOR.MINOR (per the specification's versioning contract, §9). This changelog uses three-segment SemVer, so that release appears as `1.0.0`.

---

## [Unreleased]

### MathMotion Studio application — planned, not implemented

No application code has been written; nothing in this section exists in the repository. These entries describe the intended first application release and are labelled **Planned** so they can never be mistaken for shipped work. They map to milestones [M1–M10 in ROADMAP.md](ROADMAP.md#roadmap-overview).

- **Planned** — `run.ps1` launcher with automated environment checks, `-Setup` / `-Dev` / `-Diagnostics` modes, and clean process shutdown (M1).
- **Planned** — FastAPI backend with versioned `/api/v1` endpoints, typed models, and loopback-only local binding (M1).
- **Planned** — React frontend: dashboard, Create Animation form, and the in-app prompt generator assembled from the master prompt template (M2–M3).
- **Planned** — Import Scene pipeline: in-app scene.md parser and Pydantic models implementing exactly the validation rules already frozen in the Scene format (M4).
- **Planned** — Trusted declarative compiler and Manim component registry covering the Scene format v1.0 vocabulary; mathematical verification reported separately from render success (M5).
- **Planned** — Render job pipeline: subprocess worker, job lifecycle, cancellation, honest progress, per-job logs, output verification (M6).
- **Planned** — Scene review, animation preview/player, MP4 download, and the My Animations library (M7).
- **Planned** — SQLite persistence, full Settings, dependency diagnostics, and recovery behavior (M8).
- **Planned** — Security hardening, comprehensive automated tests including one end-to-end path, accessibility and performance passes (M9).
- **Planned** — End-to-end verification, clean-install test, and the full teacher-facing documentation set (M10).

When the application ships its first release, it will appear here as a new versioned section with a real date.

## [1.0.0] - date not set

First release of the **Scene format** — the restricted, declarative, versioned format for `scene.md` lesson files. Published as **v1.0** in [`prompts/SCENE_FORMAT_SPEC.md`](../prompts/SCENE_FORMAT_SPEC.md).

*Date marker:* **date not set**. The repository is not yet under version control, so no factual release date can be recorded; none is fabricated.

### Added

- **Scene format specification v1.0** — [`prompts/SCENE_FORMAT_SPEC.md`](../prompts/SCENE_FORMAT_SPEC.md): YAML front matter (lesson metadata, objectives, prerequisites, recap, practice questions, optional verification assertions), fenced `scene` blocks, 19 object kinds with per-kind parameters, 15 action types, a 12-color palette, scene coordinates per aspect ratio (16:9 / 9:16 / 1:1), two themes (midnight / ivory), a restricted AST-allowlisted math-expression grammar, resource caps (512 KB file, ≤40 objects and ≤120 actions per scene, ≤10 verification assertions, ≤12 number-line markers), and the MAJOR.MINOR versioning/migration contract.
- **Lesson-metadata JSON Schema** (draft 2020-12) — [`schema/lesson-metadata-v1.schema.json`](../schema/lesson-metadata-v1.schema.json).
- **Scene-block JSON Schema** (draft 2020-12) — [`schema/scene-v1.schema.json`](../schema/scene-v1.schema.json).
- **Reference validator** — [`tools/validate_scene.py`](../tools/validate_scene.py): implements validation stages 1–9 and 11 of the format's validation pipeline (file intake, encoding, front-matter split, safe YAML parsing, schema-version check, both schemas, reference/semantic checks, AST-based expression safety, resource caps). Human-readable, `--json`, and `--quiet` output modes; exit codes `0` valid / `1` errors / `2` usage-or-environment error. Mathematical verification (stage 10) and rendering (stage 12) are intentionally out of scope for the validator and reserved for the application.
- **Validation rules and error taxonomy** — [`prompts/SCENE_VALIDATION_RULES.md`](../prompts/SCENE_VALIDATION_RULES.md): stage table, structured error object (category, scene, field path, line, message, suggestion), and the reject-never-guess / never-silently-discard / syntax-is-not-mathematics principles.
- **Prompt engineering package** — [`prompts/`](../prompts/): master prompt template with a documented placeholder reference ([`PROMPT_TEMPLATE.md`](../prompts/PROMPT_TEMPLATE.md)), standalone scene-generation prompt ([`SCENE_GENERATION_PROMPT.md`](../prompts/SCENE_GENERATION_PROMPT.md)), scene-correction prompt that consumes validator errors ([`SCENE_CORRECTION_PROMPT.md`](../prompts/SCENE_CORRECTION_PROMPT.md)), and an External-AI compatibility guide ([`AI_COMPATIBILITY.md`](../prompts/AI_COMPATIBILITY.md)).
- **Example corpus** — nine validated example scenes in [`prompts/examples/`](../prompts/examples/) covering arithmetic (equivalent fractions), algebra (linear equations, quadratic functions), geometry (Pythagorean theorem, triangle angle sum, circle area), trigonometry (unit circle), calculus (derivative visualization), and statistics (mean).

### Notes

- **Verification:** all nine example scenes pass the reference validator with zero errors (verified 2026-10-27 with Python 3.11.7).
- **Scope boundary:** this release contains specification artifacts and schema tooling only. The application's scene.md parser, Pydantic models, import pipeline, compiler, and renderer do **not** exist yet ([ROADMAP.md — the Phase 4 split](ROADMAP.md#the-phase-4-split)). Until the application ships, the format is usable with the standalone validator and the manual prompt workflow described in [`prompts/README.md`](../prompts/README.md).
- **Known issue (as of 2026-10-27):** the validator's `--version` flag currently fails with a `NameError` (undefined `SCENE_VERSION`). Core validation is unaffected and verified working; the defect is limited to that flag in [`tools/validate_scene.py`](../tools/validate_scene.py).
