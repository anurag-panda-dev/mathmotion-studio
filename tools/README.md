# Schema tooling

> **Status:** This directory contains **schema tooling, not the application**. The MathMotion Studio backend (FastAPI + Manim) is not yet implemented — see [`docs/ROADMAP.md`](../docs/ROADMAP.md). These scripts exist so the scene format specification, prompt templates, and example scenes can be verified today, and so the future backend parser has an executable reference for the same rules.

## `validate_scene.py`

Reference validator for scene format v1.0. Implements validation stages 1–9 and 11 of [`prompts/SCENE_VALIDATION_RULES.md`](../prompts/SCENE_VALIDATION_RULES.md) (file intake, encoding, front-matter split, safe YAML parse, schema version, both JSON schemas, reference/semantic checks, AST-based expression safety, resource caps). Mathematical verification assertions (stage 10) and rendering (stage 12) belong to the future application.

**Requirements:** Python 3.11+, `pyyaml`, `jsonschema` (draft 2020-12).

```powershell
python tools\validate_scene.py prompts\examples\pythagorean-theorem.md   # human-readable report
python tools\validate_scene.py my-scene.md --json                        # structured report
python tools\validate_scene.py my-scene.md --quiet                       # exit code only
python tools\validate_scene.py --version                                 # prints: scene-format 1.0
```

**Exit codes:** `0` valid (warnings allowed) · `1` errors found · `2` usage or environment error.

**Safety:** expression checking parses with Python's `ast` module and an allowlist — it never calls `eval`, and scene YAML is loaded with `yaml.safe_load`.

## `build_brand_svgs.py`

Generator for the six SVGs in [`branding/`](../branding/). It embeds the owner-provided potrace outlines (`assets/cleanvector-sample.svg`) as the ink layer and re-traces violet/ivory color masks (pixel-classified from the raster masters in `assets/`) with the potrace algorithm to produce the separate trajectory and icon layers. Outputs are **generated, not hand-drawn** — edit the script or its inputs and regenerate instead of editing the SVGs.

**Requirements:** Python 3.11+, `numpy`, `Pillow`, `potracer` (`pip install potracer`).

```powershell
python tools\build_brand_svgs.py   # rewrites all six SVGs in branding/
```

Provenance, tuned trace parameters, and measured fidelity numbers are documented in [`branding/assets-manifest.md`](../branding/assets-manifest.md).

This validator is exercised by the documentation consistency routine in [`docs/TESTING.md`](../docs/TESTING.md): every file in `prompts/examples/` must pass with zero errors before documentation changes are committed.
