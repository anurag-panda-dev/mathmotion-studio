# Examples — Prompt Builder Test Topics (West Bengal Syllabus)

Syllabus-aligned topics for exercising the prompt generator, the Scene review
page, and the render pipeline. Each entry notes which Scene format object kinds
it should exercise (see `prompts/SCENE_FORMAT_SPEC.md` — 19 object kinds,
15 actions).

Use these against `POST /api/v1/prompt` (Create Animation screen) or the
bundled baseline `prompts/examples/pythagorean-theorem.md`.

---

## Suggested first runs

| Order | Topic | Why start here |
|-------|-------|----------------|
| 1 | Pythagorean theorem | Validated bundled example — compare generated output against `prompts/examples/pythagorean-theorem.md`. |
| 2 | `(a + b)²` visual proof | Area decomposition of a big square into `a²`, `b²` and two `2ab` rectangles — stresses `square`, `rectangle` + `formula` labelling. |
| 3 | Graph of a quadratic function | `axes` + `function_graph` + `point` — good check that plotting coordinates come back sane. |
| 4 | Rational numbers on a number line | `number_line` + `point` + `fraction` — simplest possible scene, fast to validate. |
| 5 | Volume of a cube | **Out-of-scope honesty test** — 3D concepts are outside Scene v1.0; the prompt should *not* pretend to render solid geometry. |

---

## Class 7

| Topic | Expected object kinds |
|-------|----------------------|
| Integers on a number line | `number_line`, `point`, `text` |
| Properties of triangles (angle sum) | `triangle`, `angle`, `equation`, `text` |
| Congruence of triangles | `triangle`, `segment`, `angle`, `text` |
| Perimeter and area of plane figures | `rectangle`, `polygon`, `formula`, `text` |
| Rational numbers (comparison, ordering) | `number_line`, `fraction`, `point` |
| Algebraic expressions | `formula`, `equation`, `text` |
| Simple equations | `equation`, `text`, `formula` |
| Data handling (bar graphs) | `axes`, `rectangle`, `text`, `point` |

## Class 8

| Topic | Expected object kinds |
|-------|----------------------|
| Rational numbers (operations) | `number_line`, `fraction`, `equation` |
| Linear equations in one variable | `equation`, `text`, `formula` |
| Understanding quadrilaterals | `polygon`, `square`, `rectangle`, `angle` |
| Squares and square roots | `formula`, `equation`, `text` |
| Cubes and cube roots | `formula`, `equation`, `text` (3D — honesty check) |
| Comparing quantities (percentages, simple interest) | `formula`, `equation`, `text` |
| Mensuration (area, volume formulas) | `rectangle`, `square`, `formula`, `text` |
| Exponents and powers | `formula`, `equation`, `text` |

## Class 9

| Topic | Expected object kinds |
|-------|----------------------|
| Number systems (rational vs irrational) | `number_line`, `point`, `text` |
| Polynomials | `formula`, `equation`, `text` |
| Coordinate geometry (Cartesian plane) | `axes`, `point`, `segment`, `text` |
| Linear equations in two variables | `axes`, `line`, `equation` |
| Euclid's geometry / axioms and postulates | `line`, `segment`, `ray`, `text` |
| Angles and lines (parallel lines, transversal) | `line`, `ray`, `angle`, `text` |
| Triangles (congruence, inequalities) | `triangle`, `angle`, `segment` |
| Heron's formula | `triangle`, `segment`, `formula`, `text` |

## Class 10

| Topic | Expected object kinds |
|-------|----------------------|
| Real numbers (Euclid's division lemma) | `number_line`, `equation`, `text` |
| Arithmetic progressions | `number_line`, `equation`, `text` |
| Quadratic equations | `equation`, `formula`, `text` |
| **Graph of a quadratic function** | `axes`, `function_graph`, `point` |
| **Pythagorean theorem** | `triangle`, `angle`, `square`, `formula`, `text` |
| Triangles (similarity, Thales theorem) | `triangle`, `line`, `segment`, `text` |
| **Coordinate geometry (section formula)** | `axes`, `point`, `segment`, `equation` |
| Circles (tangents, chord properties) | `circle`, `line`, `ray`, `angle` |

---

## West Bengal–specific checks

1. **Bengali language** — set *Language* to `বাংলা` and confirm the generated
   prompt requests Bengali labels/narration end-to-end (not just an English
   topic translated at the top).
2. **Local-context additional instructions** — add something like
   *"use examples from daily life in Bengal (bus fares, rice fields, Durga Puja
   pandals)"* in the *Additional instructions* field and verify it survives into
   both the full and compact prompts without being truncated.

---

## Testing tip

Generate at **Preview quality** first (15 fps, 840×480) — fast iteration for
validating the scene before spending time on standard (30 fps) or high (60 fps)
renders. Remember: **Render Animation stays disabled until scene validation
passes**, so an invalid scene is expected to show its error count on the review
page rather than a fake progress bar.
