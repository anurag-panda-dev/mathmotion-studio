"""Security helper tests: safe paths, slugs, origin checks, rate limiting."""

from __future__ import annotations

import pytest

from app.core.errors import ForbiddenError, RateLimitError
from app.core.security import RateLimiter, is_under, safe_filename, safe_join, safe_slug


def test_safe_slug_normalizes():
    assert safe_slug("The Pythagorean Theorem!") == "the-pythagorean-theorem"
    assert safe_slug("a/b\\c:d") == "a-b-c-d"
    assert safe_slug("") == "lesson"
    assert safe_slug("!!!") == "lesson"
    assert len(safe_slug("x" * 500)) <= 60


def test_safe_filename_rejects_traversal_and_separators():
    assert safe_filename("lesson.md") == "lesson.md"
    for bad in ("../x.md", "a/b.md", "a\\b.md", "C:x.md", "", "x" * 300, ".md"):
        with pytest.raises(ForbiddenError):
            safe_filename(bad)


def test_safe_join_confines_to_root(tmp_path):
    root = tmp_path / "out"
    root.mkdir()
    assert is_under(safe_join(root, "a.mp4"), root)
    for bad in ("../escape.mp4", "a/../../escape.mp4", "/etc/passwd", "C:\\windows"):
        with pytest.raises(ForbiddenError):
            safe_join(root, bad)


def test_safe_join_allows_nested_safe_parts(tmp_path):
    root = tmp_path / "jobs"
    root.mkdir()
    joined = safe_join(root, "job123", "media")
    assert is_under(joined, root)


def test_is_under_rejects_outside(tmp_path):
    inside = tmp_path / "a" / "b"
    inside.mkdir(parents=True)
    assert is_under(inside, tmp_path)
    assert not is_under(tmp_path.parent, tmp_path)


def test_rate_limiter_enforces_window():
    limiter = RateLimiter(max_requests=2, window_s=60)
    limiter.check()
    limiter.check()
    with pytest.raises(RateLimitError):
        limiter.check()


def test_rate_limiter_window_expires():
    import time as _time

    limiter = RateLimiter(max_requests=1, window_s=0)
    limiter.check()
    # Sleep well past this platform's clock granularity: time.monotonic() is
    # GetTickCount64() here (15.625 ms resolution), so a 10 ms sleep can read
    # a zero delta ~1/3 of the time and make expiry look failed. 50 ms is
    # three ticks - always observable.
    _time.sleep(0.05)
    limiter.check()  # window already elapsed


def test_publish_output_names_safely(settings, tmp_path):
    from app.storage.files import publish_output

    source = tmp_path / "raw.mp4"
    source.write_bytes(b"\x00" * 128)
    out_dir = settings.default_output_dir
    target = publish_output(settings, out_dir, "Lesson: With / Unsafe? Chars!", "job12345678", source)
    assert target.parent == out_dir.resolve()
    assert all(c.isalnum() or c in "-_." for c in target.name)
    assert target.stat().st_size == 128


def test_publish_output_rejects_empty_file(settings, tmp_path):
    from app.storage.files import publish_output

    source = tmp_path / "empty.mp4"
    source.write_bytes(b"")
    with pytest.raises(ValueError):
        publish_output(settings, settings.default_output_dir, "T", "job1", source)
