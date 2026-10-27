"""Parser tests: front-matter split, safe YAML, scene blocks, line numbers."""

from __future__ import annotations

from app.parser.markdown import (
    MAX_FILE_BYTES,
    check_size,
    decode_bytes,
    find_line,
    parse_markdown,
    split_front_matter,
)


def test_split_front_matter_happy_path():
    text = "---\nschema_version: '1.0'\n---\n\n# Title\n"
    fm, body, delim, issue = split_front_matter(text)
    assert issue is None
    assert "schema_version" in fm
    assert body.startswith("\n# Title")
    assert delim == 3


def test_split_front_matter_missing_opening():
    fm, _body, _delim, issue = split_front_matter("# no front matter\n")
    assert fm is None
    assert issue is not None
    assert issue.category == "missing_front_matter"
    assert issue.line == 1


def test_split_front_matter_missing_closing():
    fm, _body, _delim, issue = split_front_matter("---\nlesson: x\n")
    assert fm is None
    assert issue is not None
    assert issue.category == "missing_front_matter"


def test_parse_markdown_extracts_blocks_and_prose():
    text = (
        "---\nschema_version: '1.0'\nlesson:\n  title: T\n---\n\n"
        "# Heading\n\n```scene\nid: s1\ntitle: One\ntype: intro\n```\n\nprose line\n"
    )
    parsed = parse_markdown(text)
    assert parsed.front_matter is not None
    assert len(parsed.blocks) == 1
    assert parsed.blocks[0].doc["id"] == "s1"
    assert parsed.blocks[0].start_line == 9
    assert "prose line" in parsed.prose


def test_parse_markdown_bad_yaml_reports_line():
    text = "---\nschema_version: '1.0'\n---\n\n```scene\nid: [unclosed\n```\n"
    parsed = parse_markdown(text)
    assert any(i.category == "yaml_syntax" for i in parsed.issues)
    yaml_issue = next(i for i in parsed.issues if i.category == "yaml_syntax")
    assert yaml_issue.line is not None and yaml_issue.line >= 5


def test_parse_markdown_non_mapping_block():
    text = "---\nschema_version: '1.0'\n---\n\n```scene\n- just\n- a list\n```\n"
    parsed = parse_markdown(text)
    assert parsed.blocks[0].doc is None
    assert any(i.category == "schema" for i in parsed.issues)


def test_parse_markdown_unterminated_block():
    text = "---\nschema_version: '1.0'\n---\n\n```scene\nid: s1\n"
    parsed = parse_markdown(text)
    assert any("unterminated" in i.message for i in parsed.issues)


def test_decode_bytes_utf8_and_bom():
    text, issue = decode_bytes("héllo".encode())
    assert issue is None and text == "héllo"
    text, issue = decode_bytes(b"\xef\xbb\xbfh\xc3\xa9llo")
    assert issue is None and text == "héllo"


def test_decode_bytes_invalid_utf8():
    text, issue = decode_bytes(b"\xff\xfe\x00bad")
    assert text is None
    assert issue is not None and issue.category == "encoding"


def test_check_size_boundaries():
    assert check_size(MAX_FILE_BYTES) is None
    issue = check_size(MAX_FILE_BYTES + 1)
    assert issue is not None and issue.category == "file_too_large"


def test_find_line_locates_fragment():
    src = "id: s1\ntitle: Opening\nobjects:\n  - id: caption\n"
    assert find_line(src, 10, "title:") == 11
    assert find_line(src, 10, "caption") == 13
    assert find_line(src, 10, "missing-key") is None
