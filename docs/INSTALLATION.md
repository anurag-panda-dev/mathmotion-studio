# Installing MathMotion Studio

Welcome! This guide explains what you can install and use **today**, and what will become available when the full MathMotion Studio application is released.

> **Current status — please read first.** The MathMotion Studio application (the dashboard, the one-click launcher `run.ps1`, and the video renderer) is **not yet released** — see [`ROADMAP.md`](ROADMAP.md) for the release plan. What exists today is the **Scene format toolkit**: prompt templates for an **External AI** and a checking tool (the *validator*) that tells you whether a **scene.md** file is correct. You can already prepare complete lessons with it; turning them into videos arrives with the application release.

## 1. What you can use today

| Item | Available today? | What it does |
|---|---|---|
| Prompt templates (`prompts/`) | ✅ Yes | Ready-made instructions you paste into an External AI to produce a lesson file. |
| Example lessons (`prompts/examples/`) | ✅ Yes | Nine finished, checked `scene.md` lessons you can learn from or reuse. |
| Validator (`tools/validate_scene.py`) | ✅ Yes | A small checking program that finds mistakes in a `scene.md` file and explains them. |
| Full application (`run.ps1`, dashboard, renderer) | ❌ Not yet | Planned — see [`ROADMAP.md`](ROADMAP.md). |

You do **not** need Node.js, FFmpeg, or LaTeX for anything in this section — those are planned application prerequisites only (§5).

## 2. What you need today

| Requirement | Why | How to check |
|---|---|---|
| Windows 10 or 11 | The toolkit and the future application run on Windows. | — |
| Python 3.11 or newer | The validator is a small Python program. | `python --version` |
| Two free Python packages: `pyyaml` and `jsonschema` | The validator reads and checks `scene.md` files with them. | See step 3 below. |

Python is free software that runs programs like this one. If you have never installed it, download the current **Python 3.11+** installer from `python.org`, run it, and **tick the box that says "Add python.exe to PATH"** on the first installer screen — this step is easy to miss and causes most setup problems (see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)).

## 3. Setting up the toolkit — step by step

**Step 1 — Get the project files.**
Download or receive the MathMotion Studio project folder and place it somewhere easy to find, for example `Documents\MathMotion-Studio`. Keep the folder structure intact — inside you should see at least `prompts/`, `schema/`, and `tools/`.

**Step 2 — Open PowerShell in the project folder.**
Open the project folder in File Explorer, click in the empty area of the address bar, type `powershell`, and press **Enter**. A blue window opens — this is PowerShell, and every command below goes there.

**Step 3 — Check Python and install the two packages.**

```powershell
python --version
```

You want to see `Python 3.11` or higher. Then install the two packages:

```powershell
python -m pip install pyyaml jsonschema
```

(`pip` is Python's package installer; the command simply means "have Python install these two free packages".)

**Step 4 — Verify the installation.**
Still in the same window, run the validator against one of the included example lessons:

```powershell
python tools\validate_scene.py prompts\examples\pythagorean-theorem.md
```

A correct installation prints, exactly:

```text
VALID  prompts\examples\pythagorean-theorem.md  (schema 1.0)
  0 error(s), 0 warning(s)
```

That is the whole installation. You can now check any `scene.md` file the same way — see the [USER_GUIDE.md](USER_GUIDE.md) for the full lesson workflow.

> **Known issue (verified):** the validator's `--version` switch currently crashes with a `NameError` instead of printing the version. Everything else works normally. Details and workaround: [TROUBLESHOOTING.md](TROUBLESHOOTING.md#confirmed-the---version-switch-crashes).

## 4. What you can do today — honestly

With the toolkit you can:

1. Build a complete lesson prompt from the templates and ask an External AI to write a **scene.md** file.
2. Check that file with the validator and get plain-language error reports.
3. Ask the External AI to fix the reported problems and re-check, until the file is valid.
4. Study nine finished example lessons covering algebra, geometry, trigonometry, calculus, statistics, and arithmetic.

You **cannot yet** render an MP4 video, use a dashboard, or run `run.ps1` — those belong to the application release. A file that passes validation is a correct lesson file; it has not been tested as a video, and no video exists yet.

## 5. Planned — the full application (not yet available)

Everything in this section describes the **planned** application from the build specification. None of it can be installed yet; it is published here so you know what is coming. The authoritative release plan is [`ROADMAP.md`](ROADMAP.md).

When the application releases, installation will require:

| Planned prerequisite | Needed for | Notes |
|---|---|---|
| Python 3.11+ | Backend and renderer | Same as today. |
| Manim Community Edition | Turning scene files into animations | Installed automatically during planned setup. |
| FFmpeg | Producing the final MP4 file | Installed or checked during planned setup. |
| LaTeX (optional) | Fancy mathematical typography | Optional — simple formulas work without it. |
| Node.js / npm | Building the dashboard interface | Only needed for development mode. |

The planned launcher is a single script in the project root:

```powershell
.\run.ps1              # normal start: checks everything, starts the app, opens your browser
.\run.ps1 -Setup       # planned: install/repair dependencies only
.\run.ps1 -Dev         # planned: development mode
.\run.ps1 -Diagnostics # planned: check what is installed and what is missing
```

The planned setup creates its own private Python environment inside the project, so it will not interfere with other Python programs on your computer, and it will not require administrator privileges.

## 6. Where your files will be stored (planned)

The planned application keeps everything inside the project folder, in two places:

| Planned folder | Contents |
|---|---|
| `data/` | Lesson records and settings (a small local database). Never sent anywhere — everything stays on your computer. |
| `output/` | Rendered MP4 videos, one subfolder per lesson. |

Today these folders do not exist and no files are written automatically — you decide where to keep your `scene.md` files (a folder such as `Documents\MathMotion` works well). See [SECURITY.md](SECURITY.md) for how the planned application handles your files and privacy.

## 7. Installation problems?

The most common problems and their fixes are collected in [TROUBLESHOOTING.md](TROUBLESHOOTING.md). In short:

| Symptom | Likely cause | Fix |
|---|---|---|
| `'python' is not recognized…` | Python not installed, or installed without "Add to PATH" | Reinstall Python with the PATH box ticked, or use `py -3.11` instead of `python` in every command |
| `Python 3.9`-style lower version | An older Python is found first | Install Python 3.11+ and repeat step 3 with `py -3.11` |
| `Missing dependency: …` when validating | `pyyaml` / `jsonschema` not installed | `python -m pip install pyyaml jsonschema` |
| `error: file not found` | Wrong file path, or PowerShell not opened in the project folder | Re-open PowerShell in the project folder and check the file name |

## 8. Updating or removing the toolkit

The toolkit has no version updates of its own — it is simply the project folder. To remove the two Python packages from your computer (only needed if nothing else uses them):

```powershell
python -m pip uninstall pyyaml jsonschema
```

---

**Next:** [USER_GUIDE.md](USER_GUIDE.md) — creating your first lesson, step by step.
