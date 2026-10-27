# Troubleshooting

Every problem below is labelled honestly:

- **✅ Confirmed** — reproduced by actually running the tools in this project; the error text shown is real output.
- **◐ Potential** — a possible problem based on how the tools are designed; *not* reproduced here.
- **◔ Planned application** — a failure mode of the future application (not released yet, [`ROADMAP.md`](ROADMAP.md)); listed so you recognize it once the release arrives.

If you have not set the toolkit up yet, start with [INSTALLATION.md](INSTALLATION.md).

## 1. First diagnostics — check these first

1. **What is the exit code?** In PowerShell, after a command runs, type:

   ```powershell
   echo $LASTEXITCODE
   ```

   The validator's codes: **`0`** = valid (warnings allowed) · **`1`** = errors found · **`2`** = usage or environment problem.

2. **Get the structured report.** This prints every problem with a category, location, message, and suggestion — copy it *in full* into the correction prompt:

   ```powershell
   python tools\validate_scene.py your-file.md --json
   ```

3. **The validator only reads files.** It never edits or deletes your work — running it, re-running it, and keeping old copies is always safe.

## 2. ✅ Confirmed problems with scene files

All outputs in this section were produced by running the validator in this project.

### The file is rejected before any scene is checked

| Symptom (real output) | Likely cause | Fix |
|---|---|---|
| `missing_front_matter — file must start with YAML front matter delimited by '---'` | The AI's commentary or a ```markdown fence sits at the top of the file, or the front matter is missing entirely | Delete everything above the first `---`. If there is no `---` block at all, ask the AI to produce the file with front matter (the prompt templates demand this). |
| `yaml_syntax — front matter is not valid YAML: expected <block end>, but found '<scalar>'` (reported at the offending line) | An unclosed quotation mark — most often a title containing `"` that was never closed, or a value containing `:` left unquoted | Ask the AI to re-quote the value, e.g. `title: "Balancing equations: basics"`. Simplest fix: run it through the correction prompt with this error report. |
| `schema_version '2.0' is not supported; this validator implements 1.0` | The AI invented a newer version, or copied an old file | The file must say `schema_version: "1.0"`. Regenerate with the current templates if in doubt. |
| `file is not valid UTF-8` *(potential — not reproduced here)* | The file was saved in an unusual encoding | Re-save from Notepad as **UTF-8**. |
| `file is … bytes; limit is 512 KB` *(potential — not reproduced here)* | An unusually huge lesson | Split the lesson into two files of fewer scenes each. |

### The scene blocks contain mistakes

The most instructive real report — one deliberately broken file producing several typical errors at once:

```text
INVALID  broken-references.md  (schema 1.0)
  [ERROR  ] schema  s1.$.objects.0.params.color:21
            'magenta' does not match '^(navy|violet|ivory|white|black|gray|red|green|blue|amber|teal|pink|#[0-9a-fA-F]{6})$'
            hint: Compare with SCENE_FORMAT_SPEC.md sections 4-6.
  [ERROR  ] kind_mismatch  s1.-:22
            'write' requires a text, formula, or equation object; 'circ' is a circle
            hint: Use 'create' for this object, or change the object kind.
  [ERROR  ] unknown_target  s1.actions[].target:41
            action 'create' targets unknown object 'ghost'
            hint: Declare the object in 'objects' or fix the id.
  [ERROR  ] color_unknown  s1.-
            unknown color 'magenta'
            hint: Use a palette name (amber, black, blue, gray, green, ivory, navy, pink, red, teal, violet, white) or #RRGGBB.
  [WARNING] unused_object  s1.-
            object 'unused_shape' is never used by any action
            hint: Remove it or add an action that uses it.
  [WARNING] out_of_frame  s1.-:32
            position [20, 0] lies outside the 16:9 frame (x -7.0..7.0, y -4.0..4.0); it will be clipped
            hint: Move the object inside the frame or change the aspect ratio.
  4 error(s), 2 warning(s)
```

The complete catalogue, one row per problem:

| Category (severity) | What it means | Fix |
|---|---|---|
| `schema` (error) | A field is missing, misspelled, the wrong type, out of range, or unknown. Unknown fields are **rejected on purpose** so an AI's typo never silently changes your lesson. | Compare with the field tables in [`prompts/SCENE_FORMAT_SPEC.md`](../prompts/SCENE_FORMAT_SPEC.md) §3–§6, or use the correction prompt. |
| `duplicate_id` (error) | A scene id or an object id is used twice. Ids must be unique. | Rename one of them (`s1`, `s2`, … / `tri`, `sq_a`, …). |
| `unknown_target` (error) | An action mentions an object that was never declared in `objects` — usually a typo in the id, or a forgotten object. | Declare the object or correct the spelling of the id. |
| `kind_mismatch` (error) | An action is impossible for that object — e.g. `write` only works on `text`, `formula`, or `equation` objects; a `function_graph` or `area_fill` needs an `axes` object in the same scene. | Use `create` for shapes; add an `axes` object for graphs; or change the object kind. |
| `unsafe_expression` (error) | A mathematical expression left the Scene format's small safe grammar. Expressions may use numbers, `x`, `+ - * / **`, `pi`, `e`, and only these functions: `sin cos tan asin acos atan sqrt abs ln log log10 exp floor ceil round min max`. | Rewrite using the allowed functions. Real example — this was correctly rejected: `expression "open('/etc/passwd').read()": function 'complex expression' is not in the allowlist (…)`. This strictness is what makes scene files safe to receive from an AI ([SECURITY.md](SECURITY.md)). |
| `color_unknown` (error) | A color is neither a palette name nor a hex code like `#1E1B4B`. | Use: navy, violet, ivory, white, black, gray, red, green, blue, amber, teal, pink — or `#RRGGBB`. |
| `timing_overflow` (error) | The actions run far past the scene's declared `duration` (more than 5 s over). Real example: `actions run to about 69.5s but the scene declares 5s`. | Raise `duration`, or move the actions earlier. |
| `empty_scene` (error) | The file has no ```scene blocks, or a scene declares objects but no actions. | Add scene content; every scene needs at least one action. |
| `out_of_frame` (**warning**) | An object is positioned outside the visible picture and will be clipped. | Move it inside the frame, or change the aspect ratio (16:9: x −7…7, y −4…4). |
| `unused_object` (**warning**) | An object is declared but no action ever uses it. | Remove it, or add an action that uses it. |
| `timing_tight` (**warning**) | The declared `duration` is much shorter than the actions need. | Raise `duration` for better pacing. |

Warnings do **not** block you: a file with warnings only still exits `0` and is valid.

## 3. ✅ Confirmed problems with the tools themselves

### The `--version` switch crashes

Running `python tools\validate_scene.py --version` in this project fails with:

```text
Traceback (most recent call last):
  File "...\tools\validate_scene.py", line 386, in main
    print(f"scene-format {SCENE_VERSION}")
          ^^^^^^^^^^^^^^
NameError: name 'SCENE_VERSION' is not defined. Did you mean: 'SCHEMA_VERSION'?
```

- **Likely cause:** a naming mistake inside the validator script itself (the code defines `SCHEMA_VERSION` but prints `SCENE_VERSION`). It is a defect in the tool, not in your file or your computer.
- **Impact:** only the `--version` switch is affected. Normal validation, `--json`, and `--quiet` all work correctly (verified).
- **Workaround:** you do not need `--version` for any workflow step. The format version is visible in every normal report — e.g. `VALID … (schema 1.0)` — and is documented as **Scene format 1.0** in [`prompts/SCENE_FORMAT_SPEC.md`](../prompts/SCENE_FORMAT_SPEC.md).

### The validator refuses to run at all (exit code 2)

| Real output | Likely cause | Fix |
|---|---|---|
| `usage: validate_scene.py [-h] [--json] [--quiet] [--version] [file]` | No file name was given | Type the command as `python tools\validate_scene.py your-file.md` |
| `error: file not found: nonexistent.md` | Wrong file name, wrong folder, or PowerShell is not open in the project folder | Check the path; re-open PowerShell inside the project folder (File Explorer address bar → type `powershell` → Enter) |

## 4. ◐ Potential environment problems

These are designed behaviours of the toolkit, documented from its source and requirements; they were **not** reproduced in the environment where this guide was written (Python 3.11, `pyyaml` and `jsonschema` installed), so treat them as "if this happens to you…".

| Symptom | Likely cause | Fix |
|---|---|---|
| `'python' is not recognized as an internal or external command` | Python is not installed, or was installed without "Add python.exe to PATH" | Reinstall Python 3.11+ ticking the PATH box; or call the Windows Python launcher instead: `py -3.11 tools\validate_scene.py your-file.md` (verified working as an alternative in this project's environment). |
| A version older than 3.11 is reported, or an odd import error | An old Python is found first | Check with `python --version`; run with `py -3.11 …` to target a specific version. |
| `Missing dependency: … Install with: pip install pyyaml jsonschema` (the validator exits with code `2`) | `pyyaml` or `jsonschema` is not installed for the Python you are using | `python -m pip install pyyaml jsonschema` — then validate again. |
| `Permission denied` or a Microsoft Store window opens when typing `python` | The Windows "App execution alias" for Python is redirecting to the Store | In Windows Settings search "Manage app execution aliases" and turn off the `python.exe`/`python3.exe` Store aliases, or simply use `py -3.11`. |
| pip errors mentioning permissions, proxies, or company networks | Restricted network or per-user install policy | Ask your IT department, or install for yourself only: `python -m pip install --user pyyaml jsonschema`. |

## 5. Problems coming from the External AI

Guidance from [`prompts/AI_COMPATIBILITY.md`](../prompts/AI_COMPATIBILITY.md). No particular AI tool has been verified against these prompts yet, so the *causes* below are generic; the *fixes* are concrete.

| Symptom | Fix |
|---|---|
| The reply starts with "Here is your file:" or wraps everything in a ```markdown fence | Reply: **"Output only the file itself — no fence, no commentary."** Then copy between the first `---` and the last ``` only. |
| The scene blocks are labelled `yaml` instead of `scene` | Change the opening fence from ```` ```yaml ```` to ```` ```scene ```` yourself, or ask for a correction. |
| The reply stops in the middle of the file | Reply: **"Continue from where you stopped, output only the missing part."** Then join the parts. If it happens repeatedly, ask for a shorter lesson (≤ 5 scenes) and resend the full prompt. |
| The AI invents object kinds, actions, or fields not in the format | Feed the validator errors to [`prompts/SCENE_CORRECTION_PROMPT.md`](../prompts/SCENE_CORRECTION_PROMPT.md) — its rule 3 forbids inventing syntax. If it repeats, start over from the generation prompt and restate the limits. |
| The AI rewrites the whole lesson while "fixing" one error | Reply: **"Smallest necessary corrections only; preserve the original."** |
| The AI says "now it is tested / verified / will render" | It cannot run anything. Ignore the claim — only the validator's exit code counts today. |
| The same error survives about five correction rounds | Stop looping: re-read [`prompts/SCENE_FORMAT_SPEC.md`](../prompts/SCENE_FORMAT_SPEC.md) for that construct — the Scene format may genuinely not support it — or regenerate from scratch. |

## 6. ◔ Planned application failures (for reference once released)

> Everything below concerns the **not-yet-released** application described in [`ROADMAP.md`](ROADMAP.md) and the build specification. You cannot encounter these today because the application does not exist yet.

| Planned symptom | Planned cause | Planned fix |
|---|---|---|
| The launcher reports missing dependencies and exits with an explanation | Manim, FFmpeg, Node.js, or (optionally) LaTeX is not installed | Run the planned `.\run.ps1 -Setup`, or install the named dependency; the planned Settings page will show dependency health. |
| Mathematical typography renders as plain text | LaTeX is not installed (it is optional) | Fine for most lessons; install LaTeX for advanced formula rendering. |
| "Port already in use" at launch | Another program occupies the chosen local port | The planned launcher verifies the port and explains the conflict; it will never kill unrelated programs. |
| A render job stays in `rendering` a long time, then fails | A very long or dense scene; the planned renderer has per-job timeouts | Split the lesson into shorter scenes and re-render; planned render jobs show honest progress and per-job logs. |
| Videos cannot be saved | The planned output folder is unavailable (moved, permission lost, disk full) | Change the output folder in the planned Settings page; free disk space. |

## 7. Safe recovery — when all else fails

1. **Keep originals.** Validate copies; save each AI correction under a new name until it passes. The validator never modifies files, so nothing you run here can damage your work.
2. **Reduce.** Copy a single ```scene block out of the lesson into its own file (with the same front matter) and validate that — the error list becomes much shorter and easier to read.
3. **Compare with a known-good file.** Any file in [`prompts/examples/`](../prompts/examples/) passes validation; differences from it are usually the answer.
4. **Regenerate deliberately.** Start again from [`prompts/SCENE_GENERATION_PROMPT.md`](../prompts/SCENE_GENERATION_PROMPT.md), adding one sentence naming the recurring problem ("every scene must use only these object kinds…").
5. **Ask better.** The correction prompt works best with the *complete* error report (`--json` output), not a paraphrase.

## 8. Where to look next

| Question | Document |
|---|---|
| Installation and setup | [INSTALLATION.md](INSTALLATION.md) |
| The lesson workflow, step by step | [USER_GUIDE.md](USER_GUIDE.md) |
| Every validation rule and error category | [`prompts/SCENE_VALIDATION_RULES.md`](../prompts/SCENE_VALIDATION_RULES.md) |
| The complete Scene format reference | [`prompts/SCENE_FORMAT_SPEC.md`](../prompts/SCENE_FORMAT_SPEC.md) |
| Validator usage and exit codes | [`tools/README.md`](../tools/README.md) |
| How AI-generated files are kept safe | [SECURITY.md](SECURITY.md) |
| What is being built next | [ROADMAP.md](ROADMAP.md) · [TESTING.md](TESTING.md) |
