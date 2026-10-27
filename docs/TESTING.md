# Testing MathMotion Studio

> **Status — read first.** The MathMotion Studio application (FastAPI backend, React frontend, Manim renderer, `run.ps1`) **is not yet implemented** ([`ROADMAP.md`](ROADMAP.md)). There is **no automated test suite yet** — no pytest tests, no frontend tests, no CI. What exists and is **Confirmed** today is the scene-format tooling in [`tools/validate_scene.py`](../tools/validate_scene.py): this document's commands and results were actually executed on Windows with Python 3.11.7, PyYAML 6.0.3, and jsonschema 4.26.0. Everything marked **Planned** describes the test suite specified in `MASTER-PROMPT.md` §13 and will only exist once the corresponding code is written. No test counts, coverage percentages, or passing suites are claimed anywhere in this document.

Terminology: **scene.md** — the teacher-importable lesson file; **Scene format** — the restricted declarative format ([`prompts/SCENE_FORMAT_SPEC.md`](../prompts/SCENE_FORMAT_SPEC.md)); **Render job** — an animation-rendering task; **External AI** — the third-party assistant the teacher uses manually.

---

## 1. Current verification (Confirmed)

The only executable verification today is the reference validator. It validates scene.md files against the Scene format v1.0 and both JSON schemas; it is schema tooling, not the application.

### Requirements (Confirmed installed in the verification environment)

| Requirement | Verified version |
|---|---|
| Python | 3.11.7 |
| PyYAML | 6.0.3 |
| jsonschema | 4.26.0 (draft 2020-12) |

```powershell
python --version
python -c "import yaml, jsonschema; print('pyyaml', yaml.__version__); print('jsonschema OK')"
```

If either package is missing, the validator prints `Missing dependency: ... Install with: pip install pyyaml jsonschema` and exits with code `2`.

### Commands (Confirmed working)

```powershell
python tools\validate_scene.py prompts\examples\pythagorean-theorem.md   # human-readable report
python tools\validate_scene.py my-scene.md --json                        # structured JSON report
python tools\validate_scene.py my-scene.md --quiet                       # exit code only, no output
```

### Exit codes

| Exit code | Meaning | Notes |
|---|---|---|
| `0` | Valid — **warnings are allowed** | A scene with warnings (e.g. `out_of_frame`) still passes. |
| `1` | Errors found | Any error category rejects the file. Also (incorrectly, see §7) the code produced by the broken `--version` flag. |
| `2` | Usage or environment error | No file argument, file not found, or missing Python dependencies. |

`--json` overrides `--quiet`: with both flags the JSON report is still printed (Confirmed by inspection of `main()`; behavior is intended for machine consumption).

---

## 2. The documentation consistency routine (Required)

Documentation, prompt templates, the JSON schemas, and the example scenes must describe the same Scene format. As promised in [`tools/README.md`](../tools/README.md), **every example scene in `prompts/examples/` must pass validation with zero errors before documentation changes are committed.**

Run this from the repository root:

```powershell
# Documentation consistency routine — validate every example scene.
# Fails (exit 1) if ANY example scene reports errors. Warnings do not fail the run.
$fail = 0
Get-ChildItem prompts\examples\*.md | Where-Object { $_.Name -ne 'README.md' } | ForEach-Object {
    python tools\validate_scene.py $_.FullName --quiet
    if ($LASTEXITCODE -ne 0) {
        $fail = 1
        Write-Host "FAIL  $($_.Name) (exit $LASTEXITCODE)" -ForegroundColor Red
    } else {
        Write-Host "PASS  $($_.Name)"
    }
}
if ($fail) { Write-Host 'EXAMPLE VALIDATION FAILED'; exit 1 } else { Write-Host 'All example scenes valid.' }
```

CI-style one-liner equivalent:

```powershell
$bad = Get-ChildItem prompts\examples\*.md | Where-Object { $_.Name -ne 'README.md' } | Where-Object { python tools\validate_scene.py $_.FullName --quiet; $LASTEXITCODE -ne 0 }; if ($bad) { Write-Error "Invalid examples: $($bad.Name -join ', ')"; exit 1 }
```

Notes:

- `prompts\examples\README.md` is prose documentation, not a scene file, so it is excluded; a scene validator correctly rejects it with exit code `1` (Confirmed). The routine covers the **nine example scenes** listed in [`prompts/examples/README.md`](../prompts/examples/README.md).
- Exit code `1` from the validator means *errors found*; warnings alone return `0`, so the routine never fails on warnings.
- If the routine fails after you edited an example or the schema, either fix the example or update all three artifacts together — schemas ([`schema/`](../schema/README.md)), spec ([`prompts/SCENE_FORMAT_SPEC.md`](../prompts/SCENE_FORMAT_SPEC.md)), and validator rules ([`prompts/SCENE_VALIDATION_RULES.md`](../prompts/SCENE_VALIDATION_RULES.md)) — and re-run.

**Last executed result (this document's author, verification environment):** all nine example scenes `PASS`, routine exit code `0`. Command output is reproduced in §6.

---

## 3. Planned test commands (Planned — application not yet implemented)

These commands are specified in `MASTER-PROMPT.md` §2, §13, §15 but cannot run today because `backend/`, `frontend/`, and their manifests do not exist yet.

| Command | Purpose | Status |
|---|---|---|
| `pytest backend\tests` | Backend unit and integration tests (pytest + HTTPX) | Planned |
| `ruff check .` / `ruff format .` | Python lint and format (backend, tools) | Planned |
| `npm run test` (frontend) | Frontend component and interaction tests | Planned |
| `npm run lint` | ESLint for the React/TypeScript frontend | Planned |
| `npm run typecheck` (or `tsc --noEmit`) | TypeScript strict-mode checking | Planned |
| End-to-end test run (lightweight scene) | create topic → generate prompt → load example → validate → render → preview/download | Planned |

`tools/validate_scene.py` is Python and would also benefit from Ruff once linting is configured; it is not currently linted by any committed configuration (Confirmed: no lint configuration exists in the repository).

---

## 4. Planned test plan (Planned, from `MASTER-PROMPT.md` §13)

All rows are **Planned**; none of these tests exist today.

| Layer | Scope | Key cases | Status |
|---|---|---|---|
| Backend — parsing & validation | Scene format intake | valid scene parsing; invalid front matter; missing required metadata; unsupported schema versions; unsupported actions; malformed expressions; invalid geometry parameters; oversized files; malicious path values | Planned |
| Backend — services | API behavior | prompt generation; database persistence; Render job lifecycle; cancellation and failure handling; API error responses | Planned |
| Rendering | Manim pipeline | minimal text scene renders; basic geometry scene renders; Pythagorean example renders; graph scene renders; invalid scenes rejected **before** compilation; render failure reported correctly; output files verified (exist, non-empty, readable) before job completion | Planned |
| Frontend | React UI | form validation; prompt generation and copying; clipboard-failure fallback; Markdown upload; scene validation feedback; Render job status display; error and empty states; accessible keyboard navigation | Planned |
| End-to-end | Full workflow | create topic → generate prompt → load example scene → validate → render → preview/download, using a lightweight scene so tests do not depend on optional LaTeX | Planned |

Rules that apply when the suite is built (Planned, `MASTER-PROMPT.md` §13): never claim tests passed without running them; do not make all tests depend on optional LaTeX installations; run formatting, linting, type checking, and tests where the environment supports them.

---

## 5. Sample-scene regression testing

The nine files in [`prompts/examples/`](../prompts/examples/) are the **regression corpus** for the Scene format. Every schema, validator, or prompt-template change must leave them all passing (§2 routine).

### Current coverage (Confirmed by running the validator; coverage inventory from [`prompts/examples/README.md`](../prompts/examples/README.md))

- 9 example scenes, all passing with **0 errors, 0 warnings** (Confirmed — see §6).
- Actions exercised across the corpus: `create`, `write`, `fade_in`, `fade_out`, `transform`, `move`, `scale`, `indicate`, `circumscribe`, `draw_border`, `recolor`, `wait`, `arrange`, `reveal`.
- **Known coverage gaps (Confirmed by inspection of the corpus):** the `rotate` action is not demonstrated in any example; the `ray`, `polygon`, and `vector` object kinds are not demonstrated. The future backend test suite must cover these explicitly.

### Planned: render regression

Once the trusted renderer exists (Planned), add a render-test checklist: each example scene is rendered once at preview quality, its MP4 output is verified to exist and be non-empty, and the result is recorded. **No MP4 previews exist today and none are claimed** — the renderer is not implemented.

---

## 6. Verification evidence log (actually executed)

Every row below is a real command executed in the repository root during the writing of this document, with its real result. Nothing is simulated.

| # | Command | Result | Exit code |
|---|---|---|---|
| 1 | `python --version` | `Python 3.11.7` | 0 |
| 2 | `python -c "import yaml, jsonschema; ..."` | `pyyaml 6.0.3`, `jsonschema 4.26.0` | 0 |
| 3 | `python tools\validate_scene.py --version` | **Crash:** `NameError: name 'SCENE_VERSION' is not defined` (see §7) | 1 (traceback) |
| 4 | `python tools\validate_scene.py prompts\examples\pythagorean-theorem.md` | `VALID  prompts\examples\pythagorean-theorem.md  (schema 1.0)` — `0 error(s), 0 warning(s)` | 0 |
| 5 | `python tools\validate_scene.py prompts\examples\pythagorean-theorem.md --json` | JSON report: `"errors": []`, `"warnings": []` | 0 |
| 6 | Loop over all `prompts\examples\*.md` with `--quiet` | 9 scene files exit `0`; `README.md` exits `1` (not a scene; expected) | 0 for scenes |
| 7 | Documentation consistency routine (§2 snippet) | `PASS` ×9, `All example scenes valid.` | 0 |
| 8 | `python tools\validate_scene.py --quiet` (no file) | usage message | 2 |
| 9 | `python tools\validate_scene.py does-not-exist.md` | `error: file not found: does-not-exist.md` | 2 |
| 10 | Invalid temp scene with `schema_version: "9.9"` | 1 error, category `schema_version` | 1 |
| 11 | Invalid temp scene (v1.0) containing `expression: "__import__('os').system('calc')"`, unknown color `schmozzy`, `write` on a `circle`, graph without `axes` | 11 errors, 1 warning — the malicious expression rejected **twice** (schema pattern and AST allowlist, category `unsafe_expression`) | 1 |
| 12 | Same scene with unquoted `schema_version: 1.0` | 1 error, `schema_version '1.0' is not supported` (YAML float vs. string — see §7) | 1 |

Representative output of run #11 (abbreviated):

```text
INVALID  <temp>\mms-invalid-scene.md  (schema 1.0)
  [ERROR  ] schema  s1.$.objects.1.params.expression:10
            "__import__('os').system('calc')" does not match '^[A-Za-z0-9_+\-*/^()., \t]+$'
  [ERROR  ] unsafe_expression  s1.-:19
            expression "__import__('os').system('calc')": function 'complex expression' is not in the allowlist (...)
  [ERROR  ] kind_mismatch  s1.-:11
            'write' requires a text, formula, or equation object; 'circle1' is a circle
  11 error(s), 1 warning(s)
```

---

## 7. Known issues in the reference validator (documented, not fixed)

Found while executing the commands in §6. Per project policy these are documented here rather than patched by documentation work; they should be fixed by the tooling owner with a re-run of §2 afterward.

| # | Severity | Issue | Detail |
|---|---|---|---|
| 1 | Bug | `--version` crashes | `tools/validate_scene.py` line 386 prints `SCENE_VERSION`, but the constant is named `SCHEMA_VERSION`. Result: `NameError` traceback and exit code `1`. This contradicts [`tools/README.md`](../tools/README.md), which promises `--version` prints `scene-format 1.0`, and `SCENE_FORMAT_SPEC.md` §9, which ties `--version` output to the implemented schema version. Exit code `1` additionally collides with the documented "errors found" meaning. |
| 2 | UX sharp edge | Unquoted `schema_version: 1.0` | YAML parses `1.0` as a float, which never equals the string `"1.0"`, so the file is rejected with the confusing message `schema_version 1.0 is not supported; this validator implements 1.0`. Quoting (`schema_version: "1.0"`) works. A friendlier hint ("quote the version") would help teachers and External AI tools. |
| 3 | Minor | `--json` ignores `--quiet` | Passing both still emits the JSON report. Harmless, but undocumented. |
| 4 | Minor | Line numbers are best-effort | `find_line()` uses substring matching inside the block source; schema errors may point at a plausible rather than exact line. This is already disclosed in [`prompts/SCENE_VALIDATION_RULES.md`](../prompts/SCENE_VALIDATION_RULES.md) §2 ("best effort in the reference validator; exact in the planned app parser"). |
| 5 | Note | YAML safety vs. resource exhaustion | Parsing uses `yaml.safe_load` (no arbitrary object construction — Confirmed), but a hostile deeply-nested document could still raise an unhandled resource error. The 512 KB file cap bounds the exposure. Relevant to the planned upload pipeline; see [`SECURITY.md`](SECURITY.md) §6. |

---

## 8. Manual end-to-end verification checklist (Planned application)

Today steps 1–9 cannot be executed because the application does not exist. This checklist is the acceptance script once `ROADMAP.md` milestones land (derived from `MASTER-PROMPT.md` §1 and §17). Run it before any release candidate.

1. `.\run.ps1` on a clean Windows 10/11 machine completes setup checks and opens the browser dashboard without administrator privileges.
2. Enter a topic (e.g. "Pythagorean theorem, grade 8"), generate a prompt, copy it, and download it as `.txt`; confirm the prompt preview matches the form inputs and requests only Scene format constructs.
3. Paste the prompt into an External AI of choice; save the response as `scene.md`.
4. Import `scene.md` via drag-and-drop and via paste; confirm file-size validation messages appear for oversized files.
5. Validation report shows structured errors/warnings; deliberately corrupt a field and confirm the error names the category, field, line (when available), and a suggested correction.
6. Rendering is **not** possible until validation succeeds and the teacher explicitly starts the Render job.
7. Start a Render job; verify progress states (`queued → validating → preparing → rendering → postprocessing → completed`), cancellation mid-render, and honest failure reporting (no fabricated percentages).
8. Preview the MP4 in-app; download it; open the output folder; confirm the file is non-empty and playable.
9. Reopen the lesson from history and re-render at a different quality without repeating the AI step.
10. Delete a lesson with confirmation; verify its metadata and files are removed from `data/` and `output/`.
11. Settings: change output directory (validated and persisted), run dependency health checks (Manim, FFmpeg, LaTeX availability).
12. Restart the backend during a Render job; confirm the UI recovers job state without marking an incomplete job as successful.

Manual verification steps that are executable **today**: everything in §1 and §2 of this document, plus the import-side checks in [`SECURITY.md`](SECURITY.md) §2 (feed a hostile scene.md to the validator and confirm rejection).

---

## 9. Related documents

- [`SECURITY.md`](SECURITY.md) — trust boundary and protections enforced by the validator.
- [`PRIVACY.md`](PRIVACY.md) — where validation artifacts and lesson data live.
- [`ROADMAP.md`](ROADMAP.md) — when the planned test suite becomes real.
- [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) — what to do when validation or rendering fails.
- [`../prompts/SCENE_VALIDATION_RULES.md`](../prompts/SCENE_VALIDATION_RULES.md) — full error taxonomy the tests must cover.
