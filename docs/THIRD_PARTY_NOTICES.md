# MathMotion Studio — Third-Party Notices

**Purpose:** inventory of the third-party software MathMotion Studio depends on, the licenses they are distributed under, and the verification state of each claim. This document exists so that releases ship with accurate attribution and so that no license claim is ever made without evidence.

**Policy — verify before shipping, never claim unverified licensing.** A license entry may only be stated as verified after checking the actual source (installed package metadata, the upstream repository `LICENSE` file, or the official distribution). Anything else is marked *to be verified*. Full license texts are **not** copied here; each entry links to its upstream source instead. Do not invent version numbers — record versions only when observed on a real installation.

## How to keep this document updated

1. **On every dependency change** (added, removed, upgraded, or re-pinned): update the corresponding table row in the same commit/PR that changes the dependency.
2. **Before every release:** re-verify Tier 1 entries against the actually installed versions and complete the pending verification of Tier 2 entries for everything that ships in that release (see [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md) §7).
3. **Verification method (Python packages):** inspect installed metadata, e.g.
   `python -c "from importlib.metadata import metadata; print(metadata('PyYAML').get('License'))"`
   or check the `License` / `License-Expression` field and the upstream repository.
4. **Verification method (npm packages):** check the `license` field in `package.json` and the upstream repository `LICENSE` file.
5. If verification is impossible at release time, ship the entry as *license to be verified at build time* — never upgrade it to "verified" on assumption.

---

## Tier 1 — Currently used components (implemented tooling only)

These are dependencies of what exists in the repository today: the reference validator `tools/validate_scene.py` (requires Python 3.11+, `pyyaml`, `jsonschema` per [`../tools/README.md`](../tools/README.md)).

| Component | Role | Version observed | License | Verification |
|---|---|---|---|---|
| Python | Runtime for the reference validator | 3.11.7 (observed 2026-10-27) | PSF License Agreement (Python Software Foundation License) | Standard CPython license — confirm the installed distribution's license at build time: <https://www.python.org/licenses/> |
| PyYAML | Safe YAML parsing of `scene.md` front matter and scene blocks | 6.0.3 (observed 2026-10-27) | **MIT** | Verified from installed package metadata (2026-10-27); upstream: <https://github.com/yaml/pyyaml> |
| jsonschema | JSON Schema (draft 2020-12) validation against `schema/*.schema.json` | 4.26.0 (observed 2026-10-27) | **MIT** | Verified from installed package metadata (2026-10-27); upstream: <https://github.com/python-jsonschema/jsonschema> |

Note: `jsonschema` and `PyYAML` carry their own transitive dependencies (e.g. `attrs`, `jsonschema-specifications`, `referencing`, `rpds-py`, `typing-extensions` for jsonschema; none beyond the standard library commonly flagged for PyYAML at runtime). Transitive dependency licenses must be enumerated from the actual environment at release time; none are bundled as source in this repository today.

**No third-party assets, fonts, images, or media are bundled in this repository today.** The files in `assets/` (`mathmotion_logo_dark.png`, `mathmotion_logo_light.png`, `mathmotion_app_icon.png`) are original project branding created for MathMotion Studio, not third-party material. Any font or asset adopted later (for example, a webfont for the planned frontend) must be added to this document — with its license verified — **before** it is shipped.

---

## Tier 2 — Planned application dependencies

> **Status of this entire tier: planned — license verification pending.**
> The application is not implemented yet ([`ROADMAP.md`](ROADMAP.md)). The components below are the planned stack from `MASTER-PROMPT.md` §2. "Expected license" entries reflect the upstream projects' published licenses at time of writing, but **none of this is verified against an installed release of this application** — every row must be verified (and version-pinned) at build time per the update procedure above. Do not treat these entries as final or as shipping attribution.

### Frontend (planned)

| Component | Role | Expected license | Upstream |
|---|---|---|---|
| React | UI library | MIT | <https://github.com/facebook/react> |
| TypeScript | Language (strict mode) | Apache-2.0 | <https://github.com/microsoft/TypeScript> |
| Vite | Build tool / dev server | MIT | <https://github.com/vitejs/vite> |
| Tailwind CSS | Styling | MIT | <https://github.com/tailwindlabs/tailwindcss> |
| shadcn/ui | Accessible component collection | MIT | <https://github.com/shadcn-ui/ui> |
| Lucide icons | Icon set | ISC (published as MIT-family; verify) | <https://github.com/lucide-icons/lucide> |
| React Router | Client-side routing | MIT | <https://github.com/remix-run/react-router> |
| TanStack Query | Server-state management | MIT | <https://github.com/TanStack/query> |
| Zod | Frontend validation | MIT | <https://github.com/colinhacks/zod> |
| Accessible drag-and-drop uploader | File upload component | **To be verified — library not yet selected** | — |

### Backend (planned)

| Component | Role | Expected license | Upstream |
|---|---|---|---|
| Python 3.11+ | Runtime | PSF License Agreement | <https://www.python.org/licenses/> |
| FastAPI | Local API service | MIT | <https://github.com/tiangolo/fastapi> |
| Pydantic v2 | Request/response and schema models | MIT | <https://github.com/pydantic/pydantic> |
| Uvicorn | ASGI server | BSD-3-Clause | <https://github.com/encode/uvicorn> |
| SymPy | Symbolic verification of supported expressions | BSD | <https://github.com/sympy/sympy> |
| NumPy | Numerical checks | BSD-3-Clause | <https://github.com/numpy/numpy> |
| PyYAML | YAML parsing | MIT | <https://github.com/yaml/pyyaml> |
| SQLite (Python standard library `sqlite3`) | Local metadata/job storage | PSF (Python stdlib; the SQLite engine public domain — <https://www.sqlite.org/copyright.html>) | — |
| pytest | Backend test framework | MIT | <https://github.com/pytest-dev/pytest> |
| HTTPX | Test HTTP client | BSD-3-Clause | <https://github.com/encode/httpx> |

### Rendering and media (planned)

| Component | Role | Expected license | Upstream / note |
|---|---|---|---|
| Manim Community Edition | Animation engine | MIT | <https://github.com/ManimCommunity/manim> |
| FFmpeg | Video processing | **License depends on build configuration** — typically LGPL 2.1-or-later; GPL 2.0-or-later if built with `--enable-gpl` components. Verify the exact build used and comply accordingly. | <https://ffmpeg.org/legal.html> |
| LaTeX (optional) | Advanced mathematical typography | LPPL 1.3c (LaTeX itself); distributions (e.g. MiKTeX, TeX Live) ship many packages under various licenses — verify the chosen distribution. Optional: basic lessons must work without it. | <https://www.latex-project.org/legal/> |

### Development and launch tooling (planned)

| Component | Role | Expected license | Upstream |
|---|---|---|---|
| Node.js | Frontend toolchain runtime | MIT | <https://github.com/nodejs/node> |
| npm | Frontend package manager | Artistic-2.0 | <https://github.com/npm/cli> |
| Ruff | Python linting and formatting | MIT | <https://github.com/astral-sh/ruff> |
| ESLint | Frontend linting | MIT | <https://github.com/eslint/eslint> |
| PowerShell 7 (optional) | Launcher runtime alternative; `run.ps1` targets PowerShell 5.1 and 7 | MIT | <https://github.com/PowerShell/PowerShell> |

Windows PowerShell 5.1 is a component of the Windows operating system, used in place — it is not redistributed by this project.

---

## Bundled assets and fonts — current state and policy

- **Today:** no third-party assets, fonts, icon sets, media, or code from other projects are bundled in this repository. Branding PNGs in `assets/` are original project work.
- **Planned frontend:** when the React application is built, any webfont, icon package, or component copied into the repository (rather than referenced as a normal dependency) must be inventoried here **before shipping**, with its license verified from its upstream source.
- **Example scenes and prompts:** `prompts/` and `schema/` are original project specification artifacts; they contain no third-party content.
- **Hard rule:** releases must never ship a dependency, asset, or font whose license has not been verified and recorded in this document. If verification fails, replace the component or block the release.

---

*Related documents:* [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md) (§7 security/dependency review) · [`ROADMAP.md`](ROADMAP.md) · [`SECURITY.md`](SECURITY.md) · [`../tools/README.md`](../tools/README.md) · [`../schema/README.md`](../schema/README.md)
