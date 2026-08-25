"""Small, deliberately bounded OpenMontage runner service.

The runner is an adapter for the Hub, not a second orchestrator.  It only
creates canonical project workspaces, derives their state from checkpoints and
approved renders, and records a cooperative cancellation request.  Pipeline
agents remain responsible for progressing work through the normal checkpoint
and approval protocol.
"""

from __future__ import annotations

import hmac
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from lib.checkpoint import get_pipeline_stages, init_project
from lib.paths import PROJECTS_DIR

API_PREFIX = "/api/v1"
PROJECT_ID_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62})$")
CONTROL_FILENAME = "runner_control.json"
APPROVED_RENDER_NAMES = ("final.mp4", "final.webm", "final.mov")


class CreateRunRequest(BaseModel):
    """The only information the runner accepts to initialize a run."""

    project_id: str = Field(min_length=1, max_length=63)
    title: str = Field(min_length=1, max_length=240)
    pipeline_type: str = Field(min_length=1, max_length=80)
    style_playbook: str | None = Field(default=None, max_length=80)


class RunResponse(BaseModel):
    project_id: str
    status: str
    current_stage: str | None = None
    render_id: str | None = None
    error: str | None = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _token() -> str:
    token = os.environ.get("OPENMONTAGE_RUNNER_TOKEN", "")
    if not token:
        raise HTTPException(status_code=503, detail="runner authentication is not configured")
    return token


def require_auth(authorization: str | None = Header(default=None)) -> None:
    """Require a bearer token without exposing token content in errors/logs."""

    expected = _token()
    scheme, _, supplied = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not supplied or not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="unauthorized")


def _validate_project_id(project_id: str) -> str:
    if not PROJECT_ID_RE.fullmatch(project_id):
        raise HTTPException(
            status_code=422,
            detail="project_id must be lowercase kebab-case (1-63 characters)",
        )
    return project_id


def _project_dir(project_id: str, *, require_exists: bool = True) -> Path:
    _validate_project_id(project_id)
    root = PROJECTS_DIR.resolve()
    path = (root / project_id).resolve()
    if path.parent != root:
        # Defensive even though validation makes traversal impossible.
        raise HTTPException(status_code=400, detail="invalid project id")
    if require_exists and not path.is_dir():
        raise HTTPException(status_code=404, detail="unknown project")
    return path


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeError):
        return None
    return value if isinstance(value, dict) else None


def _control_path(project_dir: Path) -> Path:
    return project_dir / CONTROL_FILENAME


def _is_cancelled(project_dir: Path) -> bool:
    control = _read_json(_control_path(project_dir))
    return bool(control and control.get("cancel_requested_at"))


def _latest_checkpoint(project_dir: Path) -> dict[str, Any] | None:
    paths = sorted(project_dir.glob("checkpoint_*.json"), key=lambda p: p.stat().st_mtime_ns, reverse=True)
    for path in paths:
        checkpoint = _read_json(path)
        if checkpoint:
            return checkpoint
    return None


def _approved_render(project_dir: Path, checkpoint: dict[str, Any] | None) -> str | None:
    """Return a project-relative identifier only after compose/publish completed."""

    completed = {
        p.stem.removeprefix("checkpoint_")
        for p in project_dir.glob("checkpoint_*.json")
        if (_read_json(p) or {}).get("status") == "completed"
    }
    if not {"compose", "publish"}.intersection(completed):
        return None
    for name in APPROVED_RENDER_NAMES:
        candidate = project_dir / "renders" / name
        if candidate.is_file():
            return f"renders/{name}"
    return None


def derive_status(project_dir: Path) -> RunResponse:
    """Derive normalized state from canonical checkpoint/render files only."""

    marker = _read_json(project_dir / "project.json") or {}
    checkpoint = _latest_checkpoint(project_dir)
    current_stage = checkpoint.get("stage") if checkpoint else None
    checkpoint_status = checkpoint.get("status") if checkpoint else None
    render_id = _approved_render(project_dir, checkpoint)

    if _is_cancelled(project_dir):
        run_status = "cancelled"
    elif render_id:
        run_status = "completed"
    elif checkpoint_status in {"failed", "error"}:
        run_status = "failed"
    elif checkpoint_status == "awaiting_human":
        run_status = "awaiting_human"
    elif checkpoint_status == "in_progress":
        run_status = "in_progress"
    elif checkpoint_status == "completed":
        pipeline_type = marker.get("pipeline_type")
        stages = get_pipeline_stages(pipeline_type) if isinstance(pipeline_type, str) else []
        completed = {
            p.stem.removeprefix("checkpoint_")
            for p in project_dir.glob("checkpoint_*.json")
            if (_read_json(p) or {}).get("status") == "completed"
        }
        run_status = "completed" if stages and set(stages).issubset(completed) else "ready"
    else:
        run_status = "initialized"

    error = checkpoint.get("error") if checkpoint and isinstance(checkpoint.get("error"), str) else None
    return RunResponse(
        project_id=str(marker.get("project_id") or project_dir.name),
        status=run_status,
        current_stage=current_stage if isinstance(current_stage, str) else None,
        render_id=render_id,
        error=error,
    )


def _write_cancel_request(project_dir: Path) -> None:
    """Atomically record cooperative cancellation; never kills a process."""

    payload = {"version": "1.0", "cancel_requested_at": _now()}
    destination = _control_path(project_dir)
    temporary = destination.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(temporary, destination)


def create_app() -> FastAPI:
    app = FastAPI(title="OpenMontage Runner", docs_url=None, redoc_url=None)

    @app.get(f"{API_PREFIX}/health")
    def health() -> dict[str, bool]:
        return {"ok": True}

    @app.post(f"{API_PREFIX}/runs", response_model=RunResponse, status_code=status.HTTP_201_CREATED)
    def create_run(request: CreateRunRequest, _: None = Depends(require_auth)) -> RunResponse:
        project_id = _validate_project_id(request.project_id)
        try:
            # Validate before filesystem mutation: an unknown pipeline must not
            # leave a half-created directory behind.
            get_pipeline_stages(request.pipeline_type)
            pipeline_known = (Path(__file__).resolve().parents[1] / "pipeline_defs" / f"{request.pipeline_type}.yaml").is_file()
            if not pipeline_known:
                raise ValueError("unknown pipeline")
        except Exception:
            raise HTTPException(status_code=422, detail="unknown pipeline_type") from None
        project_dir = _project_dir(project_id, require_exists=False)
        if project_dir.exists():
            marker = _read_json(project_dir / "project.json")
            if marker:
                raise HTTPException(status_code=409, detail="project_id already exists")
            raise HTTPException(status_code=409, detail="project directory already exists")
        try:
            init_project(
                project_id,
                title=request.title,
                pipeline_type=request.pipeline_type,
                pipeline_dir=PROJECTS_DIR,
                style_playbook=request.style_playbook,
            )
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"project initialization failed: {exc}") from None
        return derive_status(project_dir)

    @app.get(f"{API_PREFIX}/runs/{{project_id}}", response_model=RunResponse)
    def get_run_status(project_id: str, _: None = Depends(require_auth)) -> RunResponse:
        return derive_status(_project_dir(project_id))

    @app.post(f"{API_PREFIX}/runs/{{project_id}}/cancel", response_model=RunResponse)
    def cancel_run(project_id: str, _: None = Depends(require_auth)) -> RunResponse:
        project_dir = _project_dir(project_id)
        current = derive_status(project_dir)
        if current.status in {"completed", "failed", "cancelled"}:
            raise HTTPException(status_code=409, detail=f"cannot cancel a {current.status} run")
        _write_cancel_request(project_dir)
        return derive_status(project_dir)

    return app


app = create_app()
