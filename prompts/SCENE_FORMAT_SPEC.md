# MathMotion Studio — Scene Format Specification (v1.0)

> **Status:** Specification draft. The MathMotion Studio application and its parser are **not yet implemented** (see [`docs/ROADMAP.md`](../docs/ROADMAP.md)). This document defines the canonical, versioned scene format that the future parser, validator, prompt templates, and renderer will all share. It is the single source of truth for the format; other documents link here instead of restating the rules.
>
> Machine-readable schemas: [`schema/lesson-metadata-v1.schema.json`](../schema/lesson-metadata-v1.schema.json) and [`schema/scene-v1.schema.json`](../schema/scene-v1.schema.json). A reference validator is provided in [`tools/validate_scene.py`](../tools/validate_scene.py).

---

## 1. Purpose and design rules

`scene.md` is a plain-text Markdown file that an **external AI** produces from a teacher's prompt and that the teacher imports into MathMotion Studio. The format must be:

- **Readable and editable by a nontechnical teacher** — ordinary Markdown with embedded YAML blocks.
- **Deterministic for the renderer** — every instruction maps to exactly one trusted component in the planned animation registry; nothing is executable code.
- **Strict, never silent** — ambiguous or unsupported instructions are rejected with a located error, never guessed at or ignored.

**Hard rule:** the scene format contains no executable code. No Python, no shell commands, no imports, no expressions beyond the restricted math grammar defined in §7. The renderer translates validated declarations into trusted Manim components; it never executes text from the file.

## 2. File structure

A `scene.md` file has exactly two parts:

```text
---                     ← YAML front matter (lesson metadata, §3)
...YAML...
---                     ← closing delimiter
                        ← Markdown body (free prose + scene blocks, §4–§5)
```

1. **YAML front matter** — mandatory, must be the first bytes of the file (only a UTF-8 BOM may precede it). Contains lesson-level metadata, objectives, optional recap/practice content, and optional verification assertions.
2. **Markdown body** — optional free prose (treated as teacher-facing notes; never rendered) followed by one fenced `scene` block per animation scene, in playback order.

**File-level constraints**

| Constraint | Value |
|---|---|
| Encoding | UTF-8 (optional BOM) |
| Maximum file size | 512 KB (import limit; larger files are rejected before parsing) |
| Front matter delimiter | `---` on its own line, first and second non-empty lines |
| Scene blocks | Fenced code blocks whose info string is exactly `scene` |
| Comments | YAML comments (`# ...`) inside front matter and scene blocks; Markdown comments (`<!-- ... -->`) in the body. Comments are ignored by the renderer. |
| Blank scene blocks | Not allowed — every `scene` block must contain `id`, `title`, and `type` |

## 3. Front matter (lesson metadata)

Validated against [`schema/lesson-metadata-v1.schema.json`](../schema/lesson-metadata-v1.schema.json).

```yaml
---
schema_version: "1.0"
lesson:
  title: The Pythagorean Theorem
  topic: Pythagorean theorem
  grade: "8"
  language: English
  duration_minutes: 5
  aspect_ratio: "16:9"
  theme: midnight
objectives:
  - State the Pythagorean theorem for a right triangle.
  - Verify the relationship on a 3-4-5 triangle.
prerequisites:
  - Squares of whole numbers
  - The concept of a right angle
recap: >-
  For any right triangle with legs a and b and hypotenuse c,
  a² + b² = c². The relation holds only for right triangles.
practice_questions:
  - A right triangle has legs 6 and 8. Find the hypotenuse.
verification:
  - id: v1
    kind: numeric
    description: The 3-4-5 triangle satisfies the theorem.
    expression: 3**2 + 4**2 - 5**2
    expected: 0
---
```

### 3.1 Field reference

| Field | Required | Type | Default | Rules |
|---|---|---|---|---|
| `schema_version` | yes | string | — | Must be exactly `"1.0"` for this schema. See §9 for versioning. |
| `lesson.title` | yes | string | — | 1–140 characters. |
| `lesson.topic` | yes | string | — | 1–140 characters; the mathematics topic. |
| `lesson.grade` | yes | string | — | 1–24 characters, e.g. `"8"` or `"11–12"`. Quoted to avoid YAML number coercion. |
| `lesson.language` | yes | string | — | Full language name (`English`, `Bengali`, `Portuguese (Brazil)`) or BCP-47 tag (`en`, `de`, `pt-BR`); matches `^(?:[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})?\|[^0-9\s][^0-9]{1,39})$`, 2–40 characters. Full names are the recommended style — write the name exactly as the teacher entered it. Used for narration text and labels; the renderer does not translate content. |
| `lesson.duration_minutes` | no | number | `5` | 1–60. Target lesson length; advisory, not enforced. |
| `lesson.aspect_ratio` | no | string | `"16:9"` | One of `"16:9"`, `"9:16"`, `"1:1"`. |
| `lesson.theme` | no | string | `"midnight"` | One of `midnight` (dark background, light ink) or `ivory` (light background, dark ink). |
| `objectives` | no | string[] | `[]` | 0–10 items, each 1–200 characters. Shown on the scene-review page. |
| `prerequisites` | no | string[] | `[]` | 0–10 items, each 1–200 characters. |
| `recap` | no | string | — | 1–1000 characters. Plain text. |
| `practice_questions` | no | string[] | `[]` | 0–12 items, each 1–300 characters. |
| `verification` | no | object[] | `[]` | 0–10 assertions. Optional mathematical checks performed **separately from rendering** (§8). |

Unknown top-level front-matter keys are **rejected** (error category `unsupported_field`), so typos never silently discard teacher intent.

### 3.2 Verification assertion

| Field | Required | Type | Rules |
|---|---|---|---|
| `id` | yes | string | `^[a-z][a-z0-9_-]{0,39}$`, unique among assertions. |
| `kind` | yes | string | `numeric` or `symbolic`. Symbolic checks use SymPy simplification; numeric checks evaluate the expression. |
| `description` | yes | string | 1–200 characters, human-readable. |
| `expression` | yes | string | Restricted math grammar (§7), 1–200 characters. |
| `expected` | yes | number | Expected result. `0` for "identically zero" identities. |
| `tolerance` | no | number | Default `1e-9`; absolute tolerance for numeric comparison. |
| `subs` | no | map | Optional variable bindings, e.g. `{a: 3, b: 4, c: 5}`. Values must be finite numbers. |

## 4. Scene blocks

Each scene is one fenced block in the body, in playback order:

````markdown
```scene
id: s1
title: A right triangle and its squares
type: explanation
duration: 24
narration: >-
  Here is a right triangle. Its two legs are a and b,
  and the longest side, facing the right angle, is c.
objects:
  - id: tri
    kind: triangle
    params:
      vertices: [[-3, -2], [1, -2], [-3, 1.5]]
      labels: [A, B, C]
      color: ivory
  - id: caption
    kind: text
    params:
      content: "a² + b² = c²"
      position: [3.5, 3]
      font_size: 44
      color: violet
actions:
  - action: create
    target: tri
    at: 0
  - action: write
    target: caption
    at: 4
  - action: indicate
    target: tri
    style: pulse
    at: 9
    duration: 2
```
````

Validated against [`schema/scene-v1.schema.json`](../schema/scene-v1.schema.json).

### 4.1 Scene block fields

| Field | Required | Type | Default | Rules |
|---|---|---|---|---|
| `id` | yes | string | — | `^[a-z][a-z0-9_-]{0,39}$`; unique across all scene blocks in the file. |
| `title` | yes | string | — | 1–140 characters. |
| `type` | yes | string | — | `intro`, `explanation`, `worked_example`, `proof`, `recap`, or `practice` (§4.2). |
| `duration` | no | number | computed | Scene length in seconds (0.5–300). If omitted, computed as the latest action start plus its duration, with a 1.5 s tail. |
| `narration` | no | string | — | 1–2000 characters. Voiceover/subtitle source text; never rendered on screen unless a `text` object repeats it. |
| `objects` | no | object[] | `[]` | 0–40 objects, each with `id`, `kind`, optional `params` (§6). Object ids are unique **within the scene**. |
| `actions` | no | object[] | `[]` | 0–120 ordered actions (§5). |

### 4.2 Scene types

| Type | Meaning |
|---|---|
| `intro` | Opening: title, learning goal, orientation. |
| `explanation` | Concept exposition with diagrams, graphs, formulas. |
| `worked_example` | A concrete example solved step by step. |
| `proof` | A visual or deductive justification. |
| `recap` | Summary of what was learned. |
| `practice` | Practice questions for students. |

A lesson should normally begin with `intro` and end with `recap` and/or `practice`, but the format does not enforce ordering.

## 5. Actions

Every action has a discriminator `action` and a `target` (an object id, or an array of object ids). `wait` is the only action without a target.

| Action | Required extra fields | Optional fields | Effect |
|---|---|---|---|
| `create` | `target` | `at`, `duration` | Create object(s) on screen (instant unless `duration` given → fade in). Objects must not already be on screen. |
| `write` | `target` | `at`, `duration` | Write out the content of a `text`, `formula`, or `equation` object character-by-character. |
| `fade_in` | `target` | `at`, `duration` | Fade already-declared object(s) in. |
| `fade_out` | `target` | `at`, `duration` | Fade object(s) out (they remain declared; `fade_in` can return them). |
| `transform` | `target`, `into` | `at`, `duration` | Morph `target` into the declared-but-hidden object `into` (e.g. a secant becoming a tangent). |
| `move` | `target`, `to` | `at`, `duration` | Move one object to a scene position `[x, y]`. |
| `rotate` | `target`, `degrees` | `at`, `duration` | Rotate one object around its own center. |
| `scale` | `target`, `factor` | `at`, `duration` | Scale one object (0.05–20; `1` = unchanged). |
| `indicate` | `target` | `at`, `duration`, `style` | Draw attention to one object. `style`: `pulse` (default), `highlight`, `underline`. |
| `circumscribe` | `target` | `at`, `duration`, `color` | Draw a circle around one object. |
| `draw_border` | `target` | `at`, `duration`, `color` | Draw a rectangular border around one object's bounding box. |
| `recolor` | `target`, `color` | `at`, `duration` | Change the color of one or more objects. |
| `wait` | — | `at`, `duration` | Pause. Default duration 1 s. |
| `arrange` | `target` (array), `layout` | `at`, `duration`, `gap`, `to` | Lay out several objects in a `row`, `column`, or `grid` (max 24 targets). Default `gap` 0.5 scene units. `to` anchors the group center; by default the group is centered at the mean of the targets' positions. |
| `reveal` | `target` (array) | `at`, `duration`, `interval` | Create targets one after another. Default `interval` 0.75 s. |

### 5.1 Action fields

| Field | Type | Rules |
|---|---|---|
| `action` | string | One of the 15 actions above. |
| `target` | string or string[] | Object id(s) declared in the same scene's `objects`. Required for every action except `wait`. Single-target actions (`move`, `rotate`, `scale`, `indicate`, `circumscribe`, `draw_border`, `recolor`, `transform`, `write`) reject arrays. |
| `at` | number | Start time in seconds from scene start (0–600). If omitted, the action is placed after the previous action ends. |
| `duration` | number | Animation length in seconds (0.1–60). Defaults per action: most actions 1 s, `write` 2 s, `wait` 1 s, `reveal` = interval × count. |
| `into` | string | (`transform` only) A declared-but-not-yet-created object id. |
| `to` | [number, number] | (`move`, `arrange` only) Target scene position. For `arrange`: the group center; omitted → mean of the targets' positions. |
| `degrees` | number | (`rotate` only) −360…360. |
| `factor` | number | (`scale` only) 0.05–20. |
| `style` | string | (`indicate` only) `pulse`, `highlight`, or `underline`. Default `pulse`. |
| `color` | string | (`circumscribe`, `draw_border`, `recolor` only) A palette color (§7). |
| `layout` | string | (`arrange` only) `row`, `column`, or `grid`. |
| `gap` | number | (`arrange` only) 0.1–5 scene units. Default 0.5. |
| `interval` | number | (`reveal` only) 0.1–10 s. Default 0.75. |

Any field not listed for an action is rejected with error category `unsupported_field`. This strictness is deliberate: the prompt templates teach the AI exactly which fields exist, and silent acceptance of invented fields would hide errors until render time.

## 6. Objects

Common object fields:

| Field | Required | Type | Rules |
|---|---|---|---|
| `id` | yes | string | `^[a-z][a-z0-9_-]{0,39}$`, unique within the scene. |
| `kind` | yes | string | One of the 19 kinds below. |
| `params` | no | object | Kind-specific parameters (below). Omitted → documented defaults. |

Two fields that apply to every kind via `params`: `color` (palette name or `#RRGGBB`) and `position` `[x, y]` (scene coordinates, §7.1). Objects declared but never targeted by an action produce a `warning` (not an error) — they are assumed to be `transform` targets or authoring leftovers.

### 6.1 Object kinds and parameters

| Kind | Params (required in **bold**) | Defaults | Notes |
|---|---|---|---|
| `text` | **`content`** (1–200 chars), `font_size` (16–120), `color`, `position` | size 36, color = theme ink, position `[0, 0]` | Plain text label. |
| `formula` | **`content`** (1–200 chars), `renderer` (`auto`/`text`/`latex`), `font_size` (16–96), `color`, `position` | renderer `auto`, size 44 | `auto` uses LaTeX typography when installed, otherwise the plain-text fallback (see [`docs/INSTALLATION.md`](../docs/INSTALLATION.md)). |
| `equation` | **`content`** (1–200 chars, must contain `=`), `font_size` (16–96), `color`, `position` | size 40 | A single equation line; step-by-step solving uses several `equation` objects plus `transform`/`arrange`. |
| `point` | **`position`**, `radius` (0.05–0.5), `color`, `label` (1–12), `label_direction` (`up`/`down`/`left`/`right`) | radius 0.12, color violet, label none, direction `up` | |
| `segment` | **`start`**, **`end`**, `color`, `stroke_width` (1–12), `label` (1–12) | color = theme ink, width 4 | |
| `line` | **`start`**, **`end`**, `color`, `stroke_width`, `label` | color = theme ink, width 3 | Infinite line through the two points, clipped to the frame. |
| `ray` | **`start`**, **`end`**, `color`, `stroke_width`, `label` | color = theme ink, width 3 | |
| `angle` | **`vertex`**, **`start_angle`** (degrees), **`end_angle`** (degrees), `radius` (0.2–2), `color`, `label` (1–12) | radius 0.8, color violet | Angle arc drawn at `vertex` from `start_angle` to `end_angle` (counter-clockwise, degrees). |
| `triangle` | **`vertices`** (exactly 3 `[x, y]`), `labels` (0–3 strings), `color`, `fill_opacity` (0–1), `stroke_width` | fill 0, width 4 | |
| `circle` | **`center`**, **`radius`** (0.1–10), `color`, `fill_opacity`, `stroke_width` | fill 0, width 4 | |
| `polygon` | **`vertices`** (3–12 `[x, y]`), `color`, `fill_opacity`, `stroke_width`, `labels` (0–n strings) | fill 0, width 4 | Closed polygon. |
| `square` | **`origin`** (center), **`side`** (0.1–10), `angle` (degrees), `color`, `fill_opacity`, `stroke_width` | angle 0, fill 0, width 4 | |
| `rectangle` | **`origin`** (center), **`width`** (0.1–12), **`height`** (0.1–12), `angle`, `color`, `fill_opacity`, `stroke_width` | angle 0, fill 0, width 4 | |
| `vector` | **`start`**, **`end`**, `color`, `stroke_width`, `label` | color violet, width 4 | Directed arrow. |
| `axes` | `x_range` (pair, −20…20), `y_range` (pair, −20…20), `grid` (bool), `include_numbers` (bool), `x_label` (1–24), `y_label` (1–24) | x `[-7, 7]`, y `[-4, 4]`, grid false, numbers true | Cartesian axes; the coordinate frame for `function_graph`. |
| `function_graph` | **`expression`** (§7 grammar, 1–120 chars), `domain` (pair), `color`, `stroke_width`, `samples` (20–2000) | domain `[-7, 7]` clipped to the axes range, color violet, width 4, samples 400 | Plotted against the scene's `axes` object; requires an `axes` object in the same scene. |
| `area_fill` | **`expression`**, **`domain`** (pair), `color`, `fill_opacity` (0–1) | color violet, opacity 0.35 | Shaded area between a function and the x-axis over `domain`. Requires `axes`. |
| `number_line` | **`range`** (value pair, −1000…1000), `step` (0.05–100), `markers` (0–12 of `{value, label?, color?}`), `color`, `label` (1–40) | step 1, color = theme ink | Horizontal number line over a range of *values* (not scene coordinates); markers highlight values. |
| `fraction` | **`numerator`** (1–12 chars), **`denominator`** (1–12 chars), `font_size` (16–120), `color`, `position`, `label` (1–40) | size 48, position `[0, 0]` | Stacked fraction with a fraction bar. |

Kinds planned for a later minor version (rejected in v1.0 with a helpful error, never silently ignored): `area_model`, `ratio_diagram`, `inequality_region`, `secant_line`, `tangent_line`, `slider`, `parametric_graph`, `latex_block`, `image`, `voiceover_clip`. See [`docs/ROADMAP.md`](../docs/ROADMAP.md).

## 7. Colors, coordinates, timing, and the math grammar

### 7.1 Coordinate system

Scene units with the origin at the frame center; x grows right, y grows up. Default visible frame for `16:9`: x ∈ [−7, 7], y ∈ [−4, 4]. For `9:16` the frame swaps (x ∈ [−4, 4], y ∈ [−7, 7]); for `1:1`, x and y ∈ [−4.5, 4.5]. Positions outside the frame produce a warning; the renderer clips, it does not rescale.

### 7.2 Colors

A color is either a palette name or a `#RRGGBB` hex literal (case-insensitive). No other format (no `rgb()`, no names outside the palette).

| Name | Hex | Role |
|---|---|---|
| `navy` | `#061830` | Brand ink; background in `ivory` theme. |
| `violet` | `#6A4AEE` | Brand accent; highlights, vectors, graphs. |
| `ivory` | `#F1F3EA` | Light ink; background in `midnight` theme. |
| `white` | `#FFFFFF` | Neutral. |
| `black` | `#000000` | Neutral. |
| `gray` | `#8A93A6` | Secondary ink, grid lines. |
| `red` | `#D0402E` | Errors, corrections, negatives. |
| `green` | `#2E9E6B` | Correct results, positive regions. |
| `blue` | `#2E6FD0` | Secondary graph series. |
| `amber` | `#E0A126` | Warnings, emphasis series. |
| `teal` | `#1F9E9E` | Additional series. |
| `pink` | `#D0509E` | Additional series. |

Theme defaults: `midnight` → background `navy`, ink `ivory`; `ivory` → background `ivory`-white paper, ink `navy`. Explicit `color` params always override theme defaults. Palette source: [`branding/palette.json`](../branding/palette.json).

### 7.3 Timing

All times are seconds from the start of the containing scene. Actions without `at` are auto-sequenced: each starts when the previous action ends. Explicit `at` values that overlap are allowed (independent animations run concurrently). The renderer rejects an `at` + `duration` that exceeds the scene's `duration` by more than 5 s (error `timing_overflow`); a scene with no actions at all is rejected (`empty_scene`).

### 7.4 Math expression grammar

`function_graph.expression`, `area_fill.expression`, and verification `expression` strings may contain only:

- decimal numbers (`42`, `3.5`, `.5`) and the variable `x` (graphs) or assertion variables (`subs` bindings);
- operators `+ - * / **` (also `^` as an alias for `**`), parentheses;
- constants `pi`, `e`;
- functions from this allowlist only: `sin cos tan asin acos atan sqrt abs ln log log10 exp floor ceil round min max`.

Rejected with category `unsafe_expression`: any other identifier, attribute access (`x.__class__`), indexing (`x[0]`), comprehensions, lambdas, imports, assignments, calls to non-allowlisted functions, or any other Python syntax. The validator parses expressions with Python's `ast` module and an allowlist — it never uses `eval`.

## 8. Validation and error reporting

Full rules and error taxonomy: [`prompts/SCENE_VALIDATION_RULES.md`](SCENE_VALIDATION_RULES.md). In summary, an import passes through: file/size check → encoding → front matter split → YAML parse → schema-version check → metadata schema → scene-block schema → reference checks (ids, targets, `transform.into`) → resource limits → expression safety → optional mathematical verification. Errors are structured — category, scene id, field, source line when available, human-readable message, suggested correction — and warnings are reported separately. Unsupported instructions are never silently dropped.

**Rendering is not verification.** A scene that renders successfully has passed *syntax* validation only; `verification` assertions (§3.2), when present, are evaluated separately and reported as passed, failed, or unavailable.

## 9. Versioning and migration

- `schema_version` is `MAJOR.MINOR`.
- **Minor** bumps are backward-compatible additions (new optional fields, new object kinds, new actions). A v1.0 parser must accept files with a lower minor within the same major and ignore nothing — additions are optional by definition.
- **Major** bumps may break compatibility. The application will keep migration adapters for at least the previous major version and will report which migrations were applied on import.
- Unknown `schema_version` values are rejected with category `schema_version`, listing the supported versions.
- This document and the JSON schemas change together; the validator's version output (`--version`) matches the schema version it implements.

## 10. Complete valid example

The canonical worked example is the Pythagorean theorem lesson used in §3–§5 above; the full file is [`prompts/examples/pythagorean-theorem.md`](examples/pythagorean-theorem.md). Eight further examples covering algebra, functions, geometry, trigonometry, calculus, and statistics live in [`prompts/examples/`](examples/). All nine are machine-validated against the JSON schemas by `python tools/validate_scene.py <file>` and that check is part of the documentation consistency routine (see [`docs/TESTING.md`](../docs/TESTING.md)).

## 11. Open questions (require human decisions)

1. **Brand font for rendered text.** The specification does not fix a font family for `text`/`formula` rendering; the planned default is Manim's supported sans-serif plus a safe fallback stack. Decision needed before v1.0 release.
2. **Narration audio.** `narration` is text-only in v1.0; TTS and subtitle export are roadmap items, not commitments.
3. **Cross-scene object persistence.** v1.0 scenes are self-contained (each declares its own objects). A future `carry_over` mechanism is under consideration; it is not part of this version.
