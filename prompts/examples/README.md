# Example scenes

Nine complete, importable `scene.md` files demonstrating the scene format v1.0 across school mathematics. Every file here **passes validation** with zero errors and zero warnings:

```powershell
python tools\validate_scene.py prompts\examples\pythagorean-theorem.md
```

> **Status:** These are format examples, not rendered lessons. The application that renders them is not yet implemented ([`docs/ROADMAP.md`](../../docs/ROADMAP.md)), so **no MP4 previews exist** and none are claimed. Once the renderer lands, each example should be render-tested; that checklist lives in [`docs/TESTING.md`](../../docs/TESTING.md).

| File | Topic / grade | Scene types used |
|---|---|---|
| [`pythagorean-theorem.md`](pythagorean-theorem.md) | Pythagorean theorem / 8 | intro, explanation, recap — canonical worked example (spec §3–§5) |
| [`linear-equations.md`](linear-equations.md) | Straight-line graphs / 9 | intro, explanation, worked_example, recap |
| [`quadratic-functions.md`](quadratic-functions.md) | Quadratic functions / 9 | intro, explanation, recap |
| [`triangle-geometry.md`](triangle-geometry.md) | Sum of triangle angles / 8 | intro, explanation, proof, recap |
| [`trigonometry-unit-circle.md`](trigonometry-unit-circle.md) | Sine and cosine / 10 | intro, explanation, recap |
| [`derivative-visualization.md`](derivative-visualization.md) | Derivatives / 11 | intro, explanation, recap |
| [`fractions-equivalent.md`](fractions-equivalent.md) | Equivalent fractions / 5 | intro, explanation, recap |
| [`circle-area.md`](circle-area.md) | Area of a circle / 7 | intro, explanation, recap |
| [`statistics-mean.md`](statistics-mean.md) | Mean of a data set / 6 | intro, explanation, worked_example, practice |

## Action coverage

Across the set: `create`, `write`, `fade_in`, `fade_out`, `transform`, `move`, `scale`, `indicate`, `circumscribe`, `draw_border`, `recolor`, `wait`, `arrange`, `reveal` are exercised. **`rotate` is not demonstrated in any example** — it is specified in the format but has no natural home in these nine lessons; the future backend test suite should cover it (tracked in [`docs/TESTING.md`](../../docs/TESTING.md)).

## Object coverage

16 of 19 object kinds are exercised. The three kinds **not** demonstrated are `ray`, `polygon` and `vector` — they are specified in [`prompts/SCENE_FORMAT_SPEC.md` §6](../SCENE_FORMAT_SPEC.md) but have no natural home in these nine lessons; the future backend test suite should cover them (tracked in [`docs/TESTING.md`](../../docs/TESTING.md)).

## Editing and re-validating

Examples double as starting points for teachers and prompt engineers. After any edit, re-run the validator; the documentation consistency routine (`docs/TESTING.md`) requires all nine files to pass before changes are committed.
