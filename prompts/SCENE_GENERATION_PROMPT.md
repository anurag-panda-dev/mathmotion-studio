# Scene generation prompt

A complete, standalone prompt for generating a new `scene.md` from a mathematics topic and teaching requirements. **Usage:**

1. Fill in the **INPUT** block with your own words (30 seconds).
2. Copy everything inside the fenced prompt — from `ROLE` to the final line.
3. Paste it into your external AI.
4. Save the response exactly as `scene.md` and validate it: `python tools\validate_scene.py scene.md` (or import it into MathMotion Studio once the app is available).

> **Status:** Written against scene format v1.0 ([`SCENE_FORMAT_SPEC.md`](SCENE_FORMAT_SPEC.md)); the application's prompt-generator page is not yet implemented ([`docs/ROADMAP.md`](../docs/ROADMAP.md)). The schema reference below is a condensed copy of the canonical spec and must be kept in sync with it — sync rules in [`README.md`](README.md).
>
> For app-assembled prompts with teacher form fields, use [`PROMPT_TEMPLATE.md`](PROMPT_TEMPLATE.md). To fix a failed scene, use [`SCENE_CORRECTION_PROMPT.md`](SCENE_CORRECTION_PROMPT.md).

---

```text
INPUT — replace the values before sending
  Topic:            <e.g. solving linear equations by balancing>
  Grade / class:    <e.g. 7>
  Language:         <e.g. English>
  Explanation style:<intuitive | step-by-step | visual proof | worked example | revision>
  Duration (min):   <e.g. 5>
  Aspect ratio:     <16:9 | 9:16 | 1:1>
  Include recap:    <yes | no>
  Include practice: <yes | no>
  Extra instructions:<anything else, or leave empty>

ROLE
You are an experienced mathematics curriculum designer and animation designer creating a lesson for MathMotion Studio, a local Windows application that converts a structured Markdown file (scene.md) into a mathematical animation rendered with Python and Manim. Your output is imported directly by the application and must match the requested format exactly.

OBJECTIVE
Produce one complete, valid scene.md file that teaches the INPUT topic to the INPUT grade level in the INPUT duration, in the INPUT language.

LESSON STRUCTURE
1. List 2–5 prerequisites and 3–5 concrete learning objectives; put them in the front matter.
2. Build a scene sequence: intro (10–15 s) → explanation scenes (15–30 s each) → worked example where one helps → recap and/or practice when requested.
3. Each scene teaches one idea. Number the scenes s1, s2, … in order.

MATHEMATICAL CORRECTNESS
- Verify every computation yourself before writing it; do arithmetic twice, and keep exact forms (√2, π, 3/5) rather than rounded decimals unless you mark ≈ explicitly.
- Narrate why each transformation is valid (e.g. "subtracting 3 from both sides keeps the equality").
- If the lesson contains a checkable relationship, add a front-matter `verification` assertion with a method and expected value. Never claim something is "verified" without such a method.
- Distinguish syntax (the file parses) from mathematics (the statement is true): your checklist below covers the file; the assertion covers the math.

VISUAL AND ANIMATION GUIDANCE
- Reuse visual motifs across scenes (same triangle, same axes) so students can follow continuity.
- Prefer 3–7 objects per scene; reveal them with `reveal` or staggered `create` rather than dumping everything at once.
- Progressive disclosure: never place every object at time 0 — stagger create/fade_in/write about 0.5–1.5 s apart, in the order the narration introduces them.
- Show change, not only state: `transform` a figure into its equivalent, `move` a term across the equals sign, `scale` one shape onto another to show similarity, `rotate` to show congruence, `recolor` to mark what just changed.
- Direct attention: when the narration names something new, `indicate` it (pulse = emphasis, highlight = definition, underline = naming); `circumscribe` or `draw_border` the key result before moving on.
- Compare deliberately: place before/after or case/case objects into one `arrange` row or column so the eye can compare them directly.
- Earn the axes: pair `function_graph` with `area_fill` to show an accumulated quantity, and place points on the curve to connect the formula to the picture.
- Pace to the voice: one action beat every 2–4 s of narration; let a revealed result breathe for 1–2 s (`wait`) before the next beat.
- No static slides: every scene needs `create` (or `write`/`fade_in`) plus at least one further action over time.
- Finish the thought: end each explanation scene with the key object indicated, circumscribed, or bordered; leave the complete final picture on screen for the last 2–3 s.
- Position labels beside their objects, never on top of them; labels ≤40 chars, font sizes ≥24; avoid overlapping text and decorative clutter.
- Give actions sensible `at` timings with pauses for narration; set each scene's `duration` to fit its narration plus ~2 s of breathing room.
- Use color semantically and consistently (one accent per idea); stay inside the palette.
- Teach, do not decorate: if an idea cannot be drawn in this format, explain it in narration instead of inventing syntax.

SCENE FORMAT RESTRICTIONS (v1.0 — the file is data, never code)
- Structure: YAML front matter first (lines `---` … `---`), optional teacher-facing prose, then one fenced block per scene using ```scene … ```.
- Front matter: schema_version "1.0"; lesson {title, topic, grade, language, duration_minutes, aspect_ratio, theme}; objectives; prerequisites; optional recap; optional practice_questions; optional verification. Unknown keys are rejected. Quote any value containing `:`, `#`, or that could parse as a number/boolean (always quote grade). Write `language` as the full language name exactly as given in INPUT (e.g. `English`, `Bengali`) — not a code like `en` — 2-40 characters.
- Scene block: id (`^[a-z][a-z0-9_-]{0,39}$`, unique), title, type (intro | explanation | worked_example | proof | recap | practice), optional duration, optional narration, objects, actions.
- Object kinds — exactly these 19 (* = required param):
  text: content* ; formula: content*, renderer ; equation: content* (contains =) ;
  point: position*, radius, label ; segment: start*, end* ; line: start*, end* ;
  ray: start*, end* ; angle: vertex*, start_angle*, end_angle*, radius, label ;
  triangle: vertices* (3), labels ; circle: center*, radius* ;
  polygon: vertices* (3–12) ; square: origin*, side*, angle ;
  rectangle: origin*, width*, height*, angle ; vector: start*, end* ;
  axes: x_range, y_range, grid, include_numbers, x_label, y_label ;
  function_graph: expression*, domain (requires axes in the same scene) ;
  area_fill: expression*, domain* (requires axes) ;
  number_line: range* (values −1000…1000), step, markers ;
  fraction: numerator*, denominator*.
  Common: id, kind, params{color, position where applicable}.
- Actions — exactly these 15: create, write, fade_in, fade_out, transform (target, into), move (target, to), rotate (target, degrees), scale (target, factor), indicate (style: pulse|highlight|underline), circumscribe, draw_border, recolor (color), wait, arrange (target array, layout row|column|grid), reveal (target array, interval). Every action except wait needs `target`; unknown fields are rejected.
- Colors: navy, violet, ivory, white, black, gray, red, green, blue, amber, teal, pink — or #RRGGBB.
- Coordinates: origin centre, x right, y up. Frame: 16:9 → x −7…7, y −4…4 · 9:16 → x −4…4, y −7…7 · 1:1 → x −4.5…4.5. Keep all positions inside the frame.
- Expression grammar (function_graph / area_fill / verification only): numbers, x, + - * / ** ^ ( ), pi, e, and only: sin cos tan asin acos atan sqrt abs ln log log10 exp floor ceil round min max. No other syntax.
- Limits: file ≤512 KB; ≤40 objects and ≤120 actions per scene; ≤10 verification items; ≤12 markers; text ≤200 chars; narration ≤2000 chars; font sizes 16–120; scene duration 0.5–300 s.
- HARD RESTRICTIONS: no Python, no shell, no imports, no eval-like expressions, no external assets or downloads; no invented kinds, actions, fields, colors or aliases; no commentary outside the file; no ```markdown wrapper around the file; no partial output — always the entire file.

OUTPUT REQUIREMENTS
- The complete scene.md from the opening `---` to the last ``` of the final scene.
- Nothing else: no explanation, no summary, no questions back, no code fence around the file.
- The first line of your reply is exactly --- (the front-matter opener) and the last line is the closing ``` of the final scene block. Do not prefix the file with a greeting or "Here is your scene.md", and do not wrap it in ```markdown or any other fence - the file alone is the reply.

FINAL SELF-VALIDATION CHECKLIST (run silently before answering)
1. File starts with `---` front matter and `schema_version: "1.0"`.
2. Every string that could misparse as YAML is quoted (grade, values containing `:` or `#`).
3. Every scene: unique id, title, type; every action targets a declared object; `transform.into` objects are declared but never created.
4. Graph/area scenes contain `axes`; all expressions use only allowed names; colors are palette names or #RRGGBB; positions are inside the frame for the INPUT aspect ratio.
5. Durations and `at` timings fit each scene's narration; total runtime ≈ INPUT duration.
6. The mathematics is correct for INPUT grade level; objectives/recap/practice match the content; verification assertions (if present) have genuine methods.
7. Labels are readable, uncluttered, non-overlapping; no unsupported instructions anywhere.
8. The response is the bare file — no fence, no commentary.

NOW OUTPUT THE COMPLETE scene.md FILE, AND NOTHING ELSE.
```

---

## After generating

1. Save the response as `scene.md` (UTF-8).
2. Validate: `python tools\validate_scene.py scene.md`.
3. If it fails, copy the validator output plus the original scene into [`SCENE_CORRECTION_PROMPT.md`](SCENE_CORRECTION_PROMPT.md).
4. Common non-app failures are listed in [`AI_COMPATIBILITY.md`](AI_COMPATIBILITY.md) (truncated output, added code fences, YAML quoting).
