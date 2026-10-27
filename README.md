<p align="center">
  <img src="branding/logo-primary.svg" alt="MathMotion Studio logo" width="420">
</p>

<h1 align="center">MathMotion Studio</h1>

<p align="center">
  <strong>Turn a math topic into a beautiful animated lesson — by describing it, not by coding it.</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB.svg?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/FastAPI-009688.svg?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-19-61DAFB.svg?style=flat-square&logo=react&logoColor=black" alt="React 19">
  <img src="https://img.shields.io/badge/Manim-0.19-8A2BE2.svg?style=flat-square" alt="Manim">
  <img src="https://img.shields.io/badge/scene_format-v1.0-6A4AEE.svg?style=flat-square" alt="Scene format v1.0">
  <img src="https://img.shields.io/badge/platform-Windows-0078D6.svg?style=flat-square&logo=windows&logoColor=white" alt="Windows">
</p>

<p align="center">
  <a href="#-why-not-ai-generated-code">Why</a> ·
  <a href="#%EF%B8%8F-features">Features</a> ·
  <a href="#-quick-start">Quick start</a> ·
  <a href="#scenemd-at-a-glance">scene.md</a> ·
  <a href="#-architecture">Architecture</a> ·
  <a href="#-documentation-map">Docs</a> ·
  <a href="#-roadmap">Roadmap</a>
</p>

---

MathMotion Studio is a **local-first, AI-assisted mathematics animation studio** built for teachers. You describe a lesson — *"the Pythagorean theorem"*, *"equivalent fractions"*, *"the unit circle"* — the app assembles a prompt for the **External AI you already use** (ChatGPT, Claude, Gemini, …), and the AI returns a structured `scene.md` file. MathMotion validates it, compiles it through a **trusted compiler**, and renders a narrated-quality animation with **Manim** — entirely on your own machine. No cloud rendering, no API keys, no accounts, no code.

> **Status — alpha.** The scene format toolkit (spec, schemas, validator, prompt package, nine validated lessons) is complete and stable. The application — FastAPI backend, React UI, trusted compiler, and Manim render pipeline — is implemented and under active hardening. See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the milestone breakdown.

## 🛡️ Why *not* AI-generated code?

The app never asks an AI to write Python, and never executes AI-generated code. The AI fills in a **declarative** `scene.md` file — YAML front matter plus fenced ` ```scene ` blocks of objects and timed actions. That file is **data, not a program**: it can be parsed, schema-validated, mathematically verified (SymPy), and rendered without ever running untrusted code on your machine.

That is the whole philosophy: **the AI proposes, the validator decides, the compiler renders.** ([`docs/SECURITY.md`](docs/SECURITY.md), [`prompts/SCENE_VALIDATION_RULES.md`](prompts/SCENE_VALIDATION_RULES.md))

## ✨ Features

- **📝 Prompt builder** — pick a topic, grade level, duration, theme and style; get a ready-to-paste prompt tuned for your AI of choice.
- **📥 Scene import & review** — paste or drop the AI's `scene.md`, see validation errors explained in plain language, and iterate with a one-click correction prompt.
- **✅ Reference validator** — `scene.md` checked against JSON Schemas (draft 2020-12) and the full v1.0 format: 19 object kinds, 15 action types, coordinates, colors, timing rules.
- **🔢 Math verification** — expressions are parsed and verified with SymPy before anything renders.
- **🎬 Trusted compiler → Manim** — a deterministic compiler turns validated scenes into Manim code; the render worker runs jobs with progress, phases, cancel and retry.
- **📊 Render job management** — a persistent job queue with live status, output gallery and history.
- **🔒 Local-first & private** — everything runs on loopback on your Windows machine; lessons, media and jobs never leave your disk. No telemetry.
- **🎨 Themed output** — dark/light lesson themes (e.g. `midnight`, `ivory`) with a consistent design system.

## ⚡ Quick start

**Requirements:** Windows 10/11, [Python 3.11+](https://www.python.org/), [Node.js 20+](https://nodejs.org/), and [FFmpeg](https://ffmpeg.org/) (for video output). Full guide: [`docs/INSTALLATION.md`](docs/INSTALLATION.md).

```powershell
# 1) One-time: create the virtualenv and install backend dependencies
.\run.ps1 -Setup

# 2) One-time: build the frontend (the backend serves it at :8765)
cd frontend; npm ci; npm run build; cd ..

# 3) Launch — checks the environment, starts FastAPI, opens your browser
.\run.ps1

# Development with hot reload (backend :8765 + Vite dev server :5173)
.\start.ps1          # in a second terminal, keep run.ps1 running

# Stop everything cleanly
.\stop.ps1
```

Then open **http://127.0.0.1:8765**, build a prompt in the **Prompt builder**, paste it into your AI, and import the returned `scene.md` in **Scene import**. Video rendering additionally needs FFmpeg and Manim (`pip install -r backend/requirements-render.txt` — `run.ps1` reports what's missing).

**Toolkit only?** No app needed to check a lesson:

```powershell
pip install pyyaml jsonschema
python tools\validate_scene.py prompts\examples\pythagorean-theorem.md   # human-readable
python tools\validate_scene.py my-scene.md --json                        # structured report
```

Exit codes: `0` valid · `1` errors found · `2` usage or environment error.

## 🧩 scene.md at a glance

YAML front matter (lesson metadata, objectives, practice questions, verification assertions) plus one fenced ` ```scene ` block per scene. Trimmed from [`prompts/examples/pythagorean-theorem.md`](prompts/examples/pythagorean-theorem.md):

````markdown
---
schema_version: "1.0"
lesson:
  title: The Pythagorean Theorem
  grade: "8"
  duration_minutes: 5
  theme: midnight
---

```scene
id: s1
title: Opening
type: intro
duration: 12
objects:
  - id: title
    kind: text
    params: { content: "The Pythagorean Theorem", position: [0, 2], font_size: 56, color: violet }
actions:
  - { action: create, target: title, at: 0 }
  - { action: indicate, target: title, style: pulse, at: 5, duration: 1.5 }
```
````

Full grammar: [`prompts/SCENE_FORMAT_SPEC.md`](prompts/SCENE_FORMAT_SPEC.md). Nine complete lessons — algebra, geometry, trigonometry, calculus, arithmetic, statistics — live in [`prompts/examples/`](prompts/examples/), all passing the validator with zero errors.

## 🏗️ Architecture

```text
┌─────────────── Windows machine (loopback only) ────────────────┐
│                                                                │
│  React 19 + Vite UI ──/api──► FastAPI backend                  │
│  (prompt builder,           (parser · validation · SymPy       │
│   scene review,              verification · SQLite persistence) │
│   render jobs)                        │                        │
│                                       ▼                        │
│                          trusted compiler (scene → Manim)      │
│                                       │                        │
│                                       ▼                        │
│                          render worker ──► Manim ──► MP4        │
│                                                                │
│  Any External AI (ChatGPT / Claude / Gemini) ──copy/paste──►   │
└────────────────────────────────────────────────────────────────┘
```

| Path | Contents |
|---|---|
| [`backend/app/`](backend/app/) | FastAPI app: `api/` routes · `parser/` · `validation/` · `rendering/` (compiler, layouts, Manim runtime, worker) · `storage/` · `services/` · `core/` (config, security, logging). |
| [`backend/tests/`](backend/tests/) | 94 pytest tests: parser, validation, compiler, jobs, security, prompt generation, example-corpus regression. |
| [`frontend/src/`](frontend/src/) | React 19 + TypeScript + Tailwind 4 UI: dashboard, prompt-builder, scene-import, scene-review, render-jobs, animations, settings, help. |
| [`prompts/`](prompts/) | Scene format spec v1.0, validation rules, prompt templates, External-AI guide, example scenes. |
| [`schema/`](schema/) | JSON Schemas for `scene.md` front matter and scene blocks. |
| [`tools/`](tools/) | `validate_scene.py` (reference validator), `build_brand_svgs.py` (branding generator). |
| [`branding/`](branding/) | Logo/icon SVGs, PNG/ICO exports, measured palette, brand guidelines. |
| [`docs/`](docs/) | PRD, roadmap, architecture, tech stack, security, privacy, installation, testing, UI spec, user guide. |
| [`assets/`](assets/) | Original raster masters and generated vector references (do not modify). |

### Tech stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Python 3.11 · FastAPI · Pydantic v2 | Typed, fast, first-class OpenAPI. |
| Validation | JSON Schema 2020-12 · PyYAML | One schema drives both validator and AI prompt. |
| Math | SymPy · NumPy | Symbolic verification before rendering. |
| Rendering | Manim CE 0.19 · background worker | Programmatic, deterministic, beautiful math animation. |
| Frontend | React 19 · TypeScript · Vite · Tailwind 4 · TanStack Query | Modern, type-safe, fast DX. |
| Persistence | SQLite (local file) | Zero-config, portable, private. |

## ✅ Testing & quality

```powershell
cd backend; pytest                 # 94 tests, includes the 9-example regression corpus
cd backend; ruff check .           # lint (line length 100, py311)
cd frontend; npm run typecheck     # tsc --noEmit
cd frontend; npm run lint          # eslint
```

## 📚 Documentation map

| Document | For |
|---|---|
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | What is done, what is next — start here. |
| [`docs/PRD.md`](docs/PRD.md) | Product requirements, user stories, acceptance criteria. |
| [`docs/INSTALLATION.md`](docs/INSTALLATION.md) | Step-by-step setup for the app and the toolkit. |
| [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) | How a teacher works with lessons and scenes. |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) · [`docs/TECH_STACK.md`](docs/TECH_STACK.md) | System design and technology choices. |
| [`docs/SECURITY.md`](docs/SECURITY.md) · [`docs/PRIVACY.md`](docs/PRIVACY.md) | Threat model, untrusted-file handling, data-privacy posture. |
| [`docs/TESTING.md`](docs/TESTING.md) · [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) | Validation workflow and common fixes. |

## 🗺️ Roadmap

Highlights from [`docs/ROADMAP.md`](docs/ROADMAP.md):

- **Done** — Scene format v1.0 (spec, schemas, validator, prompt package, nine lessons), application foundation, UI system, prompt builder, parser & import, trusted compiler, render pipeline.
- **In flight** — import/preview/library polish, persistence & diagnostics, hardening & quality (M7–M9).
- **Next** — release readiness: packaging, installers, docs sweep (M10).

Contributions and issues are welcome once the first public release lands — for now, star ⭐ the repo and follow the roadmap.

## 🎨 Branding

Canonical colors: **navy `#061830`**, **violet `#6A4AEE`**, **ivory `#F1F3EA`** — machine-readable in [`branding/palette.json`](branding/palette.json). The logo and icon SVGs are generated by [`tools/build_brand_svgs.py`](tools/build_brand_svgs.py); regenerate rather than hand-editing. Usage rules: [`branding/BRAND_GUIDELINES.md`](branding/BRAND_GUIDELINES.md).

## 📄 License

Released under the [MIT License](LICENSE). Verified findings about specific External AI tools are recorded in [`prompts/AI_COMPATIBILITY.md`](prompts/AI_COMPATIBILITY.md).

---

<p align="center">
  <sub>Built for teachers who'd rather explain the math than fight the software.<br>
  Terminology is fixed: <b>MathMotion Studio</b> · <b>scene.md</b> · <b>Scene format</b> · <b>Render job</b> · <b>External AI</b>.</sub>
</p>
