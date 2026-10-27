# MathMotion Studio — User Guide

This guide is written for mathematics teachers with no programming experience. Everything below uses plain language, and every command is shown exactly as you would type it.

> **Where we are today.** The MathMotion Studio application — the dashboard, the **Render job** pipeline, MP4 export — is not released yet ([`ROADMAP.md`](ROADMAP.md)). But the lesson-preparation half of the workflow already works: you can write lesson prompts, have an **External AI** produce a **scene.md** file, and check that file with a small included tool called the *validator*. This guide teaches that real, usable workflow today, and clearly marks what arrives with the application release.

## 1. Six words to know

| Term | Meaning |
|---|---|
| **MathMotion Studio** | The mathematics animation application being built. Its preparation tools are usable now. |
| **scene.md** | The lesson file an External AI writes for you — a readable text file describing your animation, lesson by lesson. |
| **Scene format** | The strict set of rules a `scene.md` file must follow (version 1.0). The validator checks these rules. |
| **Render job** | The future process of turning a valid `scene.md` into a video. Part of the application release. |
| **External AI** | Any AI chat assistant you choose (a web chat, a desktop assistant, or a local model). MathMotion Studio never connects to any AI itself — you copy the prompt in and paste the answer back. |

## 2. What is a scene.md file?

Think of it as a **recipe for your animation**, written in two parts:

1. **Front matter** — the lesson's identity card at the very top of the file, between two `---` lines: title, topic, grade, language, length, learning objectives, optional recap, practice questions, and optional mathematical self-checks.
2. **Scene blocks** — one block per "shot" of the animation. Each block says *what appears* (objects: a triangle, a formula, a graph…), *what happens* (actions: create, write, transform, move…), and *when* (timings in seconds).

The file is **data, never code** — it cannot run programs on your computer. That is a core safety rule of the Scene format (see [SECURITY.md](SECURITY.md)). Here is a real, complete scene, adapted from the included example lesson `prompts\examples\pythagorean-theorem.md`:

````text
---
schema_version: "1.0"
lesson:
  title: The Pythagorean Theorem
  topic: Pythagorean theorem
  grade: "8"
  language: en
  duration_minutes: 5
  aspect_ratio: "16:9"
  theme: midnight
objectives:
  - State the Pythagorean theorem for a right triangle.
  - Check the relationship on a 3-4-5 triangle.
prerequisites:
  - Squaring whole numbers
  - Knowing what a right angle is
---

# The Pythagorean Theorem

```scene
id: s1
title: Opening
type: intro
duration: 12
narration: >-
  Today we meet one of the oldest and most useful rules in mathematics:
  the Pythagorean theorem. It connects the three sides of every right triangle.
objects:
  - id: title
    kind: text
    params:
      content: "The Pythagorean Theorem"
      position: [0, 2]
      font_size: 56
      color: violet
  - id: subtitle
    kind: text
    params:
      content: "Every right triangle tells the same story"
      position: [0, 0.8]
      font_size: 34
actions:
  - { action: create, target: title, at: 0 }
  - { action: create, target: subtitle, at: 2 }
  - { action: indicate, target: title, style: pulse, at: 5, duration: 1.5 }
  - { action: wait, at: 8, duration: 2 }
```
````

Read it as a story: *"At second 0 the title appears; at second 2 the subtitle appears; at second 5 the title pulses for 1.5 seconds; then wait."* The prose paragraph between the front matter and the scene blocks is a note for you, the teacher — it is never shown on screen. Full rules: [`prompts/SCENE_FORMAT_SPEC.md`](../prompts/SCENE_FORMAT_SPEC.md).

## 3. Creating a lesson today — the whole workflow

```text
1. Plan the lesson → 2. Build a prompt → 3. Ask your External AI → 4. Save the answer as scene.md
→ 5. Validate it → 6. Fix errors with the AI (loop) → [application release: render & export video]
```

### Step 1 — Plan the lesson in one minute

Decide four things: the **topic** (e.g. solving linear equations by balancing), the **grade**, the **target length** in minutes, and the **language** for labels and narration. That is all the preparation you need.

### Step 2 — Build your prompt

You have two ready-made prompts in the `prompts` folder:

- **Quick start — [`prompts/SCENE_GENERATION_PROMPT.md`](../prompts/SCENE_GENERATION_PROMPT.md).** Open it, fill in the small `INPUT` block at the top (topic, grade, language, style, duration…), then copy everything inside the fenced prompt box — from `ROLE` down to the final line.
- **Full control — [`prompts/PROMPT_TEMPLATE.md`](../prompts/PROMPT_TEMPLATE.md).** The master template behind the future "Create Animation" page. Use it if you want to control every detail; each `{{PLACEHOLDER}}` is documented in its first table.

### Step 3 — Ask your External AI

Open whichever AI assistant you normally use and paste the whole prompt. The response should be the `scene.md` file itself — nothing else. Two quick health checks before you save it:

1. The very first characters of the reply must be `---` (the opening of the front matter). If you see *"Here is your scene file:"* or a ```markdown fence around everything, reply: **"Output only the file itself — no fence, no commentary."**
2. The reply must end with the closing ``` of the last scene block. If it stops mid-way, reply: **"Continue from where you stopped, output only the missing part."**

More advice for different kinds of AI tools: [`prompts/AI_COMPATIBILITY.md`](../prompts/AI_COMPATIBILITY.md).

### Step 4 — Save the answer as scene.md

1. Create a plain-text file, for example `Documents\MathMotion\linear-equations.scene.md` — any name ending in `.md` works.
2. Paste the AI's answer into it and save. In Notepad, keep the default **UTF-8** encoding — that is correct.
3. Avoid special characters in file names (`: * ? " < > |`).

**Shortcut:** instead of generating a lesson, you can copy any file from [`prompts/examples/`](../prompts/examples/) — nine complete, already-checked lessons (Pythagorean theorem, straight-line graphs, quadratic functions, triangle angles, the unit circle, derivatives, equivalent fractions, area of a circle, the mean of a data set). Copying an example and changing small parts is a gentle way to learn the Scene format.

### Step 5 — Validate the file

Open PowerShell in the project folder (see [INSTALLATION.md](INSTALLATION.md) §3) and run:

```powershell
python tools\validate_scene.py Documents\MathMotion\linear-equations.scene.md
```

Adjust the file path to where you saved your file. A clean result looks like this:

```text
VALID  Documents\MathMotion\linear-equations.scene.md  (schema 1.0)
  0 error(s), 0 warning(s)
```

You can stop here and store the lesson — it is finished as a *file*. (Rendering it into a video comes with the application release.)

### Step 6 — Read errors, and ask the AI to fix them

If the file has mistakes, the validator lists each one with a category, a location, a plain-language message, and a suggestion, for example:

```text
INVALID  my-scene.md  (schema 1.0)
  [ERROR  ] unknown_target  s1.actions[].target:41
            action 'create' targets unknown object 'ghost'
            hint: Declare the object in 'objects' or fix the id.
  [WARNING] out_of_frame  s1.-:32
            position [20, 0] lies outside the 16:9 frame (x -7.0..7.0, y -4.0..4.0); it will be clipped
            hint: Move the object inside the frame or change the aspect ratio.
  1 error(s), 1 warning(s)
```

- **Errors** must be fixed; the file is not valid until none remain.
- **Warnings** are advice; a file with warnings only is still valid.

To fix errors, use the **correction prompt**: open [`prompts/SCENE_CORRECTION_PROMPT.md`](../prompts/SCENE_CORRECTION_PROMPT.md), and give your External AI three things:

1. The **original file** (complete, pasted verbatim),
2. the **validator report** (copy everything from the validator window, verbatim),
3. optionally the relevant rules from the format spec, if the AI struggles.

The AI returns a complete corrected file — save it over the old one and validate again. Repeat until the validator says `VALID`. If the same error survives three rounds, do not keep retrying: start again from the generation prompt and mention the problem explicitly — see the correction prompt's own advice (about five rounds maximum per lesson).

### Step 7 — Render, preview, export (application release)

Turning a valid `scene.md` into a video is the job of the application: you will import the file, start a **Render job**, preview the result, and export an MP4. This is **not yet available** — it arrives with the application release described in [`ROADMAP.md`](ROADMAP.md). Until then, keep your validated `scene.md` files: they are complete lessons, ready for the renderer.

## 4. A full worked example (you can follow along)

1. Topic: *the area of a circle*; grade 7; 4 minutes; English. (Or simply use the included example `prompts\examples\circle-area.md`.)
2. Open [`prompts/SCENE_GENERATION_PROMPT.md`](../prompts/SCENE_GENERATION_PROMPT.md), fill the `INPUT` block: `Topic: area of a circle`, `Grade / class: 7`, `Duration (min): 4`, recap yes, practice yes.
3. Copy the prompt into your External AI; wait for the complete answer.
4. Check the reply starts with `---` and ends with ```; save it as `Documents\MathMotion\circle-area.scene.md`.
5. Validate:
   ```powershell
   python tools\validate_scene.py Documents\MathMotion\circle-area.scene.md
   ```
6. Suppose it reports an error saying an action targets an unknown object `area_label`. Copy the whole error report, open the correction prompt template, paste the file + the report, and send it. Save the corrected file, then validate again.
7. When you see `VALID … 0 error(s)`, your lesson file is complete. Store it safely and look forward to the render release!

## 5. Where your files are stored

Today, wherever you choose — the toolkit never moves, copies, or alters your files; the validator only *reads* them. A tidy habit is one folder per subject or class, e.g. `Documents\MathMotion\Year8\`.

With the application release, lessons and settings will live in the project's `data/` folder and finished videos in `output/` — one folder per lesson ([INSTALLATION.md](INSTALLATION.md) §6). Your original `scene.md` files remain yours to keep and reuse; the planned application stores them locally and never sends them anywhere ([SECURITY.md](SECURITY.md), [`ROADMAP.md`](ROADMAP.md)).

## 6. The planned application at a glance

Coming in the application release — see [`ROADMAP.md`](ROADMAP.md). Based on the build specification, the dashboard will offer:

| Page (planned) | What it will do for you |
|---|---|
| Home | Big **Create New Animation** and **Import scene.md** buttons, your recent lessons, and setup status. |
| Create Animation | A form (topic, grade, language, style, duration, aspect ratio, colors, recap/practice/voiceover options) that assembles the prompt for you — the same job the manual templates do today. |
| Import Scene | Drag-and-drop your `scene.md`, then a review page showing objectives, the scene-by-scene timeline, timings, and the validation report. |
| Animation preview | Watch the video, see real render progress, download the MP4, re-render at another quality. |
| My Animations | Search, filter, and reopen your past lessons; render them again without asking any AI. |
| Rendering Jobs | The status of each render (queued → rendering → completed or failed). |
| Settings | Output folder, default quality and aspect ratio, theme, language, and dependency health checks. |

No terminal work will ever be needed after the first launch, and no AI account, API key, or cloud service will ever be required — the **External AI** stays a tool *you* choose and use yourself.

## 7. Tips for lessons the AI gets right the first time

The more precisely you state these, the fewer validation rounds you will need:

- **One idea per scene**, revealed step by step — not everything at once.
- **Labels ≤ 40 characters**, font size ≥ 24, placed *beside* their objects, never overlapping.
- **Positions inside the frame**: in the default 16:9 picture, x runs −7…7 and y runs −4…4 (origin in the centre). Anything outside is clipped (the validator warns you).
- **Colors** from the fixed palette: navy, violet, ivory, white, black, gray, red, green, blue, amber, teal, pink — or a hex code like `#1E1B4B`. Anything else is an error.
- **Realistic timings**: give the narration room to breathe; the validator flags scenes whose actions do not fit the declared duration.
- **Mathematics you can check**: if the lesson contains a checkable relationship (like 3² + 4² = 5²), ask for a `verification` assertion — it is checked separately from the file format.

## 8. Quick reference

| Task | Command |
|---|---|
| Validate a lesson | `python tools\validate_scene.py your-file.md` |
| Same, as a structured report (for the correction prompt) | `python tools\validate_scene.py your-file.md --json` |
| Check only pass/fail (silent) | `python tools\validate_scene.py your-file.md --quiet` |
| All exit codes | `0` = valid · `1` = errors · `2` = usage/environment problem |

Further reading: format rules in [`prompts/SCENE_FORMAT_SPEC.md`](../prompts/SCENE_FORMAT_SPEC.md), the error catalogue in [`prompts/SCENE_VALIDATION_RULES.md`](../prompts/SCENE_VALIDATION_RULES.md), and fixes for common problems in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
