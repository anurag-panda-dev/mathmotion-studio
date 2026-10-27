# MathMotion Studio — Technology stack

> **Reading guide:** This document separates what is **implemented today** (Scene format tooling) from the **planned application stack** defined in [`MASTER-PROMPT.md` §2](../MASTER-PROMPT.md). Nothing in the "planned" tables has been installed or verified in this repository yet; exact dependency versions are **to be pinned when the backend is scaffolded**, after compatibility (especially Manim ↔ Python) is verified — per `MASTER-PROMPT.md` §2, which forbids pinning before verification.

Related: [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) (components), [`docs/DATA_MODEL.md`](DATA_MODEL.md) (structures), [`docs/INSTALLATION.md`](INSTALLATION.md) (setup), [`docs/ROADMAP.md`](ROADMAP.md) (build order).

---

## 1. Implemented today

The only running code in the repository is the Scene format tooling: the reference validator and the machine-readable schemas it enforces. Verified working in the documentation environment: Python 3.11.7, PyYAML 6.0.3, jsonschema 4.26.0 (`python tools\validate_scene.py prompts\examples\pythagorean-theorem.md` → `VALID`, exit code 0).

| Technology | Version constraint | Role | Why chosen | Install prerequisites |
|---|---|---|---|---|
| **Python** | 3.11+ (the validator declares and was verified on 3.11.x) | Runs [`tools/validate_scene.py`](../tools/validate_scene.py). | Matches the planned backend's minimum version so the tooling and the future app share one interpreter baseline. | Any CPython 3.11 or newer on Windows/macOS/Linux. |
| **PyYAML** | unpinned; any version providing `yaml.safe_load` (verified: 6.0.3) | Safe YAML parsing of the front matter and ` ```scene ` blocks. | `safe_load` cannot construct arbitrary Python objects — the parser must never execute file content. | `pip install pyyaml` |
| **jsonschema** | unpinned; must support **draft 2020-12** (verified: 4.26.0) | Validates front matter and scene blocks against the two JSON Schemas (`Draft202012Validator`). | Draft 2020-12 gives conditional schemas (`if`/`then`) used for per-kind object params and per-action field requirements. | `pip install jsonschema` |
| **JSON Schema files** | Scene format **v1.0**, draft 2020-12 | [`schema/lesson-metadata-v1.schema.json`](../schema/lesson-metadata-v1.schema.json) and [`schema/scene-v1.schema.json`](../schema/scene-v1.schema.json) — the machine-readable contract for `scene.md`. | Language-neutral, reusable by the validator today and by the planned Pydantic models, prompt templates, and docs. | None (data files). |

The validator also uses only the Python standard library (`ast` for expression safety — never `eval`, `argparse`, `dataclasses`, `json`, `pathlib`, `re`, `sys`). See [`tools/README.md`](../tools/README.md).

---

## 2. Planned application stack

> **Status: Planned / not yet implemented.** No `backend/`, `frontend/`, or `run.ps1` exists yet. The tables below restate the commitments of [`MASTER-PROMPT.md` §2](../MASTER-PROMPT.md); they are the source of truth until the scaffold exists.

### 2.1 Frontend (planned)

| Technology | Version constraint | Role | Why chosen | Install prerequisites |
|---|---|---|---|---|
| **React** | current stable at scaffold time (to be pinned) | UI library for all application pages. | Ubundant ecosystem; pairs with the required component and data libraries. | Node.js + npm (version to be checked by `run.ps1`). |
| **TypeScript (strict mode)** | current stable (to be pinned) | Type-safe frontend code. | Catches contract drift between UI and the `/api/v1` API at compile time. | As above. |
| **Vite** | current stable (to be pinned) | Dev server and production build. | Fast local dev loop; simple static build the backend can serve in production mode. | As above. |
| **Tailwind CSS** | current stable (to be pinned) | Styling system for the studio design direction (light/dark themes, restrained indigo/violet accents). | Consistent spacing/typography without a heavy abstraction layer. | As above. |
| **shadcn/ui** | current stable (to be pinned) | Accessible, consistent component library (cards, dialogs, forms). | "Such as shadcn/ui" per the spec; accessible components copy-owned in the repo rather than a black-box dependency. | Tailwind + React + TypeScript. |
| **Lucide** | current stable (to be pinned) | Icon set. | Consistent, accessible icons. | As above. |
| **React Router** | current stable (to be pinned) | Page routing (Home, Create Animation, Import Scene, My Animations, Rendering Jobs, Settings, Help). | Standard client-side routing. | As above. |
| **TanStack Query** | current stable (to be pinned) | Server state: API calls, polling of Render job status, caching, invalidation. | Purpose-built for the polling/caching pattern the job monitor needs. | As above. |
| **Zod** | current stable (to be pinned) | Frontend validation of API responses and form input. | Runtime type safety mirroring the backend's Pydantic models. | As above. |
| **Accessible drag-and-drop file uploader** | to be chosen and pinned at scaffold time | `scene.md` upload UX. | Required capability; must be keyboard-accessible. | As above. |

### 2.2 Backend (planned)

| Technology | Version constraint | Role | Why chosen | Install prerequisites |
|---|---|---|---|---|
| **Python** | 3.11+, or a version supported by the selected Manim release — whichever is compatible (verified before pinning) | Application runtime. | Matches existing tooling (see §1). | CPython 3.11+; a virtual environment is created by the launcher. |
| **FastAPI** | current stable (to be pinned) | `/api/v1` HTTP API, OpenAPI-typed routes. | Typed request/response models, async support without blocking on renders. | `pip install fastapi` |
| **Pydantic v2** | v2.x (to be pinned) | Request/response models and Scene format models. | Declarative validation; expresses the JSON Schemas as code for the parser. | `pip install pydantic>=2` |
| **Uvicorn** | current stable (to be pinned) | ASGI server, loopback binding by default. | Standard FastAPI server; lightweight local footprint. | `pip install uvicorn` |
| **Manim Community Edition** | a supported CE release; compatibility with the chosen Python verified **before** pinning | The animation engine; executes only compiler-generated trusted scene code. | The spec's primary rendering engine; rich built-in animation primitives. | See [`docs/INSTALLATION.md`](INSTALLATION.md); FFmpeg required, LaTeX optional. |
| **SymPy** | current stable (to be pinned) | Symbolic checking for `verification` assertions (stage 9) and supported symbolic math. | Exact symbolic simplification for "identically zero" identity checks. | `pip install sympy` |
| **NumPy** | current stable (to be pinned) | Numerical evaluation of assertions and sampled graph values. | Fast, safe numeric evaluation of restricted expressions. | `pip install numpy` |
| **PyYAML** | as §1 | Safe YAML parsing in the application parser (same rules as the reference validator). | One parser behavior shared with the tooling. | `pip install pyyaml` |
| **pytest + HTTPX** | current stable (to be pinned) | Backend test suite (parsing, validation, API, job lifecycle) and async API test client. | Specified test stack ([`MASTER-PROMPT.md` §13](../MASTER-PROMPT.md); [`docs/TESTING.md`](TESTING.md)). | `pip install pytest httpx` |

### 2.3 Rendering and media (planned)

| Technology | Version constraint | Role | Why chosen | Install prerequisites |
|---|---|---|---|---|
| **Manim Community Edition** | as §2.2 | Renders generated scene classes to MP4 at preview/standard/high quality, configurable frame rate and aspect ratio. | Specified engine. | Python package + FFmpeg. |
| **FFmpeg** | a working `ffmpeg` on PATH (version to be detected, not pinned) | Video processing where required by Manim; output verification and export. | Manim's supported media backend. | Separate system install (winget/Chocolatey/manual); detected by `run.ps1` and the Settings health check. |
| **LaTeX (optional)** | any distribution Manim supports (e.g. MiKTeX on Windows) | Advanced mathematical typography for `formula` objects with `renderer: latex`. | Optional dependency; **basic lessons must work without LaTeX** via Manim's text/`MathTex`-free fallbacks — `renderer: text` and `auto` degrade gracefully. | Optional system install; absence is reported as "unavailable", never as an error. |

### 2.4 Storage (planned)

| Technology | Version constraint | Role | Why chosen |
|---|---|---|---|
| **SQLite** | Python stdlib `sqlite3` | Lessons, Render job records, settings, history. | Zero-administration local database; stdlib-only. No cloud database, no authentication, no mandatory telemetry. |
| **Filesystem** | — | Original `scene.md` sources, generated Manim code, logs, per-job temporary directories, final MP4s. | Large binaries stay out of the database; outputs are plain files the teacher can find and share. |

### 2.5 Development, launch, and quality (planned)

| Technology | Version constraint | Role | Why chosen |
|---|---|---|---|
| **Windows PowerShell 5.1 + PowerShell 7** | both compatible where practical | `run.ps1` / `stop.ps1` launch scripts; automated environment checks; no administrator privileges required. | The teacher's platform is Windows 10/11; one-command launch is an acceptance criterion. |
| **Python virtual environment** | stdlib `venv` | Isolated backend dependencies. | Reproducible local install; no global pollution. |
| **npm** | version detected by the launcher | Frontend dependency install and build. | Standard JS toolchain with Vite. |
| **Ruff** | current stable (to be pinned) | Python linting and formatting. | One fast tool replacing flake8/isort/black for the backend. |
| **ESLint + TypeScript checking** | current stable (to be pinned) | Frontend lint and type checking. | Standard TS quality gate. |

---

## 3. Explicit non-dependencies

MathMotion Studio requires **none** of the following:

- **No Docker** — Docker is explicitly not a prerequisite ([`MASTER-PROMPT.md` §2](../MASTER-PROMPT.md)).
- **No cloud services** — no cloud database, no hosted backend, no telemetry.
- **No accounts or API keys** — the External AI is chosen and used by the teacher entirely outside the application; the app itself never calls an AI service and requires no AI API key, account, or paid subscription.
- **No authentication layer** — the app is single-user and local (loopback networking by default).
- **No administrator privileges** — installation and launch must not require elevation.

See [`docs/SECURITY.md`](SECURITY.md) for the trust-boundary and privacy implications of the External AI workflow.
