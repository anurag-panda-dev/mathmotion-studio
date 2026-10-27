# MathMotion Studio — Product Requirements Document

> **Document status:** Baseline PRD derived from [`MASTER-PROMPT.md`](../MASTER-PROMPT.md) (the build specification) and the implemented specification artifacts in the repository.
> **Status snapshot:** 2026-10-27. The "Implemented vs Planned" table in [§13](#13-implemented-vs-planned-status-table) reflects repository contents on this date and is the single source of truth for what exists today.
>
> **Terminology used throughout:** **MathMotion Studio** (the product), **scene.md** (the teacher-importable lesson file), **Scene format** (the restricted declarative format described by the Scene format specification), **Render job** (an animation-rendering task), **External AI** (a third-party AI assistant chosen and used by the teacher, outside the application).

---

## 1. Product vision

MathMotion Studio is a local-first, AI-assisted mathematics animation studio for school teachers. A teacher describes a lesson, obtains a **scene.md** file from an **External AI** using a prompt the application generates, imports it, and receives a Manim-rendered MP4 animation — all without writing a single line of code, without any cloud account, and without any AI API key.

The product sits deliberately at the intersection of three ideas:

1. **AI authoring without AI integration.** The application never talks to an AI service. It generates a precise, schema-grounded prompt; the teacher pastes that prompt into whichever External AI they already have access to. This keeps the application free of API keys, subscriptions, and AI vendor lock-in.
2. **A restricted Scene format instead of executable code.** The External AI never returns runnable Python. It returns a declarative, versioned Markdown file that the application validates strictly and translates into a small set of trusted Manim components. This is the product's core safety and predictability guarantee.
3. **Local-first operation.** After one-time dependency setup, the application runs entirely on the teacher's Windows machine: local FastAPI backend, local storage, local rendering.

## 2. Problem statement

School mathematics teachers want animated explanations — a triangle transforming while its squares are drawn, a derivative appearing as a tangent line, fractions merging into a single visual — but the tooling available today forces a false choice:

- **General-purpose animation tools** (raw Manim, slide editors, video editors) require either programming skills or tedious manual animation work that most teachers do not have time to learn.
- **AI code generation** produces Python scripts for Manim that are fragile, occasionally mathematically wrong, and — critically — require someone to run, debug, and trust arbitrary generated code on a school machine.
- **Existing educational video content** is rarely aligned with a specific curriculum, grade level, language, or the exact example a teacher wants to show in class.

MathMotion Studio closes this gap: teachers describe what they want to teach in ordinary form fields, let an AI do the structural authoring inside a safe, restricted format, and let the application do validation, rendering, and management of the resulting lesson videos. The teacher stays in control; nothing runs as code; nothing leaves the machine except the prompt the teacher themselves chooses to paste into an External AI.

## 3. Target users and personas

The primary user is a **school mathematics teacher with no programming experience**, on a Windows 10/11 school or home machine. Three composite personas represent the target range (archetypes, not claims about specific real users):

### 3.1 Persona 1 — Primary-school teacher (Grades 3–6)

- **Context:** Teaches fractions, basic geometry, and measurement. Uses a school-issued Windows laptop, often shared. Low technical confidence; has never opened a terminal; may not have administrative privileges.
- **Goals:** Produce short, clear visual demonstrations (equivalent fractions, the area of a circle) to show on a classroom projector; reuse last term's videos without redoing the work.
- **Pain points:** Anything requiring installation steps feels risky; cryptic error messages cause abandonment; no budget or approval for paid AI subscriptions mandated by software.
- **Design implications:** Strong defaults for every optional field; plain-language, actionable error messages; a happy path (topic → prompt → scene.md → render) that requires no decisions beyond topic and grade; LaTeX must be optional.

### 3.2 Persona 2 — Secondary-school teacher (Grades 7–12)

- **Context:** Teaches algebra, functions, trigonometry, and introductory calculus. Comfortable with mathematical notation; has heard of Manim but cannot write Python reliably. Uses an External AI regularly for text, less so for structured files.
- **Goals:** Create worked examples, visual proofs (angle sums, the unit circle), and derivative visualizations; fine-tune a lesson by editing the scene.md text directly when the AI output is 90% right.
- **Pain points:** AI output varies between runs and tools; "almost valid" files are hard to debug by hand; animations that are visually attractive but mathematically wrong are worse than useless in class.
- **Design implications:** Precise, located validation errors (field path, source line) that can be pasted back into an External AI for correction; strict rejection of ambiguous instructions rather than silent misinterpretation; a correction-prompt workflow; verification assertions reported separately from render success.

### 3.3 Persona 3 — Head of maths (department lead)

- **Context:** Oversees lesson quality and consistency across a department; manages shared machines and storage; accountable for what software runs on school infrastructure.
- **Goals:** Ensure produced lessons are mathematically sound and stylistically consistent; keep a local library of department lessons; avoid tools that require student data, accounts, or cloud services.
- **Pain points:** Shadow IT and tools that exfiltrate content; unpredictable costs; software that breaks silently when dependencies change.
- **Design implications:** No accounts, no telemetry, no cloud dependencies; dependency diagnostics that identify missing tools before a lesson is due; configurable output directory and storage visibility; a documented, versioned Scene format that makes lessons portable and auditable.

## 4. Core user journeys

### 4.1 Primary journey — topic to classroom video

The end-to-end workflow the product exists to serve (from [`MASTER-PROMPT.md` §1](../MASTER-PROMPT.md)):

1. The teacher opens MathMotion Studio by running `run.ps1`. *(Planned — launcher not yet implemented.)*
2. A browser-based dashboard opens automatically.
3. The teacher enters a mathematics topic, class/grade level, language, explanation level, duration, and animation preferences.
4. The application generates a complete, topic-specific AI prompt (assembled from the canonical master template, which embeds the Scene format schema).
5. The teacher copies the prompt and pastes it into any External AI assistant.
6. The External AI returns a structured Markdown file named `scene.md`.
7. The teacher uploads `scene.md` to MathMotion Studio.
8. The application parses and validates the lesson specification against the Scene format; errors and warnings are shown separately and actionably.
9. The teacher reviews the scene plan (title, objectives, scene-by-scene timeline, formulas, narration, estimated duration) and selects the output quality.
10. The application renders the animation using Python and Manim via a trusted, declarative compiler — never by executing AI-generated code.
11. The teacher previews the result and exports the finished MP4.

Steps 5–6 are performed by the teacher with a third-party tool; the application neither initiates nor observes them. This is a deliberate product boundary, documented honestly: the workflow is local-first, not fully offline.

### 4.2 Correction journey — invalid scene.md to valid scene.md

1. Validation fails on import (or the teacher wants to adjust the lesson).
2. The teacher copies the structured error report (category, field path, line, plain-language message, suggested correction).
3. Using the correction prompt template, the teacher asks the External AI to fix the file, preserving the educational objective and making the smallest necessary corrections.
4. The teacher re-imports; repeat until clean, then render. *(This loop works today manually with `python tools\validate_scene.py`; the in-app import page will reproduce the same rules.)*

### 4.3 Re-use journey — previous lesson to new video

1. The teacher opens "My Animations", searches or filters by topic/grade.
2. They reopen a stored lesson specification, optionally edit the scene.md source, and render again with different quality settings — without repeating the AI generation step. *(Planned.)*

### 4.4 Setup and recovery journey

1. On first run, `run.ps1` checks Python, Node.js/npm, FFmpeg, and optional LaTeX, creates a virtual environment, installs dependencies, starts the backend, and opens the browser.
2. If something is missing, the launcher explains what and how to install it, then exits cleanly — it never leaves broken background processes.
3. The Settings page and `-Diagnostics` mode re-run dependency health checks later. *(Planned.)*

## 5. Functional requirements

Unless a row's status says otherwise, every requirement below is **Planned** — the application (backend, frontend, renderer, launcher) does not exist yet; see [§13](#13-implemented-vs-planned-status-table). The specification artifacts that these requirements will be built against are already **Implemented** and are referenced where relevant.

### FR-1 — AI prompt generator

| ID | Requirement |
|---|---|
| FR-1.1 | Provide a teacher-facing form: **required** topic and class/grade level; **optional** subject branch, narration/explanation language, explanation style (intuitive, step-by-step, visual proof, worked example, revision), target duration, aspect ratio (16:9, 9:16, 1:1), quality, difficulty, preferred colors, include-recap / include-practice-questions / include-voiceover-script toggles, and free-text additional instructions. Sensible defaults for a school teacher. |
| FR-1.2 | Assemble a complete, self-contained prompt from the canonical master template ([`prompts/PROMPT_TEMPLATE.md`](../prompts/PROMPT_TEMPLATE.md) — **Implemented** as a template; in-app assembly is Planned), embedding the actual Scene format schema rather than an invented one. |
| FR-1.3 | The generated prompt must instruct the External AI to: teach at the specified level; identify prerequisites and objectives; design a coherent scene sequence; use only supported Scene format constructs; include timing, narration, and labels; avoid visual clutter; return the complete scene.md file and nothing else; and never claim a mathematical result is verified without a verification assertion. |
| FR-1.4 | Offer prompt actions: live readable preview, Generate Prompt, Copy Prompt (with accessible success notification and a selectable-text fallback if clipboard access fails), Download Prompt as `.txt`, Reset Form. Offer an optional compact prompt variant for context-limited models. |
| FR-1.5 | The application must never pretend to generate an AI response itself. The prompt generator produces instructions for an External AI — nothing more. |

### FR-2 — Scene import and validation

| ID | Requirement |
|---|---|
| FR-2.1 | Import `.md` files via drag-and-drop, file picker, or paste; enforce the file-size limit (512 KB) and UTF-8 encoding; offer an example-scene download. |
| FR-2.2 | Validate every import through the staged pipeline defined in [`prompts/SCENE_VALIDATION_RULES.md`](../prompts/SCENE_VALIDATION_RULES.md) (**Implemented** as rules and in the reference validator, stages 1–9 and 11): file intake → encoding → front-matter split → safe YAML parse → schema-version check → metadata schema → scene-block schema → reference/semantic checks → expression safety → resource limits, plus (Planned, in-app) mathematical verification and layout/compile stages. |
| FR-2.3 | Report structured errors — category, scene id, field path, source line when available, human-readable message, suggested correction — and report warnings separately. Errors and warnings never silently discard an instruction; unsupported constructs are rejected, never guessed at. |
| FR-2.4 | After import, show a scene-review page: lesson title, topic, target grade, learning objectives, scene-by-scene timeline, formulas, narration notes, estimated duration, warnings/unsupported features, and the validation report. Actions: Validate Scene, Edit Source, Re-upload, Render Animation. |
| FR-2.5 | Rendering must never start automatically: validation must succeed and the teacher must explicitly start the Render job. |
| FR-2.6 | The in-app parser must implement exactly the rules of the reference validator ([`tools/validate_scene.py`](../tools/validate_scene.py) — **Implemented**) so prompt templates, examples, and the application agree. |
| FR-2.7 | Support the Scene format versioning contract (MAJOR.MINOR, backward-compatible minors, migration adapters for the previous major version) described in the Scene format specification §9 (**Implemented** as specification). |

### FR-3 — Rendering

| ID | Requirement |
|---|---|
| FR-3.1 | Compile validated scenes through a declarative compiler into trusted Manim components. **The application must never execute arbitrary Python returned by an AI model** — no `eval`, no unrestricted `exec`, no dynamic import of user-supplied modules. The Scene format contains no executable code by design (**Implemented** as a format-level guarantee). |
| FR-3.2 | Provide an extensible animation registry covering the v1.0 vocabulary: 19 object kinds (text, formula, equation, point, segment, line, ray, angle, triangle, circle, polygon, square, rectangle, vector, axes, function_graph, area_fill, number_line, fraction) and 15 actions (create, write, fade_in, fade_out, transform, move, rotate, scale, indicate, circumscribe, draw_border, recolor, wait, arrange, reveal), plus shared layout helpers for positioning, margins, text sizing, colors, and transitions. |
| FR-3.3 | Support render qualities (preview, standard, high), aspect-ratio presets, configurable output directory, cancellation, progress reporting, captured stdout/stderr, per-job logs, timeout handling, temporary-file cleanup, retry after failure, and output-integrity checks (output exists, non-empty, readable). |
| FR-3.4 | Run rendering in a subprocess worker with bounded concurrency; never block the API event loop; persist Render job state so backend restarts cannot mark incomplete jobs as successful. Job lifecycle: queued → validating → preparing → rendering → postprocessing → completed / failed / cancelling → cancelled. |
| FR-3.5 | Show honest progress: an indeterminate indicator where Manim cannot report exact progress — never fabricated percentages. |
| FR-3.6 | Where applicable, validate mathematics with SymPy (symbolic) and NumPy (numeric) against the lesson's optional `verification` assertions, and report verification results **separately** from render success. A successful render means the animation compiled — nothing more. |
| FR-3.7 | Where a scene requires an unsupported operation, explain the limitation clearly and suggest an alternative; never silently approximate. |

### FR-4 — Library and history

| ID | Requirement |
|---|---|
| FR-4.1 | Store lesson metadata and Render job records in SQLite (lesson id, title, topic, grade, language, original Markdown, schema version, creation/last-render timestamps, output paths, render settings, job status, error summary). Keep large video files on the filesystem, never in the database. |
| FR-4.2 | "My Animations" page: search, sort by creation date or title, filter by topic and grade, preview completed animations, reopen a lesson specification, render again, export or delete files (with confirmation). |
| FR-4.3 | Use unique per-job directories and safe filenames; prevent path traversal, arbitrary overwrites, and deletion outside configured application directories. Document backup and cleanup behavior. |

### FR-5 — Settings

| ID | Requirement |
|---|---|
| FR-5.1 | Settings page: output directory (validated and persisted), default render quality, default aspect ratio, theme (light/dark), preferred language, dependency health checks (Manim version, FFmpeg availability, LaTeX availability), storage usage, open logs folder, and repair/setup instructions. |

### FR-6 — Diagnostics

| ID | Requirement |
|---|---|
| FR-6.1 | `run.ps1` performs automated environment checks at launch and supports explicit modes: default launch, `-Setup`, `-Dev`, `-Diagnostics`. It tracks only the processes it started and shuts them down cleanly; it never kills unrelated processes holding the port. |
| FR-6.2 | Expose a health/dependency endpoint and Settings-page dependency status. Missing dependencies produce explicit, installable-fix explanations and a clean exit — not a broken background process. |
| FR-6.3 | Teacher-facing errors are plain language; full stack traces and technical detail live in an expandable diagnostic panel and per-job log files, never in the normal interface. |

## 6. Nonfunctional requirements

| ID | Requirement | Status |
|---|---|---|
| NFR-1 | **Local-first.** Local FastAPI backend, SQLite storage, filesystem media, loopback-only network binding by default; no cloud database, no authentication, no mandatory telemetry. | Planned (app) |
| NFR-2 | **Offline-after-setup honesty.** After dependencies are installed, the application itself runs without network access. The External AI step is, by definition, performed by the teacher with a third-party online tool. Documentation and UI must state this precisely and must never claim the overall workflow is fully offline. | Policy (binding on all docs/UI) |
| NFR-3 | **Security of AI-generated files.** scene.md is untrusted input: safe YAML loading only (no object construction), AST-allowlisted math grammar (never `eval`), upload size limits, path-traversal protection, sandboxed rendering with timeouts, resource caps (≤40 objects and ≤120 actions per scene, ≤10 verification assertions, ≤12 number-line markers), no general-purpose shell or code-execution endpoint, CORS restricted to the local frontend, state-changing operations protected against unintended cross-origin requests. | Rules **Implemented** (validator); enforcement Planned (app) |
| NFR-4 | **Performance.** Render jobs never block the API event loop; bounded render concurrency; the UI stays responsive during rendering; preview quality exists specifically so teachers can iterate cheaply. | Planned |
| NFR-5 | **Accessibility.** WCAG 2.1 AA-oriented contrast in both themes, complete keyboard navigation, visible focus, accessible notifications, no color-only status communication. Details in [§8](#8-accessibility-and-usability-requirements). | Planned (UI) |
| NFR-6 | **Platform.** Windows 10 and Windows 11; PowerShell 5.1 and PowerShell 7 compatibility where practical; no administrator privileges required; no Docker prerequisite. | Planned (launcher) |
| NFR-7 | **Reliability and honesty.** Persisted job state survives backend restarts; output files are verified before a job is marked completed; the UI must never display fabricated statistics, fake successful jobs, or placeholder functionality presented as finished. | Planned (app); standing policy |
| NFR-8 | **Maintainability.** Version-pinned, tested dependencies; typed interfaces; structured logging; the Scene format schema kept independent of React and Manim implementation details so it can outlive either. | Planned; schema independence **Implemented** |

## 7. MVP scope and out-of-scope features

### 7.1 MVP scope

The MVP is the smallest release that lets a teacher complete the primary journey ([§4.1](#41-primary-journey--topic-to-classroom-video)) end to end on Windows, with no fabricated steps. It includes:

- `run.ps1` launcher with environment checks and the four modes (FR-6.1).
- React dashboard, Create Animation form, and prompt generator with copy/download (FR-1.1–FR-1.5), assembled from the already-Implemented master template.
- Import Scene page and the full validation pipeline with structured, actionable errors (FR-2.1–FR-2.5), implementing the already-frozen validation rules.
- Scene-review page, trusted declarative compiler, and Render job pipeline for the complete v1.0 vocabulary (19 object kinds, 15 actions) with all three quality tiers (FR-3.1–FR-3.5).
- Animation preview, MP4 download, "My Animations" library, and re-render (FR-4.1–FR-4.3).
- Settings with dependency diagnostics (FR-5.1, FR-6.2).
- Backend, rendering, and frontend automated tests, including at least one end-to-end path: create topic → generate prompt → load example scene → validate → render → preview/download.

The nine Implemented example scenes ([`prompts/examples/`](../prompts/examples/)) serve as the MVP's acceptance corpus: each must validate, and at least one substantial example (the Pythagorean theorem lesson) must render into a playable MP4.

### 7.2 Explicitly out of scope

The following are **not** part of the MVP and must not appear as if they were planned for it:

- ❌ **Cloud services or sync** — no cloud database, no remote storage, no accounts.
- ❌ **User accounts or authentication** — the application is single-user and local.
- ❌ **Integrated AI or API keys** — no External AI is called by the application; no key, account, or paid subscription is required by MathMotion Studio.
- ❌ **Mobile apps** — desktop/laptop browsers on Windows only.
- ❌ **Docker** — explicitly not a prerequisite.
- ❌ **Telemetry** — no mandatory (or default) usage reporting.
- ❌ **Voiceover audio, TTS, and subtitle export** — `narration` is text-only in Scene format v1.0; audio is a roadmap idea, not a commitment.
- ❌ **Interactive demonstrations, batch rendering, additional rendering backends, macOS/Linux support** — future-expansion ideas from [`MASTER-PROMPT.md` §15](../MASTER-PROMPT.md), deferred until after MVP.
- ❌ **Object kinds beyond v1.0** (area_model, ratio_diagram, inequality_region, secant_line, tangent_line, slider, parametric_graph, latex_block, image, voiceover_clip) — rejected with a helpful error in v1.0, never silently ignored; candidates for a future minor version.

## 8. Accessibility and usability requirements

| ID | Requirement |
|---|---|
| A-1 | **Contrast:** all text and interactive controls target WCAG 2.1 AA contrast ratios in both the light and dark themes; theme choice is a first-class setting. (Compliance is verified at UI-build time; no UI exists yet to test.) |
| A-2 | **Keyboard navigation:** every workflow — form filling, prompt copying, file import, scene review, render monitoring, settings — must be completable with the keyboard alone, with visible focus indicators and logical tab order. |
| A-3 | **Non-color status:** errors, warnings, and success states use icons and text, never color alone. |
| A-4 | **Accessible notifications:** success feedback (e.g., "prompt copied") uses appropriately announced, dismissible notifications; clipboard failure degrades to a selectable text area with manual-copy instructions. |
| A-5 | **Nontechnical error language:** the teacher-facing message explains what is wrong in teaching terms and what to do next; field paths, source lines, and stack traces live in an expandable diagnostic panel. Every error carries a concrete suggestion (per the error taxonomy in [`prompts/SCENE_VALIDATION_RULES.md`](../prompts/SCENE_VALIDATION_RULES.md) — **Implemented** as rules). |
| A-6 | **Sensible defaults and empty states:** every optional input has a documented default; every page has a meaningful empty state and contextual guidance; the home dashboard shows quick-start instructions and dependency status — never fabricated statistics or fake jobs. |
| A-7 | **No terminal after launch:** after the initial `run.ps1`, the teacher never needs to interact with a terminal. |
| A-8 | **Readable output design:** on-screen labels stay short and legible (format-level rules cap label sizes and forbid clutter); the rendered video must be readable on a classroom projector. |

## 9. Constraints

| # | Constraint |
|---|---|
| C-1 | **Platform:** Windows 10/11 with PowerShell; no admin privileges assumed; no Docker. |
| C-2 | **Stack:** React + TypeScript (Vite, Tailwind, accessible component library) frontend; Python 3.11+ / FastAPI / Pydantic v2 backend; Manim Community Edition rendering; SQLite storage — fixed by [`MASTER-PROMPT.md` §2](../MASTER-PROMPT.md). |
| C-3 | **Rendering dependencies:** FFmpeg is required for video processing; LaTeX is optional, and basic lessons must work without it via Manim's text fallback. |
| C-4 | **No AI integration:** the application cannot call any AI; the quality of scene.md content depends on whichever External AI the teacher uses. |
| C-5 | **Scene format strictness:** unknown fields, unknown actions, and unknown object kinds are rejected, not ignored — a deliberate constraint that trades AI-output forgiveness for predictability and teachable error messages. |
| C-6 | **Format stability:** the Scene format v1.0 contract (specification, schemas, validator, prompt templates, examples) is synchronized as one system; changing the format requires updating all parts together ([`prompts/README.md`](../prompts/README.md) sync rules — **Implemented** as process). |

## 10. Risks and mitigations

| # | Risk | Impact | Mitigation |
|---|---|---|---|
| R-1 | **Manim/LaTeX/FFmpeg environment fragility on school machines.** Installations fail, PATHs break, LaTeX is huge and brittle. | Teachers cannot render at all; support burden. | LaTeX stays optional with a plain-text formula fallback; `run.ps1` and Settings run dependency health checks and give install instructions; versions are pinned after compatibility testing; a `-Diagnostics` mode isolates problems. |
| R-2 | **AI output quality variance.** Different External AIs, or the same AI on different days, produce files of varying validity. | Failed imports frustrate teachers; "almost right" files are hard to fix by hand. | The prompt embeds the exact schema plus a self-validation checklist; validation rejects early with located errors; the correction-prompt workflow feeds the structured error report back to the AI; nine worked examples show what good looks like. |
| R-3 | **Format drift between prompt, schema, and app.** The prompt embeds a condensed schema copy because External AIs cannot read the repository. | A change lands in one place only; teachers receive prompts for an outdated format. | Mandatory sync rules ([`prompts/README.md`](../prompts/README.md)); a documentation consistency routine requires every example to pass the validator before changes are committed; the app parser must implement the reference validator's rules exactly (FR-2.6). |
| R-4 | **Mathematically wrong animations that render fine.** A pretty, compiling video with an incorrect derivation is worse than no video. | Educational harm; loss of teacher trust. | Optional `verification` assertions evaluated with SymPy/NumPy and reported separately from render success; the prompt forbids unbacked "verified" claims; the UI never equates "rendered" with "mathematically verified". |
| R-5 | **Long or failed renders on weak school hardware.** | Dead air in class; perceived product failure. | Preview-quality renders for iteration; honest indeterminate progress instead of fake percentages; timeouts, cancellation, retry, and per-job logs; bounded concurrency. |
| R-6 | **Scene format evolution breaks existing lessons.** | Teachers lose prior work. | MAJOR.MINOR versioning with backward-compatible minors and migration adapters for the previous major version; unsupported `schema_version` values are rejected explicitly, never misparsed (Scene format specification §9 — **Implemented** as specification). |
| R-7 | **Threat model of untrusted files.** A hostile scene.md attempts code execution, path traversal, or resource exhaustion. | Compromise of the teacher's machine. | No executable code in the format; safe YAML; AST-allowlisted expressions; resource caps; sandboxed subprocess rendering with timeouts; loopback-only binding; no shell/code endpoint; safe path handling (NFR-3). |

## 11. Assumptions

- Teachers have, or can obtain, a Windows 10/11 machine on which Python 3.11+ and Node.js can be installed without administrator privileges.
- Teachers have independent access to at least one capable External AI assistant; the application neither recommends nor pays for one, and provider-neutrality is a documented requirement ([`prompts/AI_COMPATIBILITY.md`](../prompts/AI_COMPATIBILITY.md)).
- English is the first UI language; lesson content language is per-scene metadata (`lesson.language`) and the renderer does not translate content.
- The nine Implemented example scenes are valid fixtures of the Scene format and double as teacher-facing samples.
- Terminology is fixed: **MathMotion Studio**, **scene.md**, **Scene format**, **Render job**, **External AI**.

## 12. Acceptance criteria

Adapted from [`MASTER-PROMPT.md` §17](../MASTER-PROMPT.md). The project is not complete until all are true. (This repository is not yet under version control; the "status" column is a snapshot as of the date at the top of this document.)

| # | Criterion | Status |
|---|---|---|
| AC-1 | `run.ps1` is present at the repository root. | Planned |
| AC-2 | First-time setup instructions are accurate. | Planned |
| AC-3 | Running the launcher starts the local application and opens the browser. | Planned |
| AC-4 | The teacher can enter a topic and generate a complete AI prompt. | Planned (template Implemented) |
| AC-5 | The prompt can be copied or downloaded. | Planned |
| AC-6 | The teacher can import or paste a valid scene.md. | Planned (validator Implemented) |
| AC-7 | The app validates the file and displays actionable errors. | Planned (error rules Implemented) |
| AC-8 | The app never executes arbitrary AI-generated Python. | Format-level guarantee **Implemented**; app enforcement Planned |
| AC-9 | The trusted compiler can generate actual Manim animations. | Planned |
| AC-10 | At least one substantial example lesson renders into a playable MP4. | Planned (example file Implemented) |
| AC-11 | The teacher can monitor a Render job and see real errors. | Planned |
| AC-12 | The teacher can preview and download the finished video. | Planned |
| AC-13 | Previous lessons and their metadata persist locally. | Planned |
| AC-14 | Dependency diagnostics identify missing tools. | Planned |
| AC-15 | The project includes automated tests and meaningful documentation. | Partially: example-validation consistency routine documented; app test suite Planned |
| AC-16 | No cloud account, API key, backend subscription, or administrator privileges are mandatory. | Design constraint (binding) |
| AC-17 | The UI is usable by a teacher with no programming experience. | Planned (usability requirements in §8) |
| AC-18 | No fake data, nonfunctional buttons, or placeholder implementation presented as finished functionality. | Standing policy |

## 13. Implemented vs Planned status table

**This is the authoritative status summary.** "Implemented" means the artifact exists in this repository today and was verified at the snapshot date; "Planned" means it is specified but not built. Nothing in this table is aspirational — anything not listed as Implemented does not exist yet.

| Area | Component | Status | Evidence / location |
|---|---|---|---|
| **Scene format** | Scene format specification v1.0 (canonical, human-readable) | **Implemented** | [`prompts/SCENE_FORMAT_SPEC.md`](../prompts/SCENE_FORMAT_SPEC.md) |
| **Scene format** | Lesson-metadata JSON Schema (draft 2020-12) | **Implemented** | [`schema/lesson-metadata-v1.schema.json`](../schema/lesson-metadata-v1.schema.json) |
| **Scene format** | Scene-block JSON Schema (draft 2020-12; 19 object kinds, 15 actions) | **Implemented** | [`schema/scene-v1.schema.json`](../schema/scene-v1.schema.json) |
| **Validation** | Reference validator (file intake, encoding, safe YAML, version, both schemas, reference/semantic checks, AST expression safety, resource caps; exit codes 0/1/2) | **Implemented** | [`tools/validate_scene.py`](../tools/validate_scene.py), [`tools/README.md`](../tools/README.md) |
| **Validation** | Validation rules and error taxonomy document | **Implemented** | [`prompts/SCENE_VALIDATION_RULES.md`](../prompts/SCENE_VALIDATION_RULES.md) |
| **Prompt system** | Master prompt template with placeholder reference | **Implemented** (as a template; manual use) | [`prompts/PROMPT_TEMPLATE.md`](../prompts/PROMPT_TEMPLATE.md) |
| **Prompt system** | Standalone scene-generation prompt | **Implemented** | [`prompts/SCENE_GENERATION_PROMPT.md`](../prompts/SCENE_GENERATION_PROMPT.md) |
| **Prompt system** | Standalone scene-correction prompt | **Implemented** | [`prompts/SCENE_CORRECTION_PROMPT.md`](../prompts/SCENE_CORRECTION_PROMPT.md) |
| **Prompt system** | External-AI compatibility guide | **Implemented** | [`prompts/AI_COMPATIBILITY.md`](../prompts/AI_COMPATIBILITY.md) |
| **Examples** | Nine example scenes (algebra, geometry, trigonometry, calculus, arithmetic, statistics) — all pass the reference validator with zero errors (verified 2026-10-27) | **Implemented** | [`prompts/examples/`](../prompts/examples/) |
| **Branding** | Logo PNG assets (light, dark, app icon) and the SVG brand package (logo variants, app icon, favicon, palette, brand guidelines) | **Implemented** | [`assets/`](../assets/), [`branding/`](../branding/) |
| **Launcher** | `run.ps1` / `stop.ps1`, environment checks, `-Setup`/`-Dev`/`-Diagnostics` modes | **Planned** | — |
| **Backend** | FastAPI service, `/api/v1` endpoints, typed models, SQLite persistence | **Planned** | — |
| **Backend** | In-app scene.md Markdown parser and Pydantic models (application half of Scene format validation) | **Planned** | — |
| **Rendering** | Trusted Manim component registry and declarative compiler | **Planned** | — |
| **Rendering** | Render worker, job lifecycle, cancellation, logs, progress, output verification | **Planned** | — |
| **Rendering** | Mathematical verification via SymPy/NumPy (validation stage 10) | **Planned** | — |
| **Frontend** | React shell, dashboard, navigation, themes | **Planned** | — |
| **Frontend** | Create Animation page and in-app prompt generator | **Planned** | — |
| **Frontend** | Import Scene page, scene review, animation preview/player | **Planned** | — |
| **Frontend** | My Animations library, Rendering Jobs page, Settings page, Help page | **Planned** | — |
| **Quality** | Automated backend/rendering/frontend test suites, end-to-end test, security hardening, accessibility pass | **Planned** | — |
| **Docs** | Teacher/developer documentation set: installation, user guide, architecture, tech stack, testing, security, troubleshooting, privacy, UI/UX spec, release checklist (concurrent documentation workstream); data-model doc and root README/CONTRIBUTING/LICENSE still to come | **Partial** | see [ROADMAP.md — Known documentation gaps](ROADMAP.md#known-documentation-gaps) |

Related documents: [ROADMAP.md](ROADMAP.md) (milestone plan and definition of done), [CHANGELOG.md](CHANGELOG.md) (released artifacts).