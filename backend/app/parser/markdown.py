"""Safe ``scene.md`` parser: front matter split, safe YAML, scene blocks.

Mirrors the parsing stages of the reference validator
(``tools/validate_scene.py``) byte for byte in behavior, including line
numbering, so reports from the application and the CLI tool line up.

No ``yaml.load``: only ``yaml.safe_load`` — a scene.md file can never
construct a Python object (docs/SECURITY.md section 3).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import yaml

from app.validation.issues import Issue

MAX_FILE_BYTES = 512 * 1024


def check_size(nbytes: int) -> Issue | None:
    if nbytes > MAX_FILE_BYTES:
        return Issue(
            "error",
            "file_too_large",
            f"file is {nbytes} bytes; limit is {MAX_FILE_BYTES} bytes",
            suggestion="Split the lesson into smaller scenes or remove unused content.",
        )
    return None


def decode_bytes(raw: bytes) -> tuple[str | None, Issue | None]:
    """Decode upload bytes as UTF-8 with BOM tolerance."""
    try:
        return raw.decode("utf-8-sig"), None
    except UnicodeDecodeError as exc:
        return None, Issue(
            "error",
            "encoding",
            f"file is not valid UTF-8: {exc}",
            suggestion="Re-save the file as UTF-8.",
        )


@dataclass
class SceneBlockSource:
    """One fenced ```scene block and where it lives in the file."""

    doc: dict | None
    source: str
    start_line: int  # 1-based line of the opening fence
    yaml_error: Issue | None = None


@dataclass
class ParsedFile:
    text: str
    front_matter: dict | None = None
    front_matter_end_line: int = 0  # line number of the closing ---
    prose: str = ""
    blocks: list[SceneBlockSource] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)

    @property
    def schema_version(self) -> str | None:
        if isinstance(self.front_matter, dict):
            version = self.front_matter.get("schema_version")
            return str(version) if version is not None else None
        return None


def split_front_matter(text: str) -> tuple[str | None, str, int, Issue | None]:
    """Return (front-matter YAML source, body, closing-delim line, issue)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text, 0, Issue(
            "error",
            "missing_front_matter",
            "file must start with YAML front matter delimited by '---'",
            line=1,
            suggestion="Ask the AI to produce the file with '---' on the first line.",
        )
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None, "", 0, Issue(
            "error",
            "missing_front_matter",
            "closing '---' delimiter of the front matter is missing",
            suggestion="Ask the AI to close the front matter block.",
        )
    fm_src = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1:])
    return fm_src, body, end + 1, None  # end+1 is the 1-based line of `---`


def parse_scene_blocks(
    body: str, body_start_line: int
) -> tuple[list[SceneBlockSource], list[Issue], str]:
    """Extract fenced scene blocks and teacher-facing prose from the body.

    ``body_start_line`` is the 1-based line number of the first body line.
    Returns ``(blocks, issues, prose)``.
    """
    blocks: list[SceneBlockSource] = []
    issues: list[Issue] = []
    in_block = False
    buf: list[str] = []
    start_line = 0
    prose_lines: list[str] = []

    for i, line in enumerate(body.splitlines(), start=body_start_line):
        stripped = line.strip()
        if not in_block and stripped.startswith("```scene"):
            in_block, buf, start_line = True, [], i
            continue
        if in_block and stripped == "```":
            in_block = False
            source = "\n".join(buf)
            try:
                doc = yaml.safe_load(source)
            except yaml.YAMLError as exc:
                mark = getattr(exc, "problem_mark", None)
                line_no = (start_line + 1 + mark.line) if mark else start_line + 1
                issues.append(
                    Issue(
                        "error",
                        "yaml_syntax",
                        f"scene block is not valid YAML: {getattr(exc, 'problem', exc)}",
                        line=line_no,
                        suggestion="Check quoting, indentation, and colons inside strings.",
                    )
                )
                blocks.append(SceneBlockSource(None, source, start_line, issues[-1]))
                continue
            if not isinstance(doc, dict):
                issue = Issue(
                    "error",
                    "schema",
                    "scene block must be a YAML mapping",
                    line=start_line + 1,
                    suggestion="A scene block needs keys such as id, title, type.",
                )
                issues.append(issue)
                blocks.append(SceneBlockSource(None, source, start_line, issue))
                continue
            blocks.append(SceneBlockSource(doc, source, start_line))
            continue
        if in_block:
            buf.append(line)
        else:
            prose_lines.append(line)

    if in_block:
        issues.append(
            Issue(
                "error",
                "yaml_syntax",
                "unterminated ```scene block",
                line=start_line,
                suggestion="Every ```scene block must be closed with ```.",
            )
        )
    prose = "\n".join(prose_lines).strip()
    return blocks, issues, prose


def find_line(block_src: str, block_start_line: int, needle: str) -> int | None:
    """Best-effort line lookup for a key/value fragment inside a block."""
    for i, line in enumerate(block_src.splitlines()):
        if needle in line:
            return block_start_line + i
    return None


def parse_markdown(text: str) -> ParsedFile:
    """Run stages 2-4 (encoding excluded: text is already decoded)."""
    parsed = ParsedFile(text=text)

    fm_src, body, delim_line, issue = split_front_matter(text)
    if issue is not None:
        parsed.issues.append(issue)
        return parsed
    assert fm_src is not None
    parsed.front_matter_end_line = delim_line

    try:
        meta = yaml.safe_load(fm_src) or {}
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        parsed.issues.append(
            Issue(
                "error",
                "yaml_syntax",
                f"front matter is not valid YAML: {getattr(exc, 'problem', exc)}",
                line=(mark.line + 2) if mark else 2,
                suggestion="Check quoting and indentation.",
            )
        )
        return parsed

    if not isinstance(meta, dict):
        parsed.issues.append(
            Issue(
                "error",
                "yaml_syntax",
                "front matter must be a YAML mapping of keys such as schema_version and lesson",
                line=2,
            )
        )
        return parsed

    parsed.front_matter = meta
    body_start = delim_line + 1
    blocks, block_issues, prose = parse_scene_blocks(body, body_start)
    parsed.blocks = blocks
    parsed.issues.extend(block_issues)
    parsed.prose = prose
    return parsed
