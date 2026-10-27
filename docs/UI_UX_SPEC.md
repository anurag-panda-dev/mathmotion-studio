# MathMotion Studio — UI/UX Specification

> **⚠️ STATUS: Planned application UI — not yet implemented.**
> As of this writing, the MathMotion Studio application (React frontend, FastAPI backend, Manim renderer, `run.ps1`) does **not** exist. The repository currently contains only the Scene format v1.0 specification artifacts (`schema/`), the reference validator (`tools/validate_scene.py`), the prompt system (`prompts/`), and the branding system (`branding/`, [`assets/`](../branding/README.md)). Every screen, component, state, and behavior described in this document is a **plan derived from `MASTER-PROMPT.md` §3** — not a description of shipped functionality. Implementation progress is tracked in [`ROADMAP.md`](ROADMAP.md).
>
> Nothing in this document may be presented to users as an existing feature until it is implemented, tested, and verified per [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md).

**Document purpose:** the single UI/UX reference for building and reviewing the MathMotion Studio interface. It defines every planned screen, the teacher workflow, form defaults and validation, state handling (empty/loading/success/error), and accessibility requirements.

**Sources of truth:**
- Screen inventory, layout, and design direction: `MASTER-PROMPT.md` §3.
- **Color palette and brand values (normative for all UI color decisions):** [`../branding/palette.json`](../branding/palette.json), with usage rules in [`../branding/BRAND_GUIDELINES.md`](../branding/BRAND_GUIDELINES.md). Brand colors are *measured* from the raster references in `assets/` — treat the hex values in `palette.json` as canonical; do not eyedropper from PNGs (export noise varies 4–8 steps).
- Create Animation form defaults and prompt behavior: the implemented prompt template [`../prompts/PROMPT_TEMPLATE.md`](../prompts/PROMPT_TEMPLATE.md).
- Import/scene-review content and limits (file size, themes, scene types): the implemented Scene format v1.0 specification [`../prompts/SCENE_FORMAT_SPEC.md`](../prompts/SCENE_FORMAT_SPEC.md) and [`../schema/README.md`](../schema/README.md).
- Render job lifecycle states: `MASTER-PROMPT.md` §8.

---

## 1. Design direction

MathMotion Studio should feel like a cross between a modern creative studio and a mathematics teaching tool — **not** a generic admin dashboard.

| Aspect | Direction |
|---|---|
| Themes | Neutral **light** and **dark** UI themes; user-selectable in Settings (§3.8). Distinct from, but visually consistent with, the two Scene format *render* themes (`midnight` / `ivory`, §1.1). |
| Surfaces | Light theme: **paper** `#FFFFFF` with **mist** `#F4F6FA` section surfaces. Dark theme: **navy** `#061830` (the identity's midnight navy — not a generic charcoal). |
| Accents | The canonical brand **violet** `#6A4AEE`; used for primary actions, focus, and emphasis — never decoration, and never body text on navy (§1.2). |
| Ink | Light theme body text **navy** `#061830`; dark theme body text **ivory** `#F1F3EA`; secondary text **slate** `#5A6478`. |
| Typography | Clear, legible, mathematics-friendly; readable inline formulas. |
| Spacing | Generous; one primary task per screen region. |
| Borders/shadows | Subtle borders (**line** `#E2E6EF` in light theme) and soft shadows; rounded cards with consistent radii across screens. |
| Motion | Smooth, restrained transitions; never gratuitous. |
| Responsiveness | Optimized for desktop and laptop screens. |

**Explicitly avoided:** excessive gradients, neon effects, childish graphics, unnecessary interface animation, and dense technical dashboards.

**Terminal rule:** after the initial launch via `run.ps1` (see `MASTER-PROMPT.md` §10), the teacher must never need to interact with a terminal. All diagnostics, logs, and repair instructions are surfaced in the UI (Settings → dependency health checks, collapsible log panels).

### 1.1 Color system (design tokens)

All values are the canonical hexes from the normative [`../branding/palette.json`](../branding/palette.json). The `ui_support` block there is explicitly marked *planned — no UI exists yet*; the table below is its binding specification for the future frontend (e.g. as CSS custom properties or Tailwind theme entries). Brand colors are **measured** from the raster references in `assets/` — always take hexes from `palette.json`, never eyedropper the PNGs (the observed samples vary from canonical, e.g. the dark-context violet renders 4–8 steps deeper due to export/compositing).

**Brand trio** (measured):

| Token | Hex | Role in the UI |
|---|---|---|
| `navy` | `#061830` | Primary ink on light surfaces; the full dark-theme surface; app-icon background. |
| `violet` | `#6A4AEE` | The single canonical accent: primary buttons, focus rings, links, active nav item, progress highlights. |
| `ivory` | `#F1F3EA` | Ink on navy surfaces — dark-theme text, tooltips on dark, wordmark ink. |

**UI support colors** (planned; `palette.json` → `ui_support`):

| Token | Hex | Role in the UI |
|---|---|---|
| `paper` | `#FFFFFF` | Light-theme base surface. |
| `mist` | `#F4F6FA` | Light-theme alternate surface (sidebar, section bands, input fills). |
| `line` | `#E2E6EF` | Light-theme borders and dividers. |
| `slate` | `#5A6478` | Secondary/helper text and muted labels. |
| `success` | `#2E9E6B` | Success notifications; valid-field and `completed` job states. |
| `warning` | `#B26A00` | Validation warnings; `degraded` dependency status. |
| `error` | `#C0392B` | Errors, destructive actions, `failed` job states. |

Note that `success` reuses the Scene format green `#2E9E6B`; the UI `warning`/`error` values (`#B26A00` / `#C0392B`) are UI-specific and intentionally differ from the Scene format amber/red (`#E0A126` / `#D0402E`), which govern colors *inside rendered animations* only.

**Scene format palette.** The 12 color names allowed in `scene.md` (`navy`, `violet`, `ivory`, `white`, `black`, `gray`, `red`, `green`, `blue`, `amber`, `teal`, `pink`) are normative for the Scene format ([`../prompts/SCENE_FORMAT_SPEC.md`](../prompts/SCENE_FORMAT_SPEC.md) §7.2), **not** for application chrome. The Create Animation "Preferred colors" field (§3.2) offers exactly these names; app icon, favicon, and logo variants live in `branding/` (usage rules: [`../branding/BRAND_GUIDELINES.md`](../branding/BRAND_GUIDELINES.md)).

**Render themes ≠ UI themes — do not conflate.** The Scene format defines two *render* themes that affect the generated animation (`midnight`: navy background, ivory ink; `ivory`: white background, navy ink — both with violet accent). The application's light/dark *UI* theme is a separate user setting (§3.8). It should share this palette so the app and its animations feel like one product, but switching the UI theme **never** changes a lesson's render theme.

### 1.2 Contrast rules (measured WCAG 2.1 ratios)

Ratios are computed from the canonical hexes in [`../branding/palette.json`](../branding/palette.json) (`contrast_wcag_2_1`) and are binding for implementation:

| Pairing | Ratio | Verdict |
|---|---|---|
| navy on white | **17.7:1** | AAA body text — the default light-theme text pairing. |
| ivory on navy | **15.8:1** | AAA body text — the default dark-theme text pairing. |
| violet on white | **5.5:1** | AA body text; AAA for large text. |
| violet on navy | **3.2:1** | **Large text (≥24px, or ≥18.66px bold) and UI components only — never body text.** |

**Hard usage rules:**

1. Text on navy uses **ivory — never violet** (3.2:1 fails AA for body text).
2. Text on white/paper uses **navy** by default; violet text is allowed only at the large-text thresholds above.
3. Primary buttons: violet fill with an **ivory** label; if a different label color is proposed, re-verify the pairing at the rendered font size before shipping.
4. Status colors (`success`/`warning`/`error`) always pair with a text label or icon — color alone never conveys state (§5).
5. Focus indicators: a violet `#6A4AEE` ring on light surfaces; on navy, ivory or violet — whichever measures ≥3:1 against the adjacent surface at implementation time.

---

## 2. Application shell

### 2.1 Layout

- **Left sidebar** — persistent navigation (see §2.2), collapsible on narrow windows but never hidden by default.
- **Main workspace** — page header (page title + contextual guidance + meaningful status indicators), content area, and contextual empty states. `MASTER-PROMPT.md` §3: "The main workspace should contain a page header, meaningful status indicators, contextual guidance, and useful empty states."

### 2.2 Sidebar navigation

| Item | Route (planned) | Purpose |
|---|---|---|
| **Home** | `/` | Dashboard: start actions, recent work, render status, setup health. |
| **Create Animation** | `/create` | Teacher form → generated External AI prompt. |
| **Import Scene** | `/import` | Upload or paste `scene.md` → scene review. |
| **My Animations** | `/animations` | Search, filter, and manage saved lessons and outputs. |
| **Rendering Jobs** | `/jobs` | Live and historical Render job monitoring. |
| **Settings** | `/settings` | Output directory, defaults, theme, language, diagnostics. |
| **Help & Getting Started** | `/help` | Onboarding, example lessons, troubleshooting entry points. |

### 2.3 Global components and patterns

- **Notifications** — transient success/error messages (e.g. "Prompt copied"). Success notifications announce via an ARIA live region; errors persist until dismissed.
- **Confirmations** — destructive actions (delete lesson, delete output, re-render overwrite) require an explicit confirmation dialog with focus trapped inside and returned to the trigger on close.
- **Status indicators** — dependency/setup health shown as labeled states (available / missing / degraded), never as unexplained colored dots alone.
- **Honest data rule** — all counts, lists, and statuses come from real local data (SQLite + filesystem). **No fabricated statistics, fake render jobs, demo animations, or simulated progress may ever appear in the UI** (`MASTER-PROMPT.md` §3, §17.18).

---

## 3. Screen specifications

Unless noted, every screen below is **planned only**. For each screen: purpose, components, states, validation rules, and accessibility notes.

### 3.1 Home dashboard

**Purpose:** one-glance orientation — what can I do next, and is my setup working?

**Components:**
- Two prominent primary actions: **Create New Animation** (→ Create Animation) and **Import scene.md** (→ Import Scene).
- **Recent animations** — real entries from local lesson history (title, topic, grade, last rendered, status).
- **Recently imported lessons** — real entries from import history.
- **Render job status** — current/queued/failed jobs with honest states from the Render job lifecycle (`MASTER-PROMPT.md` §8).
- **Quick-start instructions** — the short version of the teacher workflow (see §5), linking to Help & Getting Started.
- **Dependency/setup status** — Manim, FFmpeg, LaTeX availability summary (details in Settings).

**States:**
| State | Behavior |
|---|---|
| Empty (first run) | Friendly first-run empty state explaining the two starting actions and pointing to Help & Getting Started. Empty lists show guidance, not zero-styled charts. |
| Loading | Small inline loading indicators while history/status loads. |
| Success | Real data rendered from the local database and job records. |
| Error | Non-technical message ("Could not load your recent lessons") plus an expandable diagnostic section; the start actions remain usable. |

**Validation rules:** none on this screen (no inputs).

**Accessibility:** both primary actions reachable and operable by keyboard in logical order; status conveyed with text labels (not color alone); error details expandable via a labeled disclosure control.

---

### 3.2 Create Animation page

**Purpose:** collect teaching preferences and produce a complete, topic-specific prompt for an External AI. The application **never pretends to generate an AI response itself** — prompt generation is a local template operation.

**Components (form fields):**

| Field | Required | Type / options | Planned default |
|---|---|---|---|
| Topic | **yes** | free text | — |
| Class / grade level | **yes** | free text | — |
| Subject / mathematical branch | no | free text | omitted from prompt |
| Language of narration & explanations | no | language tag | `English` |
| Explanation style | no | `intuitive`, `step-by-step`, `visual proof`, `worked example`, `revision` | `intuitive` |
| Target duration | no | integer, minutes | `5` |
| Output aspect ratio | no | `16:9`, `9:16`, `1:1` | `16:9` |
| Quality | no | `preview`, `standard`, `high` | `standard` (render-time setting; deliberately **not** embedded in the generated prompt) |
| Difficulty | no | `basic`, `standard`, `advanced` | `standard` |
| Preferred colors | no | one of the 12 Scene format color names (`navy`, `violet`, `ivory`, `white`, `black`, `gray`, `red`, `green`, `blue`, `amber`, `teal`, `pink`) or `#RRGGBB`, per [`../branding/palette.json`](../branding/palette.json) → `scene_format` | the brand trio (`navy`, `violet`, `ivory`) |
| Include practice questions | no | toggle | on |
| Include a recap | no | toggle | on |
| Include a voiceover script | no | toggle | on |
| Additional instructions | no | free text, 0–1000 chars | omitted |

Defaults above mirror the implemented prompt template [`../prompts/PROMPT_TEMPLATE.md`](../prompts/PROMPT_TEMPLATE.md); the built form must not diverge from it silently.

Additional components:
- **Live prompt preview** — readable, selectable preview of the generated prompt, updated per the template's placeholder rules.
- Optional **compact prompt** variant for External AI models with limited context (`MASTER-PROMPT.md` §4).
- **Buttons:** **Generate Prompt**, **Copy Prompt**, **Download Prompt as TXT**, **Reset Form**.

**States:**
| State | Behavior |
|---|---|
| Empty | Placeholders and helper text explain each field; Generate Prompt disabled until required fields are valid. |
| Loading | Brief generating state while the prompt is assembled. |
| Success | Prompt shown in preview; copy success produces an accessible success notification. |
| Error | Validation errors adjacent to fields; prompt not generated until resolved. |
| Clipboard failure | Prompt shown in a selectable text area with plain-language instructions for manual copy (`Ctrl+C`); never a dead end. |

**Validation rules (from the implemented template):**
- Topic: required, 3–200 characters; generation is blocked when empty/invalid.
- Grade: required, 1–24 characters; generation blocked when empty/invalid.
- Optional fields follow the template's documented lengths (branch 1–60; language 2–40; additional instructions 0–1000).
- Invalid values are explained in the teacher's words; the form never silently substitutes values.

**Accessibility:** every field has a persistent visible label; errors are associated with their fields and summarized at the top of the form; the prompt preview is a properly labeled region; Copy Prompt uses a real `<button>`; success notification announced via live region; Reset Form requires confirmation if the form is dirty.

---

### 3.3 Import Scene page

**Purpose:** get the External AI's `scene.md` into MathMotion Studio safely and clearly.

**Components:**
- **Drag-and-drop upload** zone and a conventional **file picker** button.
- **Paste Markdown** as a full alternative for teachers who prefer to paste text.
- **Example specification download** (from the bundled example scenes) so a teacher can try the pipeline before using an External AI.
- Size/limit messaging up front.
- Parse/validation error display (see below).

**States:**
| State | Behavior |
|---|---|
| Empty | Drop zone with plain instructions and the example-download link. |
| Loading | Parsing/validation progress indicator. |
| Success | Transition to the scene review page (§3.4). |
| Error | Structured, located errors (see §3.4) with suggested corrections; the teacher can fix the file and re-upload or paste a corrected version. |

**Validation rules:**
- Accepted extension: `.md`. Encoding: UTF-8 (optional BOM).
- **Maximum file size: 512 KB** (Scene format v1.0, [`../prompts/SCENE_FORMAT_SPEC.md`](../prompts/SCENE_FORMAT_SPEC.md) §2) — rejected *before* parsing with a clear message.
- Front matter must be present and first; `schema_version` must be supported (currently `"1.0"`).
- Errors report: category, field or scene identifier, source line when available, human-readable explanation, and a suggested correction (`MASTER-PROMPT.md` §7). Warnings are shown separately from errors and never block silently.

**Accessibility:** drop zone is keyboard-operable (file picker button is the keyboard path; the zone itself exposes the same action); paste area is a labeled `<textarea>`; error summaries use `role="alert"`; no reliance on drag-and-drop alone.

---

### 3.4 Scene review page (post-import)

**Purpose:** let the teacher *understand and approve* the lesson plan before any rendering happens.

**Components:**
- Lesson **title**; **topic and target grade**.
- **Learning objectives** (from front matter).
- **Scene-by-scene timeline** — one entry per `scene` block: id, title, type (`intro`, `explanation`, `worked_example`, `proof`, `recap`, `practice`), duration, key actions.
- **Mathematical formulas** appearing in the lesson.
- **Narration / explanation notes** per scene.
- **Estimated duration** (sum of scene durations vs. `duration_minutes` target).
- **Warnings and unsupported features** — clearly listed; unsupported instructions are never silently discarded (`MASTER-PROMPT.md` §7).
- **Validation report** — errors vs. warnings, each located and explained.

**Actions (exactly four):**
1. **Validate Scene** — (re-)run the validation pipeline.
2. **Edit Source** — open the `scene.md` source in a safe in-app editor for small fixes.
3. **Re-upload** — replace the file entirely.
4. **Render Animation** — start a Render job.

**Hard rule:** **Rendering never starts without successful validation *and* an explicit teacher action.** The Render Animation control is disabled while validation has not succeeded, with an explanatory label ("Run Validate Scene first").

**States:** empty (nothing imported yet → route back to Import Scene), loading (validating), success (validation passed; Render Animation enabled), error (validation failed; Render Animation disabled; errors + suggested corrections listed).

**Accessibility:** timeline is a semantic ordered list; validation results announced via live region ("Validation passed, 0 errors, 2 warnings"); disabled Render Animation is explained in text; the editor is keyboard-accessible with a documented exit.

---

### 3.5 Animation preview page

**Purpose:** watch the finished lesson, judge quality, and export the file.

**Components:**
- **Video player** (native controls: play/pause, seek, volume, fullscreen — keyboard-operable by default).
- **Lesson title and metadata** (topic, grade, language, aspect ratio, quality, render timestamps).
- **Render status and progress** — lifecycle states from `MASTER-PROMPT.md` §8: `queued`, `validating`, `preparing`, `rendering`, `postprocessing`, `completed`, `failed`, `cancelling`, `cancelled`. **Where exact progress cannot be determined from Manim, show an honest indeterminate progress indicator — never fabricated percentages.**
- **Render logs** in a collapsible technical panel (per-job stdout/stderr; not shown expanded by default).
- **Download MP4**, **Download scene.md**, **Open output folder**.
- **Render again** with different quality settings (creates a new Render job; the source lesson is preserved).
- **Delete** lesson or output, gated by confirmation.

**Error handling:** the teacher-facing message is nontechnical ("The animation could not be rendered because a formula could not be typeset"); expandable diagnostic details (job id, log excerpt, error category) are available for developers. Full stack traces are never dumped into the normal interface (`MASTER-PROMPT.md` §8).

**States:** loading (video/poster buffering; job in flight), success (playable video + completed job), error (failed job with honest summary + diagnostics + retry), empty (no output yet → render or navigate back).

**Accessibility:** player reachable and operable by keyboard; status transitions announced politely via live region (completed/failed); log panel is a labeled disclosure; downloads are real links/buttons with accessible names including the lesson title; delete confirmation traps focus.

---

### 3.6 My Animations page

**Purpose:** the teacher's local library of lessons and outputs.

**Components:**
- **Search** (title/topic).
- **Sort** by creation date or title.
- **Filter** by topic and grade.
- Row/card actions: **Preview** completed animations, **Reopen** a lesson specification (back to scene review without re-running the External AI), **Render again**, **Export** files, **Delete** (confirmed).

**States:** empty ("No lessons yet — create your first animation or import a scene.md"), loading (list skeleton), success (real records from SQLite), error (non-technical message + diagnostics).

**Validation rules:** none (read/manage operations only); delete prompts name the exact lesson and what will be removed.

**Accessibility:** search field labeled; sort/filter controls are native form controls; results count announced via live region; card actions keyboard-reachable in reading order.

---

### 3.7 Rendering Jobs page

**Purpose:** monitor everything currently or previously rendering, without blocking the app.

**Components:**
- Job list: lesson title, current lifecycle state, honest progress (or indeterminate indicator), start time, duration.
- Per-job actions: view logs, cancel (`cancelling` → `cancelled`), retry after failure, open output when completed.
- Bounded-concurrency note: multiple queued jobs are normal; the UI reflects queue position honestly.

**States:** empty (no jobs yet), loading, live (jobs update as the worker reports), error (failed jobs listed with summaries and diagnostics).

**Rules:** jobs survive backend restarts — an interrupted job is shown as incomplete/failed-with-reason, **never** silently marked successful (`MASTER-PROMPT.md` §8). A job is only `completed` after the output file exists, is non-empty, and is readable.

**Accessibility:** state changes announced via a polite live region (throttled — not every tick); cancel/retry are real buttons with confirmation where destructive; timestamps have textual labels.

---

### 3.8 Settings page

**Purpose:** configure defaults and keep the local environment healthy.

**Components:**
| Group | Items |
|---|---|
| Output | **Output directory** (validated on change — must be a writable local path — and persisted). |
| Defaults | Default render quality (`preview`/`standard`/`high`), default aspect ratio (`16:9`/`9:16`/`1:1`). |
| Appearance & language | UI theme (light/dark — the surfaces and inks of §1.1; changing it never alters a lesson's render theme, §1.1), preferred language. |
| Dependency health checks | Manim version, FFmpeg availability, LaTeX availability — each with plain-language meaning and impact. |
| Storage | Storage usage summary (outputs/logs/database). |
| Logs | **Open logs folder**. |
| Repair | **Repair/setup instructions** for any missing dependency. |

**States:** loading (checks running), success (persisted values shown), error (unchanged values retained; the failure is explained; nothing is silently reverted).

**Validation:** output-directory change is validated (exists/creatable, writable, not inside the app's protected internals) before persisting; invalid paths show the exact reason. All other changes confirm with a success notification.

**Accessibility:** each control labeled; health check results are text-first; storage figures announced only on explicit request (no chatter); theme change applies immediately and respects `prefers-reduced-motion`.

---

### 3.9 Help & Getting Started page

**Purpose:** make the first successful animation possible without external searching.

**Components:**
- Quick-start walkthrough mirroring the workflow in §5.
- Explanation of the **External AI** model: MathMotion Studio generates the prompt locally; **the teacher copies it into any External AI they choose**; the application sends no lesson content to any AI service and requires no API key, account, cloud service, or subscription (`MASTER-PROMPT.md` §1, §14).
- How to save the AI's answer as `scene.md`.
- Bundled example lessons and how to import them.
- Troubleshooting entry points (validation errors, missing dependencies) linking to [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) and [`USER_GUIDE.md`](USER_GUIDE.md).
- Where data is stored and privacy/security limitations, linking to [`SECURITY.md`](SECURITY.md).

**States:** static content plus live dependency status callouts; all links verified by the documentation link check in [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md).

**Accessibility:** structured headings; numbered steps; every inline help link has meaningful link text; no content conveyed only through imagery.

---

## 4. Teacher workflow narrative

The planned end-to-end journey through the screens:

1. **Launch** — teacher runs `.\run.ps1`; the local service starts and the browser opens the dashboard (no further terminal use).
2. **Home** — the teacher picks **Create New Animation** (or uses Help & Getting Started the first time).
3. **Create Animation** — enters *Topic* and *Class/grade* (required); adjusts language, style, duration, aspect ratio, quality, difficulty, colors, recap/practice/voiceover toggles, or additional instructions as desired (defaults are sensible).
4. **Create Animation** — presses **Generate Prompt**; reviews the live preview; presses **Copy Prompt** (accessible confirmation) — or uses **Download Prompt as TXT** / the manual-copy fallback if the clipboard is unavailable.
5. **External AI** — pastes the prompt into any External AI assistant of their choice; receives a complete `scene.md`; saves it as a plain `.md` file.
6. **Import Scene** — drags the file in (or uses the file picker / paste alternative); size and format limits are checked; parsing and validation run.
7. **Scene review** — reads title, topic, grade, objectives, the scene-by-scene timeline, formulas, narration notes, and estimated duration; reviews warnings, unsupported features, and the validation report; presses **Validate Scene**; optionally **Edit Source** or **Re-upload** to fix issues (corrections can be fed back to the External AI using the correction prompt pattern).
8. **Scene review** — with validation successful, explicitly presses **Render Animation** (rendering never starts otherwise).
9. **Rendering Jobs / preview** — watches honest job states (`queued` → … → `completed`), opens logs only if needed, can cancel.
10. **Animation preview** — plays the MP4, checks the lesson visually, downloads the MP4 or `scene.md`, opens the output folder, or re-renders at a different quality.
11. **My Animations** — later, searches the library, reopens a lesson, re-renders, exports, or deletes with confirmation.
12. **Settings** — adjusts output directory/defaults/theme/language; checks dependency health; follows repair instructions if something is missing.
13. **Help & Getting Started** — returns any time for the walkthrough and troubleshooting links.

---

## 5. Cross-cutting accessibility requirements

These apply to **every** screen above and are release-blocking (see [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md)):

- **Keyboard navigation** — every action is reachable and operable by keyboard in a logical order; no keyboard traps; visible, high-contrast focus indicators on all interactive elements.
- **Focus management** — dialogs trap focus and restore it to the trigger; page transitions move focus to the new page heading.
- **Contrast** — text and essential UI meet WCAG 2.1 AA contrast in **both** light and dark themes, using the measured brand ratios and hard usage rules in §1.2 as the starting point (navy↔white and ivory↔navy pairings already exceed AAA; the violet-on-navy 3.2:1 pairing is restricted to large text and UI components). State is never communicated by color alone.
- **Async status** — validation results, copy success, and Render job state changes are announced through appropriately polite ARIA live regions; continuous progress uses `aria-valuetext` or an indeterminate indicator, not fake percentages.
- **Forms** — persistent visible labels; error text programmatically associated with inputs (`aria-describedby`); an error summary at the top of failed forms.
- **Motion** — respect `prefers-reduced-motion`; the interface contains no animation that is required to understand state.
- **Player** — keyboard-operable native controls; captions/subtitle export is future work (see §7).

---

## 6. Honesty and data rules (release-blocking)

- All displayed history, counts, statuses, and storage figures derive from real local data (SQLite + filesystem). **No fabricated statistics, fake successful render jobs, demo lessons presented as the teacher's own, or placeholder progress values.**
- Buttons are never decorative: every control either performs its labeled action or is visibly disabled with an explanation.
- A successful render means the animation compiled; the UI must not describe a lesson as "mathematically verified" unless verification assertions actually ran and passed (`MASTER-PROMPT.md` §6).
- Error surfaces are honest: real error categories, real job ids, real log excerpts behind the diagnostics disclosure.

---

## 7. Planned improvements / future

> **Not part of the initial release scope.** Tracked in [`ROADMAP.md`](ROADMAP.md); listed here so reviewers can distinguish current plans from future ideas (`MASTER-PROMPT.md` §15).

- Additional geometry and graph components in the animation registry, reflected as new review-page capabilities.
- Interactive mathematical demonstrations.
- Additional narration languages and translation aids.
- Voiceover audio generation and subtitle export, with player controls to match.
- Additional export formats beyond MP4.
- Reusable lesson templates.
- Batch rendering (multiple scenes/lessons in one job queue view).
- Optional External AI provider integration, strictly separated from the core rendering engine and never required.
- Additional rendering backends.
- Refined responsive layouts for smaller laptop/tablet screens (initial release targets desktop/laptop).

---

*Related documents:* [`ROADMAP.md`](ROADMAP.md) · [`USER_GUIDE.md`](USER_GUIDE.md) · [`TESTING.md`](TESTING.md) · [`SECURITY.md`](SECURITY.md) · [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md) · Scene format spec: [`../prompts/SCENE_FORMAT_SPEC.md`](../prompts/SCENE_FORMAT_SPEC.md)
