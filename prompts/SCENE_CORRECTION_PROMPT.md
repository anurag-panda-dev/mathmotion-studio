# Scene correction prompt

A reusable prompt for fixing an invalid or failed `scene.md`. Give it three things — the original scene, the validation errors, and the format rules — and it returns the complete corrected file.

> **Status:** Written against scene format v1.0 ([`SCENE_FORMAT_SPEC.md`](SCENE_FORMAT_SPEC.md)). The application's import pipeline will produce the same structured errors the app surfaces ([`SCENE_VALIDATION_RULES.md`](SCENE_VALIDATION_RULES.md)); until then use the reference validator: `python tools\validate_scene.py scene.md --json`.

## How to use

1. Run the validator (or import into the app) and copy **all** errors and warnings.
2. Fill the three placeholders in the template below:
   - `{{ORIGINAL_SCENE}}` — the complete original file.
   - `{{ERROR_REPORT}}` — the validator/app output, pasted verbatim (it already contains categories, locations, messages, and suggestions).
   - `{{FORMAT_RULES}}` — optionally, the relevant rows from [`SCENE_FORMAT_SPEC.md`](SCENE_FORMAT_SPEC.md). If you leave this empty, the AI still has enough instruction to work; paste rules for stubborn cases (they are also condensed in [`SCENE_GENERATION_PROMPT.md`](SCENE_GENERATION_PROMPT.md)).
3. Send it, save the response as `scene.md`, and re-validate. Repeat until the validator exits 0.

---

```text
ROLE
You are the authoring assistant for MathMotion Studio, a local application that converts structured scene.md lesson files into mathematical animations. A scene file you wrote failed validation and must be repaired.

{{ORIGINAL_SCENE}}

{{ERROR_REPORT}}

{{FORMAT_RULES}}

YOUR TASK
Produce the complete corrected scene.md file that passes validation.

RULES
1. Preserve the educational objective, lesson structure, and visual design. Make the **smallest necessary corrections** — do not rewrite scenes that already pass, do not rename ids that are not implicated, do not restyle what works.
2. Fix every error; address warnings only when the fix cannot break anything else. Use each error's `suggestion` field — it is written to be applied directly.
3. Corrections must stay inside the documented format: only listed kinds, actions, fields, colors and the expression grammar. Never fix an error by inventing syntax, and never fix it by deleting the mathematical content that triggered it (e.g. if an expression was rejected, rewrite it using allowed functions — do not remove the computation).
4. If an error reveals an impossible request (an unsupported construct), do not fake it: implement the closest supported alternative and add one Markdown comment in the file, `<!-- note: ... -->`, explaining the substitution for the teacher.
5. Return the entire file from the opening `---` to the final ``` — not a diff, not a fragment, not a description of changes. Add no commentary outside the file and no ```markdown wrapper.
6. Do not claim the scene has been tested, validated, or rendered. You cannot run the application. You may only state that the corrections address the listed errors.
7. Keep the mathematics correct for the stated grade level; re-check any arithmetic you touch.

SELF-CHECK BEFORE ANSWERING (silently)
- Every entry in the error report is addressed; no new unknown fields, ids, or targets were introduced.
- Front matter still starts the file and `schema_version` is unchanged ("1.0").
- All quoted strings still quoted; all positions still inside the frame; expressions still within the grammar.
- Output is the bare, complete file with no fence and no commentary.

NOW OUTPUT THE COMPLETE CORRECTED scene.md FILE, AND NOTHING ELSE.
The first line of your reply must be exactly the `---` that opens the (unchanged) front matter, and the last line must be the closing fence of the final scene block. Do not add commentary, do not summarize the fixes, and do not wrap the file in any fence - output only the corrected file.
```

## What a good correction looks like

- **Input:** error `unknown_target — action 'write' targets unknown object 'caption'`.
- **Good fix:** add the missing `caption` text object to `objects`, or retarget the action to an existing text object — whichever preserves the scene's intent.
- **Bad fixes:** deleting the `write` action and losing the narration line; changing the scene format; claiming "this will now render successfully".

## Loop

```text
scene.md ─► validator ─► errors? ─► this prompt ─► scene.md (corrected) ─┐
                ▲                                                        │
                └────────────────────────────────────────────────────────┘
              exit code 0 → import / render
```

Cap the loop at ~5 rounds per scene: repeated identical failures indicate a format misunderstanding — re-read [`SCENE_FORMAT_SPEC.md`](SCENE_FORMAT_SPEC.md) rather than retrying, or start again from [`SCENE_GENERATION_PROMPT.md`](SCENE_GENERATION_PROMPT.md).
