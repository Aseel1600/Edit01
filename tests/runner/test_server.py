"""Focused contract tests for the bounded OpenMontage runner API."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from runner import server as runner


@pytest.fixture
def projects_root(tmp_path, monkeypatch) -> Path:
    root = tmp_path / "projects"
    root.mkdir()
    monkeypatch.setattr(runner, "PROJECTS_DIR", root)
    monkeypatch.setenv("OPENMONTAGE_RUNNER_TOKEN", "runner-test-token")
    return root


@pytest.fixture
def client(projects_root):
    return TestClient(runner.create_app())


def _headers() -> dict[str, str]:
    return {"Authorization": "Bearer runner-test-token"}


def _create(client, project_id="local-demo"):
    return client.post(
        "/api/v1/runs",
        headers=_headers(),
        json={"project_id": project_id, "title": "Local demo", "pipeline_type": "framework-smoke"},
    )


def test_create_run_initializes_fixed_canonical_project_root(client, projects_root):
    response = _create(client)
    assert response.status_code == 201
    assert response.json() == {
        "project_id": "local-demo", "status": "initialized",
        "current_stage": None, "render_id": None, "error": None,
    }
    assert (projects_root / "local-demo" / "project.json").is_file()
    assert (projects_root / "local-demo" / "artifacts").is_dir()
    assert not (projects_root / "outside").exists()


def test_auth_and_path_input_are_rejected(client):
    forbidden = client.post("/api/v1/runs", json={"project_id": "x", "title": "X", "pipeline_type": "framework-smoke"})
    assert forbidden.status_code == 401
    unsafe = _create(client, "../outside")
    assert unsafe.status_code == 422


def test_status_derives_checkpoint_then_approved_render(client, projects_root):
    assert _create(client).status_code == 201
    project = projects_root / "local-demo"
    (project / "checkpoint_research.json").write_text(json.dumps({"stage": "research", "status": "awaiting_human"}), encoding="utf-8")
    waiting = client.get("/api/v1/runs/local-demo", headers=_headers())
    assert waiting.json()["status"] == "awaiting_human"
    (project / "checkpoint_compose.json").write_text(json.dumps({"stage": "compose", "status": "completed"}), encoding="utf-8")
    (project / "renders").mkdir(exist_ok=True)
    (project / "renders" / "final.mp4").write_bytes(b"render")
    done = client.get("/api/v1/runs/local-demo", headers=_headers())
    assert done.json()["status"] == "completed"
    assert done.json()["render_id"] == "renders/final.mp4"


def test_cancel_is_cooperative_and_terminal_runs_are_not_cancelled(client, projects_root):
    assert _create(client).status_code == 201
    cancelled = client.post("/api/v1/runs/local-demo/cancel", headers=_headers())
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"
    assert (projects_root / "local-demo" / "runner_control.json").is_file()
    again = client.post("/api/v1/runs/local-demo/cancel", headers=_headers())
    assert again.status_code == 409
