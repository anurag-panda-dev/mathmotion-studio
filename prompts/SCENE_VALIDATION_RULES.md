# Scene format validation rules

> **Status:** Specification, implemented in [`tools/validate_scene.py`](../tools/validate_scene.py) (schema tooling). The application's import pipeline is not yet implemented ([`docs/ROADMAP.md`](../docs/ROADMAP.md)); when it is, it must implement exactly these rules so prompt templates, examples, and the app agree.
>
> Format reference: [`prompts/SCENE_FORMAT_SPEC.md`](SCENE_FORMAT_SPEC.md). This document explains *what is checked, why a scene may be rejected, and how errors are presented*.

## 1. Validation stages

An imported `scene.md` passes through these stages in order. A failure stops the pipeline at that stage; the teacher never sees a partial render caused by a later-stage problem.

| # | Stage | Checks | Implemented in reference validator |
|---|---|---|---|
| 1 | File intake | Extension `.md`, size ≤ 512 KB | yes |
| 2 | Encoding | UTF-8 (BOM tolerated) | yes |
| 3 | Front matter split | Opening and closing `---` present | yes |
| 4 | YAML parse | Front matter and every `scene` block parse with a *safe* YAML loader (no object construction) | yes |
| 5 | Schema version | `schema_version` equals a supported version | yes |
| 6 | Metadata schema | [`schema/lesson-metadata-v1.schema.json`](../schema/lesson-metadata-v1.schema.json) | yes |
| 7 | Scene schema | [`schema/scene-v1.schema.json`](../schema/scene-v1.schema.json) per block | yes |
| 8 | Reference & semantics | Unique scene/object ids; action targets exist; `write` targets are text-like; `transform.into` declared; `function_graph`/`area_fill` require `axes`; color names known; positions inside the frame (warning); timing vs declared duration; unused objects (warning) | yes |
| 9 | Expression safety | Math grammar via AST allowlist — never `eval` | yes |
| 10 | Mathematical verification | Optional `verification` assertions evaluated with SymPy/NumPy; reported separately from syntax validity | planned (app) |
| 11 | Resource limits | Per-file caps (40 objects, 120 actions, 10 verification assertions, 12 markers) | yes (via schema) |
| 12 | Layout & compile | Scene planning, trusted Manim component compilation, sandboxed render | planned (app) |

Run the validator yourself:

```powershell
python tools\validate_scene.py prompts\examples\pythagorean-theorem.md
python tools\validate_scene.py my-scene.md --json
```

## 2. Error object shape

Every rejection is a structured record, not a prose blob:

| Field | Meaning |
|---|---|
| `category` | Machine-readable failure class (§3). |
| `scene` | Scene id the error belongs to, or file-level. |
| `path` | Field path inside the document, e.g. `objects[2].params.radius`. |
| `line` | Source line when available (best effort in the reference validator; exact in the planned app parser). |
| `message` | Human-readable explanation in plain language. |
| `suggestion` | A concrete correction the teacher — or an external AI correction prompt — can act on. |

Warnings use the same shape but never block an import. **Errors and warnings are always reported separately**; a scene with warnings can still render.

## 3. Error categories

| Category | Severity | Meaning | Typical fix |
|---|---|---|---|
| `file_too_large` | error | File exceeds 512 KB. | Split the lesson. |
| `encoding` | error | Not valid UTF-8. | Re-save as UTF-8. |
| `missing_front_matter` | error | No `---` delimited front matter. | Regenerate with the current prompt template. |
| `yaml_syntax` | error | YAML could not be parsed (unclosed quote, bad indentation, tab characters). | Fix quoting/indentation; usually easiest to ask the AI for a corrected file. |
| `schema_version` | error | Unsupported or missing version. | Use `schema_version: "1.0"`. |
| `schema` | error | Field missing, wrong type, out of range, or **unknown field present**. | Compare with the field tables in the spec. Unknown fields are rejected so typos never silently discard intent. |
| `duplicate_id` | error | Repeated scene or object id. | Rename one of them. |
| `unknown_target` | error | Action references an object that is not declared. | Declare it or fix the id. |
| `kind_mismatch` | error | Action impossible for the object kind (e.g. `write` on a circle, graph without `axes`). | Use a suitable action or kind. |
| `unsafe_expression` | error | Expression leaves the restricted math grammar. | Use only allowlisted operators/functions (spec §7.4). |
| `color_unknown` | error | Color is neither palette name nor `#RRGGBB`. | Use a documented color. |
| `timing_overflow` | error | Actions exceed the declared scene duration by > 5 s. | Raise `duration` or tighten timing. |
| `empty_scene` | error | No scene blocks, or a scene with objects but no actions. | Add scene content. |
| `verification_failed` | error* | A declared mathematical assertion evaluated to a different result. (*Reported as verification failure, separate from syntax.) | Correct the mathematics; do not delete the assertion to hide it. |
| `out_of_frame` | warning | Object positioned outside the visible frame. | Move it inside or change aspect ratio. |
| `unused_object` | warning | Declared object never referenced. | Remove it or use it. |
| `timing_tight` | warning | Declared duration much shorter than estimated pacing. | Raise `duration`. |
| `transform_target` | warning | A `transform` destination is also explicitly created. | Remove the explicit create. |

## 4. Principles

1. **Reject, never guess.** Ambiguous or unsupported instructions produce an error, not a plausible-looking misinterpretation.
2. **Never silently discard.** Unsupported constructs are reported; nothing is dropped "to make it work".
3. **Teacher language first.** The teacher-facing message explains what is wrong in teaching terms; the technical detail (field path, line, category) lives in an expandable diagnostic panel.
4. **Errors are actionable.** Every error carries a suggestion. The correction prompt template ([`prompts/SCENE_CORRECTION_PROMPT.md`](SCENE_CORRECTION_PROMPT.md)) feeds these records back to an external AI verbatim.
5. **Syntax ≠ mathematics.** Passing validation means the file is well-formed. Only `verification` assertions — reported separately — speak to mathematical correctness, and only for the relationships they cover.
