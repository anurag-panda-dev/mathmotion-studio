# MathMotion Studio — Release Checklist

**Purpose:** the pre-release verification gate for any MathMotion Studio release. Every item must be checked by a real, observed action — never from memory or assumption. Do not mark an item complete unless you ran it; do not claim tests passed without running them (`MASTER-PROMPT.md` §13).

> **Current release scope (as of this writing):** only the **Scene format v1.0 specification artifacts** are implemented and releasable — `schema/` (JSON Schemas), `tools/validate_scene.py` (reference validator), `prompts/` (prompt templates and example scenes), and branding assets. The **application itself (React frontend, FastAPI backend, Manim renderer, `run.ps1`) is not yet implemented**; an application release is therefore pending completion of the implementation phases tracked in [`ROADMAP.md`](ROADMAP.md) (`MASTER-PROMPT.md` §16). Do not invent or commit to release dates or application version numbers.
>
> This checklist is written so that the artifact-release items (§3) can run today and the application items (§4–§9) activate once the corresponding functionality exists. Items that cannot apply to the current scope must be explicitly marked "N/A — not yet implemented", never silently skipped.

---

## 1. Environment and dependency verification

- [ ] Running on a supported Windows 10/11 machine; no administrator privileges required for normal use.
- [ ] **Python 3.11+** detected (verify with `python --version`); matches the version supported by the selected Manim release (`MASTER-PROMPT.md` §2).
- [ ] **Node.js and npm** detected (verify with `node --version`, `npm --version`) — required for the frontend once implemented.
- [ ] Backend Python dependencies install cleanly from the pinned dependency file into a fresh virtual environment.
- [ ] Frontend dependencies install cleanly from the lockfile (`npm ci`-equivalent) once implemented.
- [ ] **FFmpeg** available; version recorded in the release notes dependency section. Missing-FFmpeg behavior degrades gracefully with instructions, not a crash.
- [ ] **LaTeX** treated as *optional*: basic lessons render without it; its absence is reported as a limitation, not a failure.
- [ ] Dependency versions pinned in the dependency files are the versions actually tested (no floating ranges at release time).

## 2. Launcher (`run.ps1`) smoke test

*Applies to the application release; N/A for an artifacts-only release.*

- [ ] `.\run.ps1` from the repository root starts the local service and opens the default browser at the application URL.
- [ ] `.\run.ps1 -Setup`, `.\run.ps1 -Dev`, and `.\run.ps1 -Diagnostics` each run as documented, with documented parameters only.
- [ ] Port check works: an occupied port produces a clear message; the script never kills unrelated processes (`MASTER-PROMPT.md` §10).
- [ ] Missing-dependency path: script explains exactly what to install and exits cleanly, leaving no orphaned background processes.
- [ ] Interrupting the launcher (Ctrl+C) shuts down all child processes cleanly.
- [ ] Works on PowerShell 5.1 and PowerShell 7 where claimed; any divergence is documented.
- [ ] Teacher never needs the terminal again after launch (spot-check: full workflow achievable from the browser UI).

## 3. Scene format artifacts (releasable today)

- [ ] `python tools\validate_scene.py --version` prints `scene-format 1.0`, consistent with [`../schema/README.md`](../schema/README.md) and [`../prompts/SCENE_FORMAT_SPEC.md`](../prompts/SCENE_FORMAT_SPEC.md).
  > ⚠️ **Known issue (observed 2026-10-27):** `--version` currently raises `NameError: name 'SCENE_VERSION' is not defined` in `tools/validate_scene.py` instead of printing the version string. This must be fixed and re-verified before any release that includes the validator. Remove this note once fixed.
- [ ] **All example scenes pass validation with zero errors**, per the documentation consistency routine in [`TESTING.md`](TESTING.md): every scene file under `prompts/examples/` exits `0` from `python tools\validate_scene.py <file> --quiet`.
  - Verified on 2026-10-27 (pre-release evidence, all exit code 0): `circle-area.md`, `derivative-visualization.md`, `fractions-equivalent.md`, `linear-equations.md`, `pythagorean-theorem.md`, `quadratic-functions.md`, `statistics-mean.md`, `triangle-geometry.md`, `trigonometry-unit-circle.md`. Re-run at release time; do not reuse stale results.
- [ ] The three descriptions of the Scene format remain in lockstep: `schema/` JSON Schemas, `prompts/SCENE_FORMAT_SPEC.md`, and `tools/validate_scene.py` (plus the prompt templates) — any format change updated all of them together.
- [ ] Validator exit-code contract intact: `0` valid (warnings allowed), `1` errors found, `2` usage/environment error; `--json` and `--quiet` flags behave as documented in [`../tools/README.md`](../tools/README.md).
- [ ] Safety guarantees hold: no `eval` of scene content; YAML parsed with `yaml.safe_load`; expression checking via `ast` allowlist.

## 4. Test suite (planned — activates with implementation)

*Tracked in [`TESTING.md`](TESTING.md). Until the suites exist, this section is N/A and must be marked as such in release notes.*

- [ ] Backend pytest suite green: parsing (valid/invalid front matter, missing metadata, unsupported schema versions), unsupported actions, malformed expressions, invalid geometry, oversized files, malicious path values, prompt generation, persistence, Render job lifecycle, cancellation/failure, API error responses (`MASTER-PROMPT.md` §13).
- [ ] Rendering tests green: minimal text scene, basic geometry, Pythagorean theorem example, graph scene, rejection before compilation, failure reporting, output verification. Tests do not all depend on optional LaTeX.
- [ ] Frontend tests green: form validation, prompt generation/copy, **clipboard-failure fallback**, Markdown upload, validation feedback, job status display, error/empty states, keyboard navigation.
- [ ] At least one end-to-end test green: create topic → generate prompt → load example scene → validate → render → preview/download.
- [ ] Never claim "tests passed" in release notes without the actual run output attached to the release records.

## 5. Lint, formatting, and type checks (planned)

- [ ] Ruff lint **and** Ruff format clean for the Python codebase (`MASTER-PROMPT.md` §15).
- [ ] ESLint clean for the frontend.
- [ ] TypeScript strict-mode check clean (`tsc --noEmit` equivalent).
- [ ] No newly introduced warnings suppressed to reach green.

## 6. Accessibility pass (planned)

*Against the requirements in [`UI_UX_SPEC.md`](UI_UX_SPEC.md) §5.*

- [ ] Full workflow operable by keyboard alone (create → copy → import → validate → render → preview → download), no traps, visible focus everywhere.
- [ ] Light **and** dark themes meet WCAG 2.1 AA contrast; no state signaled by color alone.
- [ ] Async announcements verified: validation results, copy success, Render job state changes reach a screen-reader/live region.
- [ ] Error forms associate messages with inputs and present a top-of-form summary.
- [ ] `prefers-reduced-motion` respected.

## 7. Security review

- [ ] Security review completed against [`SECURITY.md`](SECURITY.md); its remaining-limitations list is current.
- [ ] Core guarantee intact: the application **never executes arbitrary Python from a `scene.md` file** — declarative parsing to trusted components only; no `eval`/unrestricted `exec`/dynamic user-module imports (`MASTER-PROMPT.md` §6; acceptance criterion 8).
- [ ] Uploaded Markdown is treated as untrusted input; path traversal and arbitrary overwrite protections tested; deletion confined to configured application directories.
- [ ] Service binds to loopback by default; CORS restricted to the local frontend; upload limits enforced; no general-purpose shell/Python execution endpoint exists.
- [ ] State-changing endpoints protected against unintended cross-origin requests.
- [ ] No required cloud account, API key, subscription, or telemetry; the app itself sends no lesson content anywhere.
- [ ] Dependency review: no known-vulnerable pinned versions; [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) updated for this release.

## 8. Documentation and consistency

- [ ] Internal documentation links resolve (README ↔ `docs/*`, including [`ROADMAP.md`](ROADMAP.md), [`USER_GUIDE.md`](USER_GUIDE.md), [`TESTING.md`](TESTING.md), [`SECURITY.md`](SECURITY.md), [`UI_UX_SPEC.md`](UI_UX_SPEC.md), [`CHANGELOG.md`](CHANGELOG.md)).
- [ ] The user guide matches the actual UI at release time; planned-vs-implemented distinctions are accurate (`UI_UX_SPEC.md` status banner still honest).
- [ ] Installation/prerequisite documentation matches the dependencies actually pinned and tested.
- [ ] Screenshot capture checklist from `MASTER-PROMPT.md` §14 completed with **real** screenshots of the released build (never mockups presented as product).
- [ ] [`CHANGELOG.md`](CHANGELOG.md) updated: entries describe actual changes, with no invented dates or version numbers.
- [ ] Version consistency: application version, API version (`/api/v1`), and **Scene format version** agree with their sources; `validate_scene.py --version` prints `scene-format 1.0` (see §3).
- [ ] Terminology pass: **MathMotion Studio**, **scene.md**, **Scene format**, **Render job**, **External AI** used consistently.

## 9. UI honesty audit (planned application)

*Directly encodes acceptance criterion 18 (`MASTER-PROMPT.md` §17).*

- [ ] No fabricated statistics, fake render jobs, demo lessons shown as the teacher's own, or simulated progress anywhere in the UI.
- [ ] No nonfunctional buttons, dead links, or placeholder screens presented as finished functionality.
- [ ] Indeterminate renders show an honest indeterminate indicator — no invented percentages.
- [ ] "Completed" is only shown after the output file exists, is non-empty, and is readable.
- [ ] A lesson is never labeled "mathematically verified" unless its verification assertions actually ran and passed.
- [ ] Error surfaces show real categories/ids/log excerpts behind the diagnostics disclosure; no stack traces in the normal teacher view.

## 10. Release mechanics and post-release

- [ ] Release artifacts assembled from a clean checkout; generated videos, logs, virtual environments, `node_modules/`, and local databases excluded (`.gitignore` audit).
- [ ] Fresh-machine install rehearsal: clone/copy → documented setup → `.\run.ps1` → complete one full lesson workflow.
- [ ] Release notes state: what is implemented, what remains planned, dependency requirements (Python/Node/FFmpeg; LaTeX optional), and honest limitations.
- [ ] Tag/label chosen by the maintainers at release time — this checklist does not assign version numbers or dates.
- [ ] Post-release: verify the documentation links and download instructions from the published location.

---

*Related documents:* [`ROADMAP.md`](ROADMAP.md) · [`TESTING.md`](TESTING.md) · [`SECURITY.md`](SECURITY.md) · [`USER_GUIDE.md`](USER_GUIDE.md) · [`UI_UX_SPEC.md`](UI_UX_SPEC.md) · [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)
