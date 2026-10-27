"""The External-AI prompt generator (master prompt template assembly).

Assembles ``prompts/PROMPT_TEMPLATE.md`` from the teacher's form inputs
per the documented assembly rules (template section 3), producing both the
full prompt and the compact variant for context-limited models. The
generator embeds the *actual* Scene format template — never an invented
schema — and is provider-neutral (no ``{{#IF}}``-style AI-provider
instructions are ever added).

The application never produces an AI response itself: it produces the
prompt the teacher carries to whichever External AI they choose.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.core.config import Settings, get_settings
from app.core.errors import AppError

DEFAULT_COLORS = "midnight navy, electric violet, ivory"

_TOKEN_RE = re.compile(r"\{\{([A-Z_]+)\}\}")
_BLOCK_RE = re.compile(r"\{\{#IF ([a-z_]+)\}\}(.*?)\{\{/IF\}\}", re.DOTALL)
_RECAP_ANNOTATION = re.compile(r"^#\s*\{\{RECAP[^}]*\}\}\s*")
_PRACTICE_ANNOTATION = re.compile(r"^#\s*\{\{PRACTICE[^}]*\}\}\s*")
_COORDINATES_BRACE = re.compile(r"\{\{ASPECT_RATIO = [^}]*\}\}")

_KNOWN_TOKENS = {
    "TOPIC", "GRADE", "BRANCH", "LANGUAGE", "STYLE", "DURATION", "ASPECT_RATIO",
    "DIFFICULTY", "COLORS", "RECAP", "PRACTICE", "VOICEOVER", "ADDITIONAL",
}

# Frame ranges per aspect ratio, mirroring prompts/SCENE_FORMAT_SPEC.md section 7.1.
_FRAME_TEXT = {
    "16:9": "x \u22127\u20267, y \u22124\u20264",
    "9:16": "x \u22124\u20264, y \u22127\u20267",
    "1:1": "x \u22124.5\u20264.5, y \u22124.5\u20264.5",
}


class PromptTemplateError(AppError):  # pragma: no cover - defensive
    code = "prompt_template_error"
    status_code = 500


def load_template_body(settings: Settings | None = None) -> str:
    """Extract the prompt body from ``prompts/PROMPT_TEMPLATE.md`` section 2."""
    settings = settings or get_settings()
    path = settings.prompts_dir / "PROMPT_TEMPLATE.md"
    if not path.is_file():
        raise PromptTemplateError(
            "The prompt template file is missing from the installation.",
            detail=str(path),
        )
    text = path.read_text(encoding="utf-8")
    marker = "## 2. The template"
    if marker not in text:
        raise PromptTemplateError("The prompt template is malformed (section 2 missing).")
    tail = text.split(marker, 1)[1]
    match = re.search(r"````text\n(.*?)\n````", tail, re.DOTALL)
    if match is None:
        raise PromptTemplateError("The prompt template is malformed (template body not found).")
    return match.group(1)


@dataclass(frozen=True)
class PromptInputs:
    topic: str
    grade: str
    branch: str | None = None
    language: str = "English"
    style: str = "intuitive"
    duration: int = 5
    aspect_ratio: str = "16:9"
    difficulty: str = "standard"
    colors: str | None = None
    include_recap: bool = True
    include_practice: bool = True
    include_voiceover: bool = True
    additional: str | None = None


def _assemble_tokens(body: str, inputs: PromptInputs) -> str:
    values = {
        "TOPIC": inputs.topic,
        "GRADE": inputs.grade,
        "BRANCH": inputs.branch or "",
        "LANGUAGE": inputs.language,
        "STYLE": inputs.style,
        "DURATION": str(inputs.duration),
        "ASPECT_RATIO": inputs.aspect_ratio,
        "DIFFICULTY": inputs.difficulty,
        "COLORS": inputs.colors or DEFAULT_COLORS,
        "RECAP": "true" if inputs.include_recap else "false",
        "PRACTICE": "true" if inputs.include_practice else "false",
        "VOICEOVER": "true" if inputs.include_voiceover else "false",
        "ADDITIONAL": inputs.additional or "",
    }

    found = set(_TOKEN_RE.findall(body)) | {m[0] for m in _BLOCK_RE.findall(body)}
    unknown = found - _KNOWN_TOKENS
    if unknown:
        raise PromptTemplateError(
            "The prompt template contains unknown placeholders.",
            detail=sorted(unknown),
        )

    # Optional-sentence lines are deleted when their input is empty.
    lines = []
    for line in body.splitlines():
        token_match = _TOKEN_RE.search(line)
        if token_match and token_match.group(1) in ("BRANCH", "ADDITIONAL") and not values[token_match.group(1)]:
            continue
        lines.append(line)
    body = "\n".join(lines)

    # Conditional {{#IF x}} ... {{/IF}} blocks (documented in template section 3).
    def _resolve_block(match: re.Match[str]) -> str:
        name, inner = match.group(1), match.group(2)
        flag = values.get(name.upper(), "")
        return inner if str(flag).lower() in ("true", "1") else ""

    body = _BLOCK_RE.sub(_resolve_block, body)

    # Aspect-ratio brace expression -> concrete frame numbers.
    body = _COORDINATES_BRACE.sub(
        lambda _m: f"frame {_FRAME_TEXT.get(inputs.aspect_ratio, _FRAME_TEXT['16:9'])}", body
    )

    # Plain placeholders.
    body = _TOKEN_RE.sub(lambda m: values[m.group(1)], body)

    # Front-matter annotation comments: keep the field when included, drop both otherwise.
    out: list[str] = []
    body_lines = body.splitlines()
    i = 0
    while i < len(body_lines):
        line = body_lines[i]
        if _RECAP_ANNOTATION.search(line):
            if inputs.include_recap:
                out.append(_RECAP_ANNOTATION.sub("", line))
            i += 1
            continue
        if _PRACTICE_ANNOTATION.search(line):
            if inputs.include_practice:
                out.append(_PRACTICE_ANNOTATION.sub("", line))
                if i + 1 < len(body_lines):
                    out.append(body_lines[i + 1])
                    i += 1
            i += 1
            continue
        out.append(line)
        i += 1
    body = "\n".join(out)

    # Narration line in the scene-block reference follows the VOICEOVER flag.
    if not inputs.include_voiceover:
        body = "\n".join(
            line for line in body.splitlines() if not line.startswith('narration: "…"')
        )

    return body.strip() + "\n"


# --- compact variant -------------------------------------------------------
# Section headers that collapse to a single line (template section 3.4).
_COMPRESS: dict[str, tuple[str, str]] = {
    "SUPPORTED OBJECT KINDS": (
        "kinds: text, formula, equation, point, segment, line, ray, angle, triangle, "
        "circle, polygon, square, rectangle, vector, axes, function_graph, area_fill, "
        "number_line, fraction — required params are marked with * in the front-matter "
        "and scene examples above; do not invent params",
        "SUPPORTED ACTIONS",
    ),
    "SUPPORTED ACTIONS": (
        "actions: create, write, fade_in, fade_out, transform, move, rotate, scale, "
        "indicate, circumscribe, draw_border, recolor, wait, arrange, reveal — every "
        "action except wait needs a target; unknown fields on an action are rejected",
        "COLORS (",
    ),
    "COLORS (": (
        "colors: navy, violet, ivory, white, black, gray, red, green, blue, amber, teal, "
        "pink (palette names or #RRGGBB — nothing else)",
        "COORDINATES",
    ),
    "MATH EXPRESSION GRAMMAR": (
        "math expression grammar (function_graph, area_fill, verification only): numbers, "
        "x, parentheses, + - * / ** (^ allowed as **), constants pi and e, and ONLY "
        "sin cos tan asin acos atan sqrt abs ln log log10 exp floor ceil round min max",
        "LIMITS",
    ),
}

_KEEP_BUILDS = ("1. ", "3. ", "6. ")


def build_compact(full_prompt: str) -> str:
    """Compress the assembled prompt for context-limited models (template §3.4)."""
    lines = full_prompt.splitlines()
    out: list[str] = []
    i = 0
    in_build = False
    while i < len(lines):
        line = lines[i]

        if line.startswith("HOW TO BUILD THE LESSON"):
            in_build = True
            out.append(line)
            i += 1
            continue
        if in_build:
            if line.startswith("OUTPUT FORMAT"):
                in_build = False
            elif not line.startswith(_KEEP_BUILDS) and re.match(r"^\d\. ", line):
                i += 1
                continue

        compressed = next(
            ((replacement, stop) for header, (replacement, stop) in _COMPRESS.items()
             if line.startswith(header)),
            None,
        )
        if compressed:
            replacement, stop = compressed
            out.append(replacement)
            i += 1
            while i < len(lines) and not lines[i].startswith(stop):
                i += 1
            continue

        out.append(line)
        i += 1

    compact = "\n".join(out)
    # Collapse runs of blank lines created by removed content.
    compact = re.sub(r"\n{3,}", "\n\n", compact)
    return compact.strip() + "\n"


def generate_prompt(inputs: PromptInputs, settings: Settings | None = None) -> dict[str, object]:
    """Assemble the full and compact prompts for the given teacher inputs."""
    settings = settings or get_settings()
    body = load_template_body(settings)
    full = _assemble_tokens(body, inputs)
    compact = build_compact(full)
    slug = re.sub(r"[^a-z0-9]+", "-", inputs.topic.lower()).strip("-")[:40] or "lesson"
    return {
        "prompt": full,
        "compact_prompt": compact,
        "filename": f"mathmotion-prompt-{slug}.txt",
        "char_count": len(full),
        "compact_char_count": len(compact),
        "compact_reduced_percent": round(100.0 * (len(full) - len(compact)) / max(1, len(full)), 1),
    }
