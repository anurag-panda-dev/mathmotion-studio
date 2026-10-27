# AI compatibility guide

How to use the MathMotion Studio prompts with different **external AI** tools and get a `scene.md` file the application accepts.

> **Status:** Provider-neutral guidance. No specific external AI tool has been verified against these prompts yet — behavior notes below are generic and honest about that. Anything provider-specific must be **tested and recorded here** before being presented as fact (this repository has no `CONTRIBUTING.md` yet; tested findings belong in this file).

## 1. Which tools work

Anything that can receive a long text prompt and return long Markdown text:

| Category | Typical fit | Things to watch |
|---|---|---|
| Web chat assistants | Good for lessons up to ~6 scenes | Output length limits may truncate long files (§4). |
| Desktop / IDE assistants | Good; can iterate quickly with the correction loop | May try to "explain" the file instead of outputting it — reinforce the final output line. |
| Local models (offline) | Quality varies with model size | Smaller models break YAML quoting more often; validate every time. |
| Long-context models | Best fit for 8+ scene lessons | Still validate; length does not imply correctness. |

The application itself never calls any AI service: no API key, account, or cloud connection is part of MathMotion Studio ([`docs/PRIVACY.md`](../docs/PRIVACY.md)).

## 2. Getting a clean file out

The single most common failure is the AI wrapping the file in a ```markdown fence or adding commentary. The prompts demand a bare file; still, check the response:

1. The first characters of the response should be `---` (the front matter opening). If you see `Here is your scene.md:` or a fence, reply: *"Output only the file itself — no fence, no commentary."*
2. The last characters should be the closing ``` of the final scene block.
3. Copy **everything** between those points.

### Saving as `scene.md`

1. Create a new plain-text file next to your lessons (e.g. `Documents\MathMotion\my-lesson.scene.md` — any `.md` name works; the app accepts `.md`).
2. Paste the content, save with **UTF-8** encoding (Notepad's default; in VS Code the encoding indicator in the status bar says `UTF-8`).
3. Keep the name simple and readable; avoid characters like `: * ? " < > |`.

### Markdown wrappers that are *not* part of the format

| Symptom | Fix |
|---|---|
| Outer ``` or ```markdown fence around the whole file | Delete the first and last fence lines. |
| `scene` blocks written as `yaml` fences | Replace the info string: ` ```yaml ` → ` ```scene `. |
| Curly quotes `“ ”` in strings | Valid YAML as long as the string is quoted — no change needed. |
| Smart dashes or ellipses in narration | Fine; but avoid them inside `expression:` values. |

## 3. Validate every time

```powershell
python tools\validate_scene.py scene.md
```

- Exit `0` → import it (or render once the app is available).
- Exit `1` → the report lists category, scene, field, line, message, suggestion. Feed it verbatim to [`SCENE_CORRECTION_PROMPT.md`](SCENE_CORRECTION_PROMPT.md).

Validation proves the file is well-formed, not that the mathematics is right — mathematical checks come from `verification` assertions, reported separately ([`SCENE_VALIDATION_RULES.md`](SCENE_VALIDATION_RULES.md) §4).

## 4. Recovering from common failures

| Failure | What to do |
|---|---|
| Response cut off mid-file | Reply: *"Continue from where you stopped, output only the missing part."* Then join without adding anything — or ask for a shorter lesson (≤5 scenes) and re-send the full prompt. |
| File parses but a scene fails | Use the correction prompt with the exact error report. |
| AI invented an object kind or action | Correction prompt rule 3 covers this; if it repeats, start over with [`SCENE_GENERATION_PROMPT.md`](SCENE_GENERATION_PROMPT.md) and state the limits line once more. |
| AI rewrites the whole lesson differently | Remind it: *"Smallest necessary corrections only; preserve the original."* |
| AI claims "now tested/verified" | It cannot test anything. Ignore the claim; only the validator's exit code and (later) the app's verification report count. |
| Repeated identical failures | Re-read [`SCENE_FORMAT_SPEC.md`](SCENE_FORMAT_SPEC.md) for that construct; the format may genuinely not support it (supported-feature table in spec §6). |

## 5. Tips per workflow

- **First lesson on a new tool:** start with the canonical example ([`examples/pythagorean-theorem.md`](examples/pythagorean-theorem.md)) as a style reference — paste it after the prompt as "Here is a known-valid file matching your output format." This is legitimate: it demonstrates format, not the lesson content.
- **Small-context models:** use the compact variant described in [`PROMPT_TEMPLATE.md`](PROMPT_TEMPLATE.md) §3.4.
- **Non-English lessons:** set the language input; check labels and narration language in the returned file — models sometimes revert to English mid-file.
- **Reuse:** once a lesson validates, keep it — the application stores lessons locally and re-renders without calling an AI again (planned behavior, [`docs/ROADMAP.md`](../docs/ROADMAP.md)).

## 6. Reporting provider findings

If you verify tool-specific behavior (truncation limits, wrapper habits, reliable output modes), document: tool name, model/version, date, prompt variant (full/compact), result, and any required extra instruction. No such records exist yet — this section stays honest until they do.
