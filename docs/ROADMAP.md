# MathMotion Studio — Roadmap

> **Purpose:** This file is the forward plan for MathMotion Studio. It exists (and is linked from [`schema/README.md`](../schema/README.md) and [`tools/README.md`](../tools/README.md)) so those implemented specification artifacts have a real destination for their "not yet implemented — see the roadmap" status notes.
>
> **Status snapshot:** 2026-10-27. Every milestone below is labelled **Complete**, **Partial**, or **Planned** against repository contents on this date. Product context and requirements: [PRD.md](PRD.md). Released artifacts: [CHANGELOG.md](CHANGELOG.md).

## How to read this roadmap

- **Source of phases:** The ten phases below are the implementation sequence defined in [`MASTER-PROMPT.md` §16](../MASTER-PROMPT.md). This roadmap maps each phase to a milestone, adds a status, and states a concrete *definition of done* (DoD).
- **Status meanings:**
  - **Complete** — the deliverable exists in the repository today and works as specified.
  - **Partial** — part of the phase is complete; the remainder is planned. Phase 4 is the only partial phase (see [The Phase 4 split](#the-phase-4-split)).
  - **Planned** — specified but not built. No application code (backend, frontend, renderer, launcher) exists yet.
- **Deliberate re-ordering:** The specification track for the Scene format (the schema/spec portion of Phase 4) was completed *ahead of* Phases 1–3. This was intentional: freezing the Scene format first means the prompt generator, parser, and renderer are all built against one stable, validated contract rather than inventing the format as they go.

## Roadmap overview

| Milestone | Phase ([`MASTER-PROMPT.md` §16](../MASTER-PROMPT.md)) | Scope | Status |
|---|---|---|---|
| **M0 — Scene format specification track** | Phase 4 (schema/spec portion) | Scene format v1.0, JSON schemas, reference validator, prompt templates, example scenes | **Complete** |
| **M1 — Foundation** | Phase 1 | Repository scaffold, environment checks, `run.ps1` launcher, FastAPI health endpoint, React shell | **Planned** |
| **M2 — UI system** | Phase 2 | UI system, dashboard, theme, navigation, Settings shell | **Planned** |
| **M3 — Prompt builder** | Phase 3 | In-app prompt generator (teacher inputs → assembled prompt → copy/download) | **Planned** |
| **M4 — Application parser & import** | Phase 4 (application portion) | In-app Markdown parser, Pydantic models, import pipeline implementing the frozen validation rules | **Planned** |
| **M5 — Trusted compiler** | Phase 5 | Manim component registry and declarative compiler | **Planned** |
| **M6 — Render pipeline** | Phase 6 | Render worker, job lifecycle, cancellation, logs, output management, preview rendering | **Planned** |
| **M7 — Import, preview & library UI** | Phase 7 | Scene import/review UI, animation player, download flow, history | **Planned** |
| **M8 — Persistence & diagnostics** | Phase 8 | SQLite persistence, Settings, dependency diagnostics, recovery behavior | **Planned** |
| **M9 — Hardening & quality** | Phase 9 | Security hardening, comprehensive tests, accessibility, performance | **Planned** |
| **M10 — Release readiness** | Phase 10 | End-to-end verification, clean-install test, final documentation, release checklist | **Planned** |

---

## The Phase 4 split

[`MASTER-PROMPT.md` §16](../MASTER-PROMPT.md) Phase 4 is: *"Versioned scene schema, Markdown parser, documentation, examples, and validation."* This phase has two distinct halves, and only one of them is done.

### ✅ Complete — the schema/specification half (now milestone M0)

Everything a future parser must agree with already exists and is verified:

| Artifact | Location | What it delivers |
|---|---|---|
| Scene format specification v1.0 | [`prompts/SCENE_FORMAT_SPEC.md`](../prompts/SCENE_FORMAT_SPEC.md) | The canonical, versioned, human-readable definition of scene.md (front matter, 19 object kinds, 15 actions, colors, coordinates, timing, math grammar, versioning contract). |
| Lesson-metadata JSON Schema | [`schema/lesson-metadata-v1.schema.json`](../schema/lesson-metadata-v1.schema.json) | Machine-readable validation (draft 2020-12) of the YAML front matter. |
| Scene-block JSON Schema | [`schema/scene-v1.schema.json`](../schema/scene-v1.schema.json) | Machine-readable validation of each ` ```scene ` block. |
| Reference validator | [`tools/validate_scene.py`](../tools/validate_scene.py) | Executable implementation of validation stages 1–9 and 11 (file intake, encoding, safe YAML, version, both schemas, reference/semantic checks, AST expression safety, resource caps). Exit codes 0/1/2. |
| Validation rules & error taxonomy | [`prompts/SCENE_VALIDATION_RULES.md`](../prompts/SCENE_VALIDATION_RULES.md) | What is checked, why a scene is rejected, how errors are reported to teachers. |
| Prompt engineering package | [`prompts/`](../prompts/) | Master template, generation prompt, correction prompt, External-AI compatibility guide. |
| Example corpus | [`prompts/examples/`](../prompts/examples/) | Nine example scenes across algebra, geometry, trigonometry, calculus, arithmetic, and statistics — all pass the reference validator with zero errors (verified 2026-10-27). |

### ⏳ Planned — the application half (now milestone M4)

- An in-app scene.md Markdown parser (front-matter split, safe YAML, body/scene-block extraction).
- Pydantic v2 models mirroring the JSON schemas.
- An import pipeline that implements **exactly** the rules of the reference validator (stages 1–9, 11) plus the two currently-application-only stages: mathematical verification (stage 10) and layout/compile (stage 12). See [`prompts/SCENE_VALIDATION_RULES.md`](../prompts/SCENE_VALIDATION_RULES.md) for the stage-by-stage split.

**Invariant for M4:** the application parser, the reference validator, the JSON schemas, and the prompt templates must always describe and enforce the same format. Any divergence is a bug in the application, not a licence to reinterpret the format. The sync rules in [`prompts/README.md`](../prompts/README.md) govern format changes.

---

## Milestone definitions of done

Each milestone's DoD is a checklist. A milestone is done when every item is verifiably true; the phases end-to-end also carry the standing requirement from [`MASTER-PROMPT.md` §16](../MASTER-PROMPT.md) to *run the relevant tests and fix regressions before continuing*.

### M0 — Scene format specification track · **Complete**

- [x] Scene format v1.0 specified, versioned, and documented as the single source of truth.
- [x] Two JSON Schemas (draft 2020-12) published under [`schema/`](../schema/).
- [x] Reference validator implements stages 1–9 and 11 and is runnable (`python tools\validate_scene.py <file>`).
- [x] Prompt templates (master, generation, correction, compatibility) exist and are consistent with the format.
- [x] Nine example scenes exist; every one passes the validator with zero errors.
- [x] The versioning and migration contract (MAJOR.MINOR, backward-compatible minors, previous-major adapters) is documented.

*Remaining follow-ups owned by this track, not blocking M1:* see [Open questions](#open-questions-requiring-human-decisions).

### M1 — Foundation · **Planned**

- [ ] Repository scaffold matching [`MASTER-PROMPT.md` §11](../MASTER-PROMPT.md) (backend/, frontend/, scripts/, data/, output/), with clear separation of concerns and no empty placeholder modules.
- [ ] Root-level `run.ps1` performs environment checks (Windows/PowerShell, Python, Node/npm, FFmpeg, optional LaTeX), creates the virtual environment, installs dependencies, starts the backend, waits for the health endpoint, and opens the browser.
- [ ] `run.ps1` supports `-Setup`, `-Dev`, and `-Diagnostics` modes; tracks only its own child processes and shuts them down cleanly; never kills unrelated processes on a shared port; needs no admin privileges.
- [ ] FastAPI service exposes a health/dependency endpoint under `/api/v1`.
- [ ] React + TypeScript (Vite) shell builds and renders a placeholder route.

### M2 — UI system · **Planned**

- [ ] Sidebar navigation for Home, Create Animation, Import Scene, My Animations, Rendering Jobs, Settings, Help & Getting Started.
- [ ] Design system per [`MASTER-PROMPT.md` §3](../MASTER-PROMPT.md): light/dark themes, restrained indigo/violet accents on neutral surfaces, accessible contrast, keyboard navigation.
- [ ] Home dashboard with real actions and honest empty states — no fabricated statistics or fake render jobs.
- [ ] Settings page shell (theme, language, and placeholders for the dependency/storage sections completed in M8).

### M3 — Prompt builder · **Planned**

- [ ] Create Animation form with all teacher inputs (required: topic, grade; the documented optionals) and sensible defaults.
- [ ] Prompt generator assembles the master template ([`prompts/PROMPT_TEMPLATE.md`](../prompts/PROMPT_TEMPLATE.md)) from form inputs, embedding the actual Scene format schema, resolving conditional blocks and the compact variant.
- [ ] Live prompt preview; Generate, Copy (with accessible success notice and clipboard-failure fallback), Download as `.txt`, and Reset all work.
- [ ] The page never implies the application itself produced an AI response.
- [ ] Automated tests: form validation, prompt assembly, copy/download, clipboard fallback.

### M4 — Application parser & import · **Planned** *(application half of Phase 4 — see [The Phase 4 split](#the-phase-4-split))*

- [ ] In-app Markdown parser: front-matter split, safe YAML (no object construction), scene-block extraction, encoding and size checks.
- [ ] Pydantic v2 models mirror both JSON schemas; unsupported `schema_version` rejected explicitly.
- [ ] Import pipeline implements stages 1–9 and 11 exactly as the reference validator does; every example in [`prompts/examples/`](../prompts/examples/) imports with zero errors through the app pipeline.
- [ ] Structured errors (category, scene id, field path, line, message, suggestion) and separately reported warnings are exposed through the API.
- [ ] Backend tests cover the invalid cases enumerated in [`MASTER-PROMPT.md` §13](../MASTER-PROMPT.md) (bad front matter, missing metadata, unsupported version, unknown actions, malformed expressions, bad geometry, oversized files, malicious paths).

### M5 — Trusted compiler · **Planned**

- [ ] Declarative compiler maps every validated v1.0 construct (19 object kinds, 15 actions) to a trusted Manim component; **no execution of AI-generated Python, ever** (no `eval`, no unrestricted `exec`, no dynamic import of user modules).
- [ ] Shared layout helpers for positioning, margins, text sizing, color management, and transitions.
- [ ] The registry is extensible — a developer can add a trusted component without rewriting the application.
- [ ] Formula rendering degrades gracefully to a text fallback when LaTeX is absent.
- [ ] Rendering tests: minimal text scene, basic geometry, the Pythagorean theorem example, a graph scene; invalid scenes are rejected *before* compilation.

### M6 — Render pipeline · **Planned**

- [ ] Subprocess-based render worker with bounded concurrency; the API event loop is never blocked.
- [ ] Full job lifecycle (queued → validating → preparing → rendering → postprocessing → completed / failed / cancelling → cancelled) with cancellation, timeouts, retry, and per-job logs.
- [ ] Preview / standard / high quality tiers; aspect-ratio presets; configurable output directory.
- [ ] Honest progress reporting (indeterminate where exact progress is unknowable — never fabricated percentages).
- [ ] Output integrity check (file exists, non-empty, readable) before a job is marked completed; persisted job state survives a backend restart without falsely marking incomplete jobs successful.
- [ ] Mathematical verification (stage 10) via SymPy/NumPy, reported separately from render success.

### M7 — Import, preview & library UI · **Planned**

- [ ] Import Scene page: drag-and-drop, file picker, paste alternative, example download, size validation, clear parse/validation errors.
- [ ] Scene review page with title, topic, grade, objectives, timeline, formulas, narration, estimated duration, warnings, and validation report; Validate / Edit Source / Re-upload / Render actions; rendering gated on successful validation plus explicit teacher action.
- [ ] Animation preview page: video player, status/progress, collapsible diagnostic logs, Download MP4, Download scene.md, open output folder, re-render, delete-with-confirmation.
- [ ] My Animations: search, sort, filter, preview, reopen, re-render, export, delete.
- [ ] Frontend tests for upload, validation feedback, job status, error/empty states, and keyboard navigation.

### M8 — Persistence & diagnostics · **Planned**

- [ ] SQLite stores lesson metadata and render jobs per [`MASTER-PROMPT.md` §12](../MASTER-PROMPT.md); videos stay on the filesystem.
- [ ] Unique per-job directories, safe filenames, path-traversal and arbitrary-overwrite/deletion protection; configurable, validated, persisted output directory.
- [ ] Settings completes dependency health checks (Manim version, FFmpeg, LaTeX), storage usage, open-logs, and repair instructions.
- [ ] Documented backup and cleanup behavior.
- [ ] Reopening and re-rendering a stored lesson requires no repeat of the AI generation step.

### M9 — Hardening & quality · **Planned**

- [ ] Security review of the trust boundary for AI-generated files: upload limits, CORS, loopback-only binding, state-changing request protection, sandboxed rendering, resource caps, no shell/code endpoint.
- [ ] Comprehensive automated test suites (backend, rendering, frontend) plus at least one end-to-end path: create topic → generate prompt → load example scene → validate → render → preview/download.
- [ ] Accessibility pass against the requirements in [PRD.md §8](PRD.md#8-accessibility-and-usability-requirements) (contrast, keyboard navigation, non-color status, accessible notifications, non-technical errors).
- [ ] Performance pass: responsive UI during renders, bounded concurrency, preview-quality iteration loop.

### M10 — Release readiness · **Planned**

- [ ] End-to-end verification of every acceptance criterion in [PRD.md §12](PRD.md#12-acceptance-criteria).
- [ ] Clean-install test on a fresh Windows 10/11 machine following the first-time setup instructions exactly.
- [ ] Final teacher-facing documentation complete and cross-linked (see [Known documentation gaps](#known-documentation-gaps)).
- [ ] Release checklist executed; the first application version is recorded in [CHANGELOG.md](CHANGELOG.md) with a real date.

---

## Near-term next steps

Ordered by dependency. These are the next actions for the application workstream; the specification track (M0) is done and only its open questions (below) remain.

1. **Start M1 (Foundation).** Scaffold the repository structure, write `run.ps1` with environment checks, stand up the FastAPI health endpoint and the React shell. Nothing else can be integration-tested until this exists.
2. **Build M4's parser next to M1–M3, not after M5.** The in-app parser has an executable reference ([`tools/validate_scene.py`](../tools/validate_scene.py)) and a nine-scene fixture corpus — implement and test against both from day one. This finishes Phase 4's application half.
3. **Wire the format-consistency check into development.** The routine documented in [`docs/TESTING.md`](TESTING.md) §2 — *every file in [`prompts/examples/`](../prompts/examples/) must pass with zero errors* — should run as part of the backend test suite so a schema change can never silently break the corpus.
4. **Resolve the open questions below** before M5 (trusted compiler) begins, since they affect rendered output and the format's next minor version.
5. **Keep the sync rule sacred.** Any Scene format change updates specification, schemas, prompt-template schema copy, and examples together ([`prompts/README.md`](../prompts/README.md) sync rules) — and bumps the version per the spec's MAJOR.MINOR contract.

## Open questions (require human decisions)

Carried forward from [`prompts/SCENE_FORMAT_SPEC.md` §11](../prompts/SCENE_FORMAT_SPEC.md). None block M1–M4; all should be closed before M5 renders its first frame.

1. **Brand font for rendered text.** The format does not fix a font family for `text`/`formula` rendering; the planned default is Manim's supported sans-serif plus a safe fallback stack. Decision needed before a v1.0 render ships. (Note: the *logo* no longer depends on this — the wordmark ships as outlined path data in [`branding/`](../branding/); see [`branding/assets-manifest.md`](../branding/assets-manifest.md).)
2. **Narration audio.** `narration` is text-only in Scene format v1.0; TTS and subtitle export are roadmap ideas, not commitments. Decide whether/when to design a minor-version extension.
3. **Cross-scene object persistence.** v1.0 scenes are self-contained (each declares its own objects). A future `carry_over` mechanism is under consideration; it is not part of this version.

## Known documentation gaps

**Closed as of the snapshot date:** every documentation file cross-referenced by the Implemented specification artifacts now exists — [`docs/TESTING.md`](TESTING.md) (documentation-consistency routine), [`docs/INSTALLATION.md`](INSTALLATION.md) (LaTeX/text-fallback setup), and [`branding/palette.json`](../branding/palette.json) (palette source) — along with the broader documentation set produced by the concurrent documentation workstream (`docs/ARCHITECTURE.md`, `docs/TECH_STACK.md`, `docs/USER_GUIDE.md`, `docs/SECURITY.md`, `docs/TROUBLESHOOTING.md`, `docs/PRIVACY.md`, `docs/UI_UX_SPEC.md`, `docs/RELEASE_CHECKLIST.md`, and others). No broken cross-reference links remain from the scene format specification, the JSON schemas, the reference validator, or the prompt templates.

**Still planned as of the snapshot date** (part of M10's final-documentation scope; owned by the documentation workstream, not this roadmap):

- `docs/DATA_MODEL.md` (named in [`DOCS-ASSETS-PROMPT.md` §3](../DOCS-ASSETS-PROMPT.md)).
- A root `README.md` for teachers, plus `CONTRIBUTING.md` and `LICENSE` (per [`MASTER-PROMPT.md` §11 and §14](../MASTER-PROMPT.md)).
- Application-behavior content inside the existing documents (full-app install steps, application test commands, screen descriptions) is marked "Planned" within those files and completes as milestones M1–M10 ship.

## Roadmap change policy

- Statuses in this file are updated when a milestone's DoD items become verifiably true — never before.
- Released artifacts (currently the Scene format and its tooling) are recorded in [CHANGELOG.md](CHANGELOG.md).
- Requirement-level detail lives in [PRD.md](PRD.md); this file tracks sequencing and completion, not restated requirements.