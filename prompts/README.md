# Prompt engineering package

Reusable prompt templates for the MathMotion Studio workflow: a teacher fills a form, the application assembles a prompt, the teacher pastes it into any **external AI**, and the AI returns a `scene.md` file that MathMotion Studio validates and renders.

> **Status:** These templates are specification artifacts written against the documented scene format v1.0. The application's prompt-generator page is **not yet implemented** ([`docs/ROADMAP.md`](../docs/ROADMAP.md), Phase 3); until then the templates here can be copied and used manually — that is exactly how the example scenes in [`examples/`](examples/) were conceived.

## Files

| File | Purpose |
|---|---|
| [`PROMPT_TEMPLATE.md`](PROMPT_TEMPLATE.md) | **Master template** with `{{PLACEHOLDERS}}` for every supported teacher input. The future prompt generator fills this; each placeholder documents meaning, default, validation, and empty behavior. |
| [`SCENE_GENERATION_PROMPT.md`](SCENE_GENERATION_PROMPT.md) | Complete standalone prompt for creating a new scene from a topic. Usable as-is, without the application. |
| [`SCENE_CORRECTION_PROMPT.md`](SCENE_CORRECTION_PROMPT.md) | Standalone prompt for fixing an invalid scene: feed it the original file plus the validator errors; it returns a corrected file. |
| [`SCENE_FORMAT_SPEC.md`](SCENE_FORMAT_SPEC.md) | **Canonical scene format specification v1.0** — the single source of truth. Everything else derives from it. |
| [`SCENE_VALIDATION_RULES.md`](SCENE_VALIDATION_RULES.md) | What is validated, error taxonomy, how errors are reported to teachers. |
| [`AI_COMPATIBILITY.md`](AI_COMPATIBILITY.md) | How to use these prompts with different external AI tools, save responses as `scene.md`, and recover from validation failures. |
| [`examples/`](examples/) | Nine validated example scenes covering algebra, geometry, trigonometry, calculus, arithmetic, and statistics. |

## The loop these templates support

```text
teacher inputs ─► PROMPT_TEMPLATE (assembled) ─► external AI ─► scene.md
                                   ▲                             │
                                   │                             ▼
                     SCENE_CORRECTION_PROMPT ◄── validator errors (tools/validate_scene.py
                                                   today; the app import pipeline later)
```

1. Generate → paste into an external AI → save the response as `scene.md`.
2. Validate (`python tools\validate_scene.py scene.md` today; the app's Import Scene page later).
3. If errors: paste the error report + the original scene into **SCENE_CORRECTION_PROMPT** → re-validate.
4. Repeat from 2 until clean, then render.

## Sync rules (important)

The prompt templates embed a condensed copy of the scene schema because external AIs cannot read this repository. Therefore **every format change requires updating, in the same commit:**

1. [`SCENE_FORMAT_SPEC.md`](SCENE_FORMAT_SPEC.md) (canonical),
2. [`schema/*.json`](../schema/) (machine-readable),
3. the schema quick-reference inside `PROMPT_TEMPLATE.md` and `SCENE_GENERATION_PROMPT.md` (AI-facing copy),
4. all [`examples/`](examples/) — re-validated with `tools/validate_scene.py`.

This synchronization is checked by the documentation consistency routine in [`docs/TESTING.md`](../docs/TESTING.md).
