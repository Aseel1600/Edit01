"""Hostinger-domain deploy helper for the Hermes API."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SERVICE_DIR = REPO_ROOT / "services" / "hermes-api"
DEFAULT_DOMAIN = "hermestudios.com"


class HostingerDeploy(BaseTool):
    name = "hostinger_deploy"
    version = "1.0.0"
    tier = ToolTier.PUBLISH
    capability = "deploy"
    provider = "hostinger"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.HYBRID

    dependencies = []
    install_instructions = (
        "Local: Docker Desktop. Production: Hostinger VPS with Docker template, "
        "HOSTINGER_API_KEY from hPanel → API, HOSTINGER_VM_ID from the VPS URL. "
        "Do not purchase a VPS without the user's approval."
    )
    agent_skills = ["creative/hermes-hostinger"]

    capabilities = ["scaffold", "status", "serve_local", "deploy", "health_public"]
    supports = {"docker": True, "github_actions": True}
    best_for = ["Hermes API on hermestudios.com"]
    not_good_for = ["shared PHP-only hosting without a VPS or Node runtime"]

    input_schema = {
        "type": "object",
        "required": ["action"],
        "properties": {
            "action": {
                "type": "string",
                "enum": ["status", "scaffold", "serve_local", "deploy", "health_public"],
            },
            "domain": {"type": "string"},
            "url": {"type": "string"},
            "port": {"type": "integer"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=128, vram_mb=0, disk_mb=50, network_required=False
    )
    side_effects = [
        "serve_local starts uvicorn",
        "deploy requires Hostinger API credentials",
    ]
    user_visible_verification = [
        "Open https://<domain>/health or http://127.0.0.1:8080/health",
    ]

    def get_status(self) -> ToolStatus:
        if (SERVICE_DIR / "app.py").is_file() and (SERVICE_DIR / "docker-compose.yml").is_file():
            return ToolStatus.AVAILABLE
        return ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        started = time.monotonic()
        action = (inputs.get("action") or "status").strip().lower()
        domain = inputs.get("domain") or os.environ.get("PUBLIC_DOMAIN") or DEFAULT_DOMAIN

        if action == "status":
            return ToolResult(
                success=True,
                data=self._status(domain),
                duration_seconds=time.monotonic() - started,
            )

        if action == "scaffold":
            missing = [
                name
                for name in ("app.py", "Dockerfile", "docker-compose.yml")
                if not (SERVICE_DIR / name).is_file()
            ]
            return ToolResult(
                success=not missing,
                data={
                    "service_dir": str(SERVICE_DIR),
                    "compose_path": str(SERVICE_DIR / "docker-compose.yml"),
                    "domain": domain,
                    "missing": missing,
                    "workflow": ".github/workflows/deploy-hostinger.yml",
                },
                error=("Missing files: " + ", ".join(missing)) if missing else None,
                duration_seconds=time.monotonic() - started,
            )

        if action == "health_public":
            url = inputs.get("url") or f"https://{domain}/health"
            payload = self._http_get(url)
            ok = bool(payload.get("ok") and payload.get("status_code") == 200)
            return ToolResult(
                success=ok,
                data={"url": url, **payload},
                error=None if ok else payload.get("error") or f"health failed for {url}",
                duration_seconds=time.monotonic() - started,
            )

        if action == "serve_local":
            port = int(inputs.get("port") or os.environ.get("HERMES_PORT") or 8080)
            return ToolResult(
                success=True,
                data={
                    "command": [
                        "uvicorn",
                        "app:app",
                        "--app-dir",
                        str(SERVICE_DIR),
                        "--host",
                        "127.0.0.1",
                        "--port",
                        str(port),
                    ],
                    "health": f"http://127.0.0.1:{port}/health",
                    "note": "Start via: python scripts/hermes_hostinger.py serve",
                },
                duration_seconds=time.monotonic() - started,
            )

        if action == "deploy":
            api_key = os.environ.get("HOSTINGER_API_KEY")
            vm_id = os.environ.get("HOSTINGER_VM_ID")
            if not api_key or not vm_id:
                return ToolResult(
                    success=False,
                    error=(
                        "HOSTINGER_API_KEY and HOSTINGER_VM_ID are required for remote deploy. "
                        "Use serve_local or the GitHub Action instead. Do not buy a VPS without approval."
                    ),
                    data={
                        "domain": domain,
                        "workflow": ".github/workflows/deploy-hostinger.yml",
                        "compose_path": str(SERVICE_DIR / "docker-compose.yml"),
                    },
                    duration_seconds=time.monotonic() - started,
                )
            if shutil.which("docker") is None:
                return ToolResult(success=False, error="docker CLI not found")
            check = subprocess.run(
                ["docker", "compose", "-f", str(SERVICE_DIR / "docker-compose.yml"), "config"],
                capture_output=True,
                text=True,
                check=False,
            )
            if check.returncode != 0:
                return ToolResult(
                    success=False,
                    error=check.stderr.strip() or "docker compose config failed",
                )
            return ToolResult(
                success=True,
                data={
                    "domain": domain,
                    "vm_id_set": True,
                    "compose_valid": True,
                    "next": "Push to main or run workflow_dispatch on deploy-hostinger.yml",
                },
                duration_seconds=time.monotonic() - started,
            )

        return ToolResult(success=False, error=f"Unknown action: {action}")

    def _status(self, domain: str) -> dict[str, Any]:
        return {
            "domain": domain,
            "service_dir": str(SERVICE_DIR),
            "compose_exists": (SERVICE_DIR / "docker-compose.yml").is_file(),
            "app_exists": (SERVICE_DIR / "app.py").is_file(),
            "docker": shutil.which("docker") is not None,
            "hostinger_api_key": bool(os.environ.get("HOSTINGER_API_KEY")),
            "hostinger_vm_id": bool(os.environ.get("HOSTINGER_VM_ID")),
            "hermes_api_key": bool(os.environ.get("HERMES_API_KEY")),
            "public_domain": os.environ.get("PUBLIC_DOMAIN") or domain,
            "workflow": ".github/workflows/deploy-hostinger.yml",
        }

    @staticmethod
    def _http_get(url: str) -> dict[str, Any]:
        req = Request(url, method="GET")
        try:
            with urlopen(req, timeout=8) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                try:
                    body = json.loads(raw)
                except json.JSONDecodeError:
                    body = {"raw": raw[:300]}
                return {"ok": True, "status_code": getattr(resp, "status", 200), "body": body}
        except URLError as exc:
            return {"ok": False, "error": str(exc.reason)}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}
