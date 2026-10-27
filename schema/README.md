# Scene format schemas

Machine-readable JSON Schemas (draft 2020-12) for the MathMotion Studio scene format **v1.0**.

> **Status:** Specification artifacts. The application parser is not yet implemented ([`docs/ROADMAP.md`](../docs/ROADMAP.md)). These schemas, the reference validator, and the prompt templates must always describe the same format; changing the format requires updating all three together.

| File | Validates |
|---|---|
| [`lesson-metadata-v1.schema.json`](lesson-metadata-v1.schema.json) | The YAML front matter of a `scene.md` file (lesson metadata, objectives, recap, practice questions, verification assertions). |
| [`scene-v1.schema.json`](scene-v1.schema.json) | A single ` ```scene ` fenced block (scene fields, 19 object kinds with per-kind parameters, 15 action types with per-action fields). |

Human-readable specification: [`prompts/SCENE_FORMAT_SPEC.md`](../prompts/SCENE_FORMAT_SPEC.md).
Reference validator: [`tools/validate_scene.py`](../tools/validate_scene.py) — adds cross-reference, timing, and expression-safety checks that JSON Schema alone cannot express.

```powershell
python tools\validate_scene.py prompts\examples\pythagorean-theorem.md
```

Versioning rules (MAJOR.MINOR, backward-compatible minors, migration adapters): [`prompts/SCENE_FORMAT_SPEC.md` §9](../prompts/SCENE_FORMAT_SPEC.md).
