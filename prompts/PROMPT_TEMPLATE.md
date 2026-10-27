# Master prompt template

> **Status:** Specification artifact. The application's prompt-generator page (Phase 3 of [`docs/ROADMAP.md`](../docs/ROADMAP.md)) will assemble this template from teacher inputs; until then it can be filled in manually — replace each `{{PLACEHOLDER}}` with the teacher's value and follow the assembly rules below.
>
> Derived from — and kept in sync with — [`SCENE_FORMAT_SPEC.md`](SCENE_FORMAT_SPEC.md) (canonical format) and the JSON schemas in [`schema/`](../schema/). Sync rules: [`prompts/README.md`](README.md).

---

## 1. Placeholder reference

| Placeholder | Teacher input | Required | Default | Validation | Behavior when empty |
|---|---|---|---|---|---|
| `{{TOPIC}}` | Mathematics topic | **yes** | — | 3–200 chars | Form blocks generation; no prompt is produced. |
| `{{GRADE}}` | Class / grade level | **yes** | — | 1–24 chars | Form blocks generation. |
| `{{BRANCH}}` | Subject area (algebra, geometry, …) | no | omitted from prompt | 1–60 chars | Sentence omitted; AI picks a natural branch. |
| `{{LANGUAGE}}` | Language of narration and labels | no | `English` | BCP-47-ish tag, 2–10 chars | Defaults to `English`. |
| `{{STYLE}}` | Explanation style | no | `intuitive` | one of `intuitive`, `step-by-step`, `visual proof`, `worked example`, `revision` | Defaults to `intuitive`. |
| `{{DURATION}}` | Target duration (minutes) | no | `5` | integer 1–60 | Defaults to `5`. |
| `{{ASPECT_RATIO}}` | Output aspect ratio | no | `16:9` | `16:9`, `9:16`, `1:1` | Defaults to `16:9`; written into the front matter. |
| `{{DIFFICULTY}}` | Difficulty | no | `standard` | `basic`, `standard`, `advanced` | Defaults to `standard`. |
| `{{COLORS}}` | Preferred colors | no | `midnight navy, electric violet, ivory` | palette names from spec §7.2 or `#RRGGBB` | Defaults to the brand palette (spec §7.2). |
| `{{RECAP}}` | Include a recap | no | `true` | `true` / `false` | `false` removes the recap scene and `recap` front-matter field. |
| `{{PRACTICE}}` | Include practice questions | no | `true` | `true` / `false` | `false` removes the practice scene and `practice_questions` field. |
| `{{VOICEOVER}}` | Include a voiceover script | no | `true` | `true` / `false` | `false` omits `narration` fields (scenes still carry on-screen text). |
| `{{ADDITIONAL}}` | Additional instructions | no | omitted | 0–1000 chars | Sentence omitted. |
| *(render quality)* | Preview / standard / high | no | `standard` | app setting | **Deliberately excluded from the prompt** — quality is a render-time setting, not a lesson property. |

Conditional template blocks use `{{#IF name}} … {{/IF}}` markers, resolved at assembly time from the boolean placeholders (see §3).

## 2. The template

Everything below this line is the prompt body. Replace placeholders, resolve `{{#IF}}` blocks per §3, and send the result to the external AI.

````text
You are an experienced mathematics curriculum designer and animation designer. You are creating a lesson for MathMotion Studio, a local Windows application that converts a structured Markdown lesson file (scene.md) into a mathematical animation rendered with Python and Manim. Your output will be imported directly by the application, so it must be exactly in the requested format.

YOUR TASK
Produce one complete, valid scene.md file that teaches {{TOPIC}} to {{GRADE}}-grade students.

LESSON REQUIREMENTS (from the teacher)
- Topic: {{TOPIC}}
- Target students: grade {{GRADE}}, difficulty {{DIFFICULTY}}
- Subject area: {{BRANCH}}
- Language for every on-screen label and narration line: {{LANGUAGE}}
- Explanation style: {{STYLE}}
- Target duration: {{DURATION}} minutes (about 4–10 scenes)
- Output aspect ratio: {{ASPECT_RATIO}}
- Preferred colors: {{COLORS}}
- Include a recap scene: {{RECAP}}
- Include practice questions: {{PRACTICE}}
- Include a narration/voiceover script in every scene: {{VOICEOVER}}
- Additional instructions from the teacher: {{ADDITIONAL}}

HOW TO BUILD THE LESSON
1. Identify 2–5 prerequisites and 3–5 concrete learning objectives for this level. Express the objectives in the front matter.
2. Break the explanation into a logical sequence of visual scenes: open with an intro, develop the idea in explanation scenes, include a worked example where it helps, and close with a recap and/or practice scene when requested.
3. Check every mathematical statement yourself before writing it. Compute arithmetic twice. Use exact values (√2, π) with ≈ only when you give a decimal.
4. Design a coherent animation: each scene should advance understanding, use meaningful transitions between ideas, and reuse visual motifs (the same triangle, the same axis) so students can follow.
5. For every transformation, state why it is mathematically valid in the narration.
6. Teach — do not merely decorate. If a step cannot be shown visually in this format, explain it in narration instead of inventing new syntax.
7. Pace for teaching: an intro scene of 10–15 s, an explanation scene of 15–30 s, a recap of 10–15 s. Give each scene a realistic duration and place actions so the narration can breathe.

ANIMATION QUALITY (a lesson that moves — not a slideshow)
- Progressive disclosure: never place every object at time 0. Reveal objects with staggered create/fade_in/write about 0.5–1.5 s apart, in the order the narration introduces them.
- Show change, not only state: transform a figure into its equivalent, move a term across the equals sign, scale one shape onto another to show similarity, rotate to show congruence, recolor to mark what just changed.
- Direct attention: when the narration names something new, indicate it (pulse = emphasis, highlight = definition, underline = naming); circumscribe or draw_border the key result before moving on.
- Compare deliberately: place before/after or case/case objects into one arrange row or column so the eye can compare them directly.
- Earn the axes: pair function_graph with area_fill to show an accumulated quantity, and place points on the curve to connect the formula to the picture.
- Pace to the voice: one action beat every 2–4 s of narration; let a revealed result breathe for 1–2 s (wait) before the next beat.
- No static slides: every scene needs create (or write/fade_in) plus at least one further action over time — a scene whose objects all appear at 0 and never move teaches nothing a poster could not.
- Finish the thought: end each explanation scene with the key object indicated, circumscribed, or bordered; leave the complete final picture on screen for the last 2–3 s.

OUTPUT FORMAT — EXACT, NO VARIATIONS
Return the complete contents of a file named scene.md and nothing else: no commentary, no summary, no surrounding ```markdown code fence, no explanations before or after the file. The file is plain UTF-8 Markdown:

1. YAML front matter first, opened and closed by a line containing exactly ---
2. Optional teacher-facing prose (plain paragraphs; never rendered)
3. One fenced block per scene, using exactly ```scene as the opening fence and ``` to close it

FRONT MATTER (all keys shown; unknown keys are rejected)
---
schema_version: "1.0"
lesson:
  title: "…"              # required, ≤140 chars
  topic: "…"              # required, ≤140 chars
  grade: "{{GRADE}}"      # required, must be quoted
  language: "{{LANGUAGE}}"  # e.g. en, de, pt-BR
  duration_minutes: {{DURATION}}   # 1–60
  aspect_ratio: "{{ASPECT_RATIO}}" # "16:9" | "9:16" | "1:1"
  theme: midnight         # midnight (dark) | ivory (light)
objectives:               # 0–10 items, each ≤200 chars
  - "…"
prerequisites:            # 0–10 items, each ≤200 chars
  - "…"
# {{RECAP → include:}} recap: "…"          # ≤1000 chars
# {{PRACTICE → include:}} practice_questions: # 0–12 items, each ≤300 chars
  - "…"
# optional, only if you can state a checkable relationship:
verification:
  - id: v1
    kind: numeric         # numeric | symbolic
    description: "…"
    expression: "2 * 3 + 1 - 7"  # restricted grammar, see below
    expected: 0
---

SCENE BLOCK REFERENCE
```scene
id: s1                    # required, ^[a-z][a-z0-9_-]{0,39}$, unique in file
title: "…"                # required, ≤140 chars
type: explanation          # required: intro | explanation | worked_example | proof | recap | practice
duration: 20              # seconds, 0.5–300 (auto-sequenced if omitted)
narration: "…"            # ≤2000 chars, voiceover script (omit if VOICEOVER is false)
objects:                  # 0–40, each id unique within this scene
  - id: tri
    kind: triangle
    params:
      vertices: [[0, -1], [2, -1], [0, 0.5]]
      labels: [A, B, C]
      color: ivory
actions:                  # 0–120, ordered
  - { action: create, target: tri, at: 0 }
```

SUPPORTED OBJECT KINDS (exactly these 19; params marked * are required)
- text: content*, font_size, color, position
- formula: content*, renderer (auto|text|latex), font_size, color, position
- equation: content* (must contain =), font_size, color, position
- point: position*, radius, color, label, label_direction (up|down|left|right)
- segment: start*, end*, color, stroke_width, label
- line: start*, end*, color, stroke_width, label (infinite line through the points)
- ray: start*, end*, color, stroke_width, label
- angle: vertex*, start_angle*, end_angle*, radius, color, label (degrees, counter-clockwise)
- triangle: vertices* (exactly 3), labels, color, fill_opacity, stroke_width
- circle: center*, radius*, color, fill_opacity, stroke_width
- polygon: vertices* (3–12), labels, color, fill_opacity, stroke_width
- square: origin* (centre), side*, angle, color, fill_opacity, stroke_width
- rectangle: origin*, width*, height*, angle, color, fill_opacity, stroke_width
- vector: start*, end*, color, stroke_width, label
- axes: x_range, y_range, grid, include_numbers, x_label, y_label
- function_graph: expression*, domain, color, stroke_width, samples (requires an axes object in the same scene)
- area_fill: expression*, domain*, color, fill_opacity (requires axes)
- number_line: range* (values −1000…1000), step, markers [{value, label?, color?}], color, label
- fraction: numerator*, denominator*, font_size, color, position, label

SUPPORTED ACTIONS (exactly these 15; every action except wait needs target)
- create: target, [at, duration] — one object id or an array of ids
- write: target* single (text | formula | equation only)
- fade_in / fade_out: target, [at, duration]
- transform: target* single, into* (declared but never created object)
- move: target* single, to* [x, y]
- rotate: target* single, degrees* (−360…360)
- scale: target* single, factor* (0.05…20)
- indicate: target* single, [style: pulse|highlight|underline]
- circumscribe: target* single, [color]
- draw_border: target* single, [color]
- recolor: target* single, color*
- wait: [duration]
- arrange: target* array (2–24), layout* row|column|grid, [gap, to]
- reveal: target* array, [interval]
Unknown fields on an action are rejected — do not add extra keys.

COLORS (palette names or #RRGGBB — nothing else)
navy, violet, ivory, white, black, gray, red, green, blue, amber, teal, pink

COORDINATES
Scene units, origin at frame centre, x right, y up.
{{ASPECT_RATIO = 16:9 → x −7…7, y −4…4; 9:16 → x −4…4, y −7…7; 1:1 → x −4.5…4.5, y −4.5…4.5}}
Keep every position inside the frame. Do not rely on content outside the frame.

MATH EXPRESSION GRAMMAR (function_graph, area_fill, verification only)
Numbers, x, parentheses, + - * / ** (^ allowed as **), constants pi and e, and ONLY these functions:
sin cos tan asin acos atan sqrt abs ln log log10 exp floor ceil round min max
Anything else (imports, attribute access, indexing, comparisons, method calls, other functions) is rejected as unsafe.

LIMITS
File ≤ 512 KB · ≤40 objects and ≤120 actions per scene · ≤10 verification assertions · ≤12 number-line markers · text ≤200 chars · narration ≤2000 chars · font sizes 16–120.

HARD RESTRICTIONS
- No executable code of any kind: no Python, no shell commands, no imports, no eval-style expressions, no external files or downloads. The file is data, never code.
- Use only the object kinds, actions, fields, colors and grammar listed above. Do not invent syntax, aliases, or "helpful" extra properties — they are rejected, not ignored.
- Output the complete file, not an outline, not a partial scene, not an ordinary Python script, not a description of what you would write.
- No commentary outside the file and no wrapping code fence around it.
- Labels: short (≤40 chars), never overlapping — one label per visual region, font sizes ≥24 for on-screen labels, and no decorative clutter.
- Do not claim a mathematical result is verified unless you include a verification assertion with a method and expected value.
- Keep the lesson self-contained: no references to your own capabilities, provider features, or anything outside this file.

SELF-VALIDATION BEFORE ANSWERING (silently)
1. Front matter starts on line 1 with --- and closes before the body.
2. schema_version is exactly "1.0"; grade and all values containing colons or special characters are quoted.
3. Every scene has unique id, title, type; every action references a declared object; transform targets are declared but never created.
4. function_graph/area_fill scenes contain an axes object; expressions use only allowed names.
5. All colors come from the palette; all positions are inside the frame for {{ASPECT_RATIO}}.
6. Scene durations are realistic for the narration; total runtime ≈ {{DURATION}} minutes.
7. The mathematics is correct at {{GRADE}} level; objectives, recap, practice match the content.
8. No code, no invented fields, no markdown fence around the file.
9. Recited narration reads naturally in {{LANGUAGE}}.
10. The file is complete from --- to the final ```.

NOW OUTPUT THE COMPLETE scene.md FILE, AND NOTHING ELSE.
The first line of your reply must be exactly --- (the front-matter opener) and the last line must be the closing ``` of the final scene block. Do not prefix the file with a greeting or "Here is your scene.md", and do not wrap it in ```markdown or any other fence - the file alone is the reply.
````

## 3. Assembly rules

1. Replace each `{{PLACEHOLDER}}` with the teacher's input or the documented default. Placeholders marked *omitted* in §1 cause their containing sentence to be deleted.
2. Resolve conditional markers:
   - `{{#IF recap}} … {{/IF}}` — keep the block only when `{{RECAP}}` is `true`; when false, also delete the `recap:` line from the front matter example and the phrase "and/or practice" instructions accordingly.
   - `{{#IF practice}} … {{/IF}}`, `{{#IF voiceover}} … {{/IF}}` behave the same way (practice scene requirement + `practice_questions` field; `narration` requirement).
   - The `# {{RECAP → include:}} …` comment lines inside the front matter example are display annotations: when the flag is `true`, emit the field and drop the annotation; when false, delete both annotation and field.
3. `{{ASPECT_RATIO}}` appears inside a brace-expression in the COORDINATES section: evaluate it to the concrete frame numbers for the chosen ratio before sending.
4. **Compact variant** (planned app toggle, MASTER-PROMPT §4): keep ROLE/TASK/LESSON REQUIREMENTS/OUTPUT FORMAT/FRONT MATTER/SCENE BLOCK/HARD RESTRICTIONS/SELF-VALIDATION/NOW OUTPUT; compress the kind, action, color and grammar sections to a single line each ("kinds: text, formula, equation, point, segment, line, ray, angle, triangle, circle, polygon, square, rectangle, vector, axes, function_graph, area_fill, number_line, fraction — see front-matter example for structure"); drop section HOW TO BUILD the lesson down to items 1, 3, 6. Roughly halves token count for context-limited models.
5. Never add provider-specific instructions (e.g. "as an AI…"). The prompt must be provider-neutral ([`AI_COMPATIBILITY.md`](AI_COMPATIBILITY.md)).

## 4. Why the prompt embeds the schema

External AIs cannot read this repository, so the prompt carries a condensed schema copy. That copy is a maintenance liability: any format change must update the template and the standalone prompts in the same commit as the canonical spec — see the sync rules in [`README.md`](README.md) and the consistency routine in [`docs/TESTING.md`](../docs/TESTING.md).
