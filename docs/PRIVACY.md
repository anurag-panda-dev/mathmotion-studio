# Privacy — MathMotion Studio

> **Status.** The MathMotion Studio application is **not yet implemented** ([`ROADMAP.md`](ROADMAP.md)). Local storage described here (SQLite, `data/`, `output/`) is **Planned** per `MASTER-PROMPT.md` §2 and §12; the behaviors marked **Confirmed** were verified by inspecting the current repository and running its only tool, [`tools/validate_scene.py`](../tools/validate_scene.py) (a local script that performs no network access and writes nothing). This document makes no legal compliance claims — see §7.

Terminology: **scene.md** — the teacher-importable lesson file; **Render job** — an animation-rendering task; **External AI** — the third-party assistant the teacher uses manually.

---

## 1. Summary

MathMotion Studio is a **local-first** desktop application for Windows. Its design intent:

- **The application itself sends no lesson content anywhere.** There is no cloud backend, no account system, no API key, and no telemetry (planned; the app does not exist yet, so today it sends nothing because it does not run at all).
- Lesson data lives on the teacher's own machine, in files and a local SQLite database the teacher controls.
- The **one exception is entirely manual and outside the application**: the teacher copies the generated prompt into an External AI of their choice and pastes the result back. That third party never sees the data through MathMotion Studio — it sees it because the teacher chose to share it. Details in §2.

---

## 2. The External AI boundary — the honest picture

The workflow (`MASTER-PROMPT.md` §1) is: the teacher fills in a form → the app generates a **prompt locally** → the teacher **manually copies** it into any External AI (a chatbot, a web tool, whatever they have) → the External AI returns a **scene.md** file → the teacher imports it.

Facts a teacher must understand:

1. **MathMotion Studio never contacts an External AI.** Prompt generation is a local text-template operation; there is no integrated AI, no API key, no paid subscription, and no hidden request (`MASTER-PROMPT.md` §1, §4). Confirmed for today's repository: the only code that exists, `tools/validate_scene.py`, imports only `argparse ast json re sys pathlib dataclasses yaml jsonschema` and performs no network I/O.
2. **The moment you paste the prompt into an External AI, that provider's privacy policy, retention settings, and training settings apply — not this application's.** Whatever the prompt contains (topic, grade, language, your notes, school context) becomes data the third party processes under its own terms.
3. **Pasting the returned scene.md back into MathMotion Studio does not "un-share" it.** The External AI already received the content; importing the answer locally adds no new outbound data flow, but it also doesn't undo the original one.
4. **The application cannot see, audit, or control what you paste.** It has no visibility into the External AI at all. Choosing which tool to use, and what to put into it, is entirely the teacher's decision.

Practical guidance for the copy/paste step is in §4.

---

## 3. What data lives where

### Today (Confirmed)

Nothing is stored by MathMotion Studio because the application does not exist yet. The reference validator only reads a file path you give it and prints a report to the console; it creates no files, no database, and no logs.

### Planned local storage (`MASTER-PROMPT.md` §2, §12)

| Data | Location (planned) | Lifetime |
|---|---|---|
| Lesson metadata (title, topic, grade, language, timestamps, settings, Render job status) | SQLite database under `data/` | Until deleted by the teacher |
| Original Markdown of each imported scene.md | Filesystem under `data/` | Until deleted by the teacher |
| Generated trusted Manim scene code, per-job logs | Per-job directory (isolated, cleaned up) | Temporary; cleaned after the job |
| Rendered MP4 videos | `output/` (configurable output directory) | Until deleted by the teacher |
| Application logs | Local logs folder | Until deleted by the teacher |
| Settings (output directory, default quality/aspect ratio, theme, language) | Local configuration | Until reset |

All of this stays on the machine. There is **no cloud database** and **no mandatory telemetry** (planned). Large video files are kept outside SQLite, on the filesystem, where the teacher can see and delete them directly.

---

## 4. What to know before pasting lesson content into an External AI

A checklist for teachers (and schools) — none of this is enforced by the app; it is your decision space:

1. **Remove student-identifying information.** Names, photos, grades, individual performance notes, or any real classroom data do not belong in a prompt.
2. **Consider school policy.** Many schools restrict which AI tools may be used with lesson material; check before pasting.
3. **Assume prompts may be retained or used for training** by the provider unless you have verified otherwise in that provider's settings and policy; use account settings to opt out where available.
4. **Prefer generic descriptions** ("grade 8, Pythagorean theorem, step-by-step") over pasting proprietary worksheets verbatim.
5. **Remember the generated scene.md comes back from a third party.** It is untrusted input — that is exactly why the app validates it aggressively before rendering ([`SECURITY.md`](SECURITY.md)).
6. **The prompt contains only what you typed.** The app does not enrich it with data from your machine; whatever is in the copied text is what the External AI receives.

---

## 5. No accounts, no telemetry, no elevated privileges (Planned)

Per `MASTER-PROMPT.md` §2, §10, the application is designed to require:

- **No account or login** — no authentication system exists or is planned for the local app.
- **No telemetry** — no usage analytics, crash reporting, or phone-home behavior is planned. Dependency checks (Manim, FFmpeg, LaTeX availability) run locally.
- **No cloud service dependency** — the app works locally after dependencies are installed. The only online step is the teacher's own manual use of an External AI, which happens outside the application.
- **No administrator privileges** — `run.ps1` must avoid requiring elevation.

---

## 6. Deleting your data

### Planned application behavior

- Per-lesson deletion from the **My Animations** and **Render job** views with explicit confirmation, removing the lesson's metadata, source copy, and rendered output (`MASTER-PROMPT.md` §3, §12).
- A configurable output directory, plus cleanup tooling for temporary job files (`MASTER-PROMPT.md` §8, §11 `scripts/cleanup.ps1`).
- Backup/cleanup behavior to be documented in `docs/DATA_MODEL.md` when the storage layer is implemented.

### Manual cleanup you can do today or later (works regardless of app state)

Because everything is local files, full deletion never requires the app:

1. Close MathMotion Studio.
2. Delete the `data/` directory (SQLite database and scene.md copies).
3. Delete or empty the `output/` directory (rendered MP4 files).
4. Delete the local logs folder if you configured one.
5. Optional: uninstall the Python virtual environment created by `run.ps1` to remove installed dependencies.

Deleting these directories removes every artifact MathMotion Studio stores. Nothing is retained anywhere else by the application.

---

## 7. Honest scope — what this document does NOT claim

- **No legal certifications or compliance claims.** MathMotion Studio does not claim GDPR, HIPAA, FERPA, or any other regulatory certification or compliance. It is a local tool; whether its use complies with your institution's policies is your assessment.
- **No security audit has been performed** on the project; see [`SECURITY.md`](SECURITY.md) §6 for the list of implemented vs. planned protections and known gaps.
- **Offline claims are qualified.** The application's features are local, but the *workflow* relies on an External AI that is online by nature. Do not describe the product as fully offline ([`../DOCS-ASSETS-PROMPT.md`](../DOCS-ASSETS-PROMPT.md) §1).
- **Planned behavior is not current behavior.** Anything marked Planned in this document depends on future implementation tracked in [`ROADMAP.md`](ROADMAP.md).

---

## 8. Related documents

- [`SECURITY.md`](SECURITY.md) — trust boundary for untrusted AI-generated input and the protections around it.
- [`TESTING.md`](TESTING.md) — how the validator (the only running component today) is verified.
- [`ROADMAP.md`](ROADMAP.md) — implementation status of the planned storage and deletion behaviors.
- [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) — recovering from failed imports and renders.
