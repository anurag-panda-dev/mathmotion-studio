"""Prompt generator tests: template assembly, token substitution, compact variant."""

from __future__ import annotations

from app.services.prompt_generator import (
    PromptInputs,
    build_compact,
    generate_prompt,
    load_template_body,
)


def _inputs(**overrides) -> PromptInputs:
    base = dict(topic="Quadratic functions", grade="9", branch="Algebra")
    base.update(overrides)
    return PromptInputs(**base)


def test_template_body_loads(settings):
    body = load_template_body(settings)
    assert "{{TOPIC}}" in body
    assert "SUPPORTED OBJECT KINDS" in body or "object" in body.lower()


def test_generate_prompt_substitutes_tokens(settings):
    out = generate_prompt(_inputs(), settings)
    prompt = out["prompt"]
    assert "Quadratic functions" in prompt
    assert "Algebra" in prompt
    assert "{{TOPIC}}" not in prompt
    assert "{{GRADE}}" not in prompt


def test_generate_prompt_filename_is_safe(settings):
    out = generate_prompt(_inputs(topic="Ratio & proportion: the whole story!"), settings)
    name = out["filename"]
    assert name.startswith("mathmotion-prompt-")
    assert name.endswith(".txt")
    assert all(c.isalnum() or c in "-_." for c in name)


def test_compact_is_shorter_and_kept_structure(settings):
    out = generate_prompt(_inputs(), settings)
    full, compact = out["prompt"], out["compact_prompt"]
    assert len(compact) < len(full)
    assert out["compact_reduced_percent"] > 0
    # Section 3.4 keeps build steps 1, 3, 6 and the output format.
    assert "HOW TO BUILD THE LESSON" in compact
    assert "OUTPUT FORMAT" in compact


def test_optional_blocks_follow_flags(settings):
    without = generate_prompt(
        _inputs(include_recap=False, include_practice=False, include_voiceover=False),
        settings,
    )
    with_all = generate_prompt(
        _inputs(include_recap=True, include_practice=True, include_voiceover=True),
        settings,
    )
    assert len(with_all["prompt"]) > len(without["prompt"])


def test_branch_omitted_when_absent(settings):
    out = generate_prompt(_inputs(branch=None), settings)
    assert "Algebra" not in out["prompt"]


def test_prompt_output_contract_anti_wrapper(settings):
    """The copied prompt must pin the two wrapper failure modes from the field.

    ``prompts/AI_COMPATIBILITY.md`` section 2 documents what external AIs
    actually do: wrap the file in an outer fence or prepend commentary. The
    prompt's final lines (what the model reads last - strongest position)
    state the mechanical rule: first line ``---``, last line the closing
    fence, no wrapper. Both the full and compact variants must carry it.
    """
    out = generate_prompt(_inputs(), settings)
    for prompt in (out["prompt"], out["compact_prompt"]):
        assert "The first line of your reply must be exactly ---" in prompt
        assert "do not wrap it in ```markdown or any other fence" in prompt
        # The rule must be the LAST line: recency is what models obey.
        last = prompt.strip().splitlines()[-1]
        assert last.startswith("The first line of your reply must be exactly ---")


def test_prompt_animation_quality_section(settings):
    """The prompt asks for animated lessons, not static slideshows."""
    out = generate_prompt(_inputs(), settings)
    for prompt in (out["prompt"], out["compact_prompt"]):
        assert "ANIMATION QUALITY" in prompt
        assert "Progressive disclosure" in prompt
        assert "No static slides" in prompt
        assert "Show change, not only state" in prompt
        assert "Pace to the voice" in prompt


def test_prompt_language_written_as_bcp47_code(settings):
    """Front matter asks for the BCP-47 code, never the full name.

    Field report: generated scene.md wrote ``language: English``. The
    front-matter example must print a literal code (``en``) with a
    conversion rule - it must not substitute the teacher's raw value
    there, because printing the raw value is exactly what previously
    produced output that failed validation (docs/CHANGELOG.md). Both
    the full and compact variants must carry the rule.
    """
    out = generate_prompt(_inputs(), settings)
    for prompt in (out["prompt"], out["compact_prompt"]):
        assert 'language: "en"' in prompt
        assert 'language: "English"' not in prompt
        assert "BCP-47 code of en" in prompt
        assert "never the full name" in prompt


def test_prompt_language_converts_teacher_full_name(settings):
    """A teacher who types ``Bengali`` still gets code output instructions.

    The teacher's words stay in the requirements (they guide narration),
    while the front-matter example remains the literal code and names the
    teacher's language in the conversion rule.
    """
    out = generate_prompt(_inputs(language="Bengali"), settings)
    for prompt in (out["prompt"], out["compact_prompt"]):
        assert "Bengali" in prompt
        assert 'language: "en"' in prompt
        assert "BCP-47 code of Bengali" in prompt
        assert "Bengali → bn" in prompt
        assert 'language: "Bengali"' not in prompt


def test_build_compact_collapses_reference_sections():
    full = (
        "SUPPORTED OBJECT KINDS\n"
        "- text: a line of text\n- formula: LaTeX\n"
        "SUPPORTED ACTIONS\n- create\n- write\n"
        "COLORS (palette)\n- navy\n- violet\n"
        "MATH EXPRESSION GRAMMAR\n- numbers\n"
        "COORDINATES\n- frame\n"
    )
    compact = build_compact(full)
    assert "kinds: text, formula" in compact
    assert "actions: create, write" in compact
    assert "- text: a line of text" not in compact
    assert "COORDINATES" in compact
