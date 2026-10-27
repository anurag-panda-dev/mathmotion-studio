"""End-to-end API tests over a real app instance (client fixture)."""

from __future__ import annotations


def test_health_reports_honest_status(client):
    body = client.get("/api/v1/health").json()
    assert body["status"] in ("ok", "degraded")
    assert body["scene_format_version"] == "1.0"
    names = {d["name"] for d in body["dependencies"]}
    assert {"manim", "ffmpeg", "latex"} <= names


def test_diagnostics_counts_jobs(client):
    body = client.get("/api/v1/diagnostics").json()
    assert body["render_concurrency"] >= 1
    assert "job_counts" in body
    assert body["storage"]["total_bytes"] >= 0


def test_validate_scene_accepts_valid(client, valid_markdown):
    r = client.post(
        "/api/v1/scenes/validate",
        json={"markdown": valid_markdown, "filename": "pythagorean-theorem.md"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["valid"] is True
    assert body["errors"] == []
    assert body["summary"]["title"] == "The Pythagorean Theorem"


def test_validate_scene_reports_errors_with_line_and_category(client):
    bad = "---\nschema_version: '1.0'\n---\n\n```scene\nid: s1\ntitle: T\ntype: bogus\n```\n"
    r = client.post("/api/v1/scenes/validate", json={"markdown": bad})
    assert r.status_code == 200
    body = r.json()
    assert body["valid"] is False
    assert body["errors"], "errors must be reported"
    first = body["errors"][0]
    assert first["severity"] == "error"
    assert first["message"]


def test_validate_rejects_oversized_paste(client, settings):
    huge = "x" * (settings.max_paste_chars + 1)
    r = client.post("/api/v1/scenes/validate", json={"markdown": huge})
    assert r.status_code == 413


def test_import_creates_lesson_and_detail_round_trips(client, valid_markdown):
    r = client.post(
        "/api/v1/lessons",
        json={"markdown": valid_markdown, "filename": "pythagorean-theorem.md"},
    )
    assert r.status_code == 201
    lesson_id = r.json()["lesson_id"]

    detail = client.get(f"/api/v1/lessons/{lesson_id}").json()
    assert detail["title"] == "The Pythagorean Theorem"
    assert detail["markdown"] == valid_markdown
    assert detail["report"]["valid"] is True
    assert len(detail["summary"]["scenes"]) == 4

    listing = client.get("/api/v1/lessons").json()
    assert any(item["lesson_id"] == lesson_id for item in listing)


def test_import_rejects_traversal_filename(client, valid_markdown):
    r = client.post(
        "/api/v1/lessons",
        json={"markdown": valid_markdown, "filename": "../../etc/passwd"},
    )
    assert r.status_code == 403


def test_update_source_revalidates(client, valid_markdown):
    lesson_id = client.post(
        "/api/v1/lessons", json={"markdown": valid_markdown, "filename": "a.md"}
    ).json()["lesson_id"]
    broken = "---\nschema_version: '1.0'\n---\n\n```scene\nid: s1\n```\n"
    r = client.patch(f"/api/v1/lessons/{lesson_id}/source", json={"markdown": broken})
    assert r.status_code == 200
    assert r.json()["report"]["valid"] is False


def test_delete_lesson_removes_it(client, valid_markdown):
    lesson_id = client.post(
        "/api/v1/lessons", json={"markdown": valid_markdown, "filename": "a.md"}
    ).json()["lesson_id"]
    assert client.delete(f"/api/v1/lessons/{lesson_id}").status_code == 204
    assert client.get(f"/api/v1/lessons/{lesson_id}").status_code == 404


def test_reference_schema_lists_kinds_and_actions(client):
    body = client.get("/api/v1/reference/schema").json()
    assert "function_graph" in body["object_kinds"]
    assert "reveal" in body["actions"]
    assert "16:9" in body["frames"]
    assert body["lesson_schema"]["$schema"] or body["lesson_schema"]["type"]


def test_reference_examples_lists_and_serves(client):
    listing = client.get("/api/v1/reference/examples").json()["examples"]
    assert listing, "examples must be listed"
    first = listing[0]
    content = client.get(f"/api/v1/reference/examples/{first['name']}").json()
    assert content["markdown"].startswith("---")


def test_reference_example_rejects_traversal(client):
    assert client.get("/api/v1/reference/examples/..%2Fsecret.md").status_code in (403, 404)


def test_unknown_api_path_returns_json_404_not_spa(client):
    """Unknown /api/ paths must be JSON 404s even when a built frontend's
    SPA catch-all is mounted (it must never swallow API paths)."""
    r = client.get("/api/v1/does-not-exist")
    assert r.status_code == 404
    assert "application/json" in r.headers["content-type"]


def test_prompt_generation(client):
    r = client.post(
        "/api/v1/prompt",
        json={"topic": "Pythagorean theorem", "grade": "8", "style": "step-by-step"},
    )
    assert r.status_code == 200
    body = r.json()
    assert "Pythagorean theorem" in body["prompt"]
    assert body["char_count"] == len(body["prompt"])
    assert body["compact_char_count"] <= body["char_count"]


def test_state_changing_request_from_foreign_origin_is_blocked(client, valid_markdown):
    r = client.post(
        "/api/v1/lessons",
        json={"markdown": valid_markdown, "filename": "a.md"},
        headers={"origin": "http://evil.example.com"},
    )
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "forbidden_origin"


def test_same_origin_state_change_is_allowed(client, valid_markdown):
    r = client.post(
        "/api/v1/lessons",
        json={"markdown": valid_markdown, "filename": "a.md"},
        headers={"origin": "http://127.0.0.1:8765"},
    )
    assert r.status_code == 201


def test_settings_round_trip_and_validation(client):
    r = client.get("/api/v1/settings")
    assert r.status_code == 200
    patched = client.patch("/api/v1/settings", json={"default_quality": "preview"})
    assert patched.status_code == 200
    assert patched.json()["default_quality"] == "preview"
    bad = client.patch("/api/v1/settings", json={"default_quality": "ultra"})
    assert bad.status_code == 422


def test_open_output_reports_honestly(client):
    body = client.post("/api/v1/settings/open-output").json()
    assert "opened" in body and "path" in body


def test_root_status_page_or_built_frontend(client, settings):
    """Root responds honestly in both states: status JSON without a build,
    the built index.html once frontend/dist exists."""
    r = client.get("/")
    assert r.status_code == 200
    if (settings.frontend_dist / "index.html").is_file():
        assert "text/html" in r.headers["content-type"]
        assert "<!doctype html" in r.text.lower()
    else:
        assert r.json()["status"] == "frontend_not_built"


def test_request_id_header_is_echoed(client):
    r = client.get("/api/v1/health", headers={"X-Request-ID": "test-123"})
    assert r.headers.get("X-Request-ID") == "test-123"


def test_error_envelope_shape(client):
    r = client.get("/api/v1/lessons/does-not-exist")
    assert r.status_code == 404
    err = r.json()["error"]
    assert err["code"] == "not_found"
    assert err["request_id"]
    assert "traceback" not in r.text.lower()
