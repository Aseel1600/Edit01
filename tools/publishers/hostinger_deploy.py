"""Hostinger-domain deploy helper for the Hermes API."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
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
HOSTINGER_API = "https://developers.hostinger.com"
HPANEL_DNS = "https://hpanel.hostinger.com/domains"

# User shorthand hermestudio.com is not in the Hostinger portfolio.
_DOMAIN_ALIASES = {
    "hermestudio.com": DEFAULT_DOMAIN,
    "www.hermestudio.com": DEFAULT_DOMAIN,
    "hermestudios.com": DEFAULT_DOMAIN,
    "www.hermestudios.com": DEFAULT_DOMAIN,
    "hermestudios.org": DEFAULT_DOMAIN,
    "hermestudios.online": DEFAULT_DOMAIN,
    "hermestudioos.com": DEFAULT_DOMAIN,
}


def canonical_domain(raw: str | None) -> str:
    value = (raw or DEFAULT_DOMAIN).strip().lower()
    value = value.removeprefix("https://").removeprefix("http://")
    value = value.split("/", 1)[0]
    if value.startswith("www."):
        mapped = _DOMAIN_ALIASES.get(value) or _DOMAIN_ALIASES.get(value[4:])
        return mapped or DEFAULT_DOMAIN
    return _DOMAIN_ALIASES.get(value) or value or DEFAULT_DOMAIN

SCAFFOLD_FILES = (
    "app.py",
    "Dockerfile",
    "docker-compose.yml",
    "requirements.txt",
    "Caddyfile",
    ".env.example",
    ".dockerignore",
    "static/index.html",
    "static/styles.css",
)

# Regenerated only when missing. Do not clobber a customized app.py.
_SCAFFOLD_TEMPLATES: dict[str, str] = {
    ".dockerignore": """\
.env
.env.*
!.env.example
__pycache__
*.pyc
*.pyo
.DS_Store
cloudflared.yml.example
Caddyfile
docker-compose.yml
""",
    ".env.example": """\
PUBLIC_DOMAIN=hermestudios.com
HERMES_REQUIRE_AUTH=true
HERMES_API_KEY=
HERMES_MAX_INFLIGHT=32
HERMES_INFLIGHT_WAIT_SECONDS=5
HERMES_HOST_PORT=8080
INFERENCE_BACKEND=vllm
INFERENCE_BASE_URL=
INFERENCE_API_KEY=
INFERENCE_MODEL=qwen3-30b-a3b
LM_STUDIO_BASE_URL=
LM_STUDIO_API_KEY=
LM_STUDIO_MODEL=
CADDY_EMAIL=ops@hermestudios.com
""",
    "Caddyfile": """\
{
  email {$CADDY_EMAIL}
}

hermestudios.com, www.hermestudios.com {
  encode gzip
  reverse_proxy hermes-api:8080
}

hermestudios.org {
  encode gzip
  reverse_proxy hermes-api:8080
}

hermestudios.online {
  encode gzip
  reverse_proxy hermes-api:8080
}
""",
}


class HostingerDeploy(BaseTool):
    name = "hostinger_deploy"
    version = "1.1.0"
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

    capabilities = [
        "scaffold",
        "status",
        "serve_local",
        "deploy",
        "health_public",
        "dns_status",
        "dns_apply",
    ]
    supports = {
        "docker": True,
        "github_actions": True,
        "caddy_tls": True,
        "hostinger_dns": True,
    }
    best_for = ["Hermes API on hermestudios.com"]
    not_good_for = ["shared PHP-only hosting without a VPS or Node runtime"]

    input_schema = {
        "type": "object",
        "required": ["action"],
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "status",
                    "scaffold",
                    "serve_local",
                    "deploy",
                    "health_public",
                    "dns_status",
                    "dns_apply",
                ],
            },
            "domain": {"type": "string"},
            "url": {"type": "string"},
            "port": {"type": "integer"},
            "ipv4": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=128, vram_mb=0, disk_mb=50, network_required=False
    )
    side_effects = [
        "scaffold writes missing files under services/hermes-api/",
        "serve_local starts uvicorn",
        "deploy requires Hostinger API credentials",
        "dns_apply updates Hostinger A/@ and A/www records",
    ]
    user_visible_verification = [
        "Open https://<domain>/health or http://127.0.0.1:8080/livez",
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
        requested_domain = inputs.get("domain") or os.environ.get("PUBLIC_DOMAIN") or DEFAULT_DOMAIN
        domain = canonical_domain(requested_domain)

        if action == "status":
            return ToolResult(
                success=True,
                data=self._status(domain),
                duration_seconds=time.monotonic() - started,
            )

        if action == "scaffold":
            payload = self._scaffold(domain)
            missing = payload["missing"]
            compose_ok = payload.get("compose_valid")
            auth_ok = bool(os.environ.get("HERMES_API_KEY"))
            success = not missing and compose_ok is not False
            error = None
            if missing:
                error = "Missing files: " + ", ".join(missing)
            elif compose_ok is False:
                error = payload.get("compose_error") or "docker compose config failed"
            return ToolResult(
                success=success,
                data={
                    **payload,
                    "auth_configured": auth_ok,
                    "deployed": False,
                    "production_blocked_reason": (
                        None
                        if auth_ok
                        else "HERMES_API_KEY empty — local scaffold only; refuse deployed=true"
                    ),
                    "workflow": ".github/workflows/deploy-hostinger.yml",
                },
                error=error,
                duration_seconds=time.monotonic() - started,
            )

        if action == "dns_status":
            payload = self._dns_status(domain, requested_domain=str(requested_domain))
            return ToolResult(
                success=bool(payload.get("ok")),
                data=payload,
                error=None if payload.get("ok") else payload.get("error"),
                duration_seconds=time.monotonic() - started,
            )

        if action == "dns_apply":
            payload = self._dns_apply(
                domain,
                requested_domain=str(requested_domain),
                ipv4=inputs.get("ipv4"),
            )
            return ToolResult(
                success=bool(payload.get("ok")),
                data=payload,
                error=None if payload.get("ok") else payload.get("error"),
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
                    "livez": f"http://127.0.0.1:{port}/livez",
                    "note": "Start via: python scripts/hermes_hostinger.py serve",
                },
                duration_seconds=time.monotonic() - started,
            )

        if action == "deploy":
            api_key = os.environ.get("HOSTINGER_API_KEY")
            vm_id = os.environ.get("HOSTINGER_VM_ID")
            hermes_key = os.environ.get("HERMES_API_KEY") or ""
            if not hermes_key.strip():
                return ToolResult(
                    success=False,
                    error=(
                        "HERMES_API_KEY is required to mark a production deploy. "
                        "Scaffold and serve_local remain available."
                    ),
                    data={
                        "domain": domain,
                        "deployed": False,
                        "auth_configured": False,
                        "workflow": ".github/workflows/deploy-hostinger.yml",
                    },
                    duration_seconds=time.monotonic() - started,
                )
            if not api_key or not vm_id:
                return ToolResult(
                    success=False,
                    error=(
                        "HOSTINGER_API_KEY and HOSTINGER_VM_ID are required for remote deploy. "
                        "Use serve_local or the GitHub Action instead. Do not buy a VPS without approval."
                    ),
                    data={
                        "domain": domain,
                        "deployed": False,
                        "auth_configured": True,
                        "workflow": ".github/workflows/deploy-hostinger.yml",
                        "compose_path": str(SERVICE_DIR / "docker-compose.yml"),
                    },
                    duration_seconds=time.monotonic() - started,
                )
            if shutil.which("docker") is None:
                return ToolResult(success=False, error="docker CLI not found")
            check = self._compose_config()
            if not check["ok"]:
                return ToolResult(
                    success=False,
                    error=check["error"],
                    data={"compose_valid": False, "deployed": False},
                    duration_seconds=time.monotonic() - started,
                )
            return ToolResult(
                success=True,
                data={
                    "domain": domain,
                    "vm_id_set": True,
                    "compose_valid": True,
                    "auth_configured": True,
                    "deployed": False,
                    "next": "Push to main or run workflow_dispatch on deploy-hostinger.yml",
                },
                duration_seconds=time.monotonic() - started,
            )

        return ToolResult(success=False, error=f"Unknown action: {action}")

    def _scaffold(self, domain: str) -> dict[str, Any]:
        SERVICE_DIR.mkdir(parents=True, exist_ok=True)
        written: list[str] = []
        existing: list[str] = []
        for relative, body in _SCAFFOLD_TEMPLATES.items():
            path = SERVICE_DIR / relative
            if path.is_file():
                existing.append(relative)
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
            written.append(relative)

        missing = [name for name in SCAFFOLD_FILES if not (SERVICE_DIR / name).is_file()]
        for name in SCAFFOLD_FILES:
            if name not in missing and name not in written and name not in existing:
                existing.append(name)

        compose = self._compose_config()
        tls = self._compose_config(profiles="tls")
        return {
            "service_dir": str(SERVICE_DIR),
            "compose_path": str(SERVICE_DIR / "docker-compose.yml"),
            "caddy_path": str(SERVICE_DIR / "Caddyfile"),
            "domain": domain,
            "written": written,
            "existing": sorted(set(existing)),
            "missing": missing,
            "compose_valid": compose["ok"] if compose["ok"] is not None else None,
            "compose_error": compose.get("error"),
            "tls_profile_valid": tls["ok"] if tls["ok"] is not None else None,
            "tls_profile": "COMPOSE_PROFILES=tls",
            "livez": "/livez",
            "health": "/health",
        }

    def _status(self, domain: str) -> dict[str, Any]:
        return {
            "domain": domain,
            "service_dir": str(SERVICE_DIR),
            "compose_exists": (SERVICE_DIR / "docker-compose.yml").is_file(),
            "caddy_exists": (SERVICE_DIR / "Caddyfile").is_file(),
            "app_exists": (SERVICE_DIR / "app.py").is_file(),
            "docker": shutil.which("docker") is not None,
            "hostinger_api_key": bool(os.environ.get("HOSTINGER_API_KEY")),
            "hostinger_vm_id": bool(os.environ.get("HOSTINGER_VM_ID")),
            "hermes_api_key": bool(os.environ.get("HERMES_API_KEY")),
            "public_domain": os.environ.get("PUBLIC_DOMAIN") or domain,
            "canonical_domain": canonical_domain(domain),
            "hpanel_dns": HPANEL_DNS,
            "workflow": ".github/workflows/deploy-hostinger.yml",
            "tls_profile": "COMPOSE_PROFILES=tls",
            "hostinger_vps_ip": bool(os.environ.get("HOSTINGER_VPS_IP")),
        }

    @staticmethod
    def _compose_config(*, profiles: str | None = None) -> dict[str, Any]:
        if shutil.which("docker") is None:
            return {"ok": None, "error": "docker CLI not found"}
        env = os.environ.copy()
        if profiles:
            env["COMPOSE_PROFILES"] = profiles
        check = subprocess.run(
            ["docker", "compose", "-f", str(SERVICE_DIR / "docker-compose.yml"), "config"],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        if check.returncode != 0:
            return {"ok": False, "error": (check.stderr or check.stdout).strip()}
        return {"ok": True}

    def _dns_status(self, domain: str, *, requested_domain: str) -> dict[str, Any]:
        api_key = os.environ.get("HOSTINGER_API_KEY")
        base = {
            "provider": "hostinger",
            "requested_domain": requested_domain,
            "canonical_domain": domain,
            "hpanel_dns": f"{HPANEL_DNS}",
            "applied": False,
            "status": "blocked",
        }
        if not api_key:
            return {
                **base,
                "ok": False,
                "error": (
                    "HOSTINGER_API_KEY missing. Sign in to hPanel → API, then retry "
                    f"dns_status. Manual path: {HPANEL_DNS} → {domain} → DNS."
                ),
            }
        response = self._hostinger_request("GET", f"/api/dns/v1/zones/{domain}")
        if not response.get("ok"):
            return {
                **base,
                "ok": False,
                "error": response.get("error") or "Hostinger DNS GET failed",
                "status_code": response.get("status_code"),
            }
        apex, www = _extract_a_records(response.get("body"))
        return {
            **base,
            "ok": True,
            "status": "read",
            "apex_a": apex,
            "www_a": www,
            "records": _summarize_records(response.get("body")),
        }

    def _dns_apply(
        self,
        domain: str,
        *,
        requested_domain: str,
        ipv4: str | None,
    ) -> dict[str, Any]:
        target = self._resolve_ipv4(ipv4)
        status = self._dns_status(domain, requested_domain=requested_domain)
        if not target:
            return {
                **status,
                "ok": False,
                "applied": False,
                "status": "blocked",
                "error": (
                    "No VPS IPv4. Pass ipv4, set HOSTINGER_VPS_IP, or set "
                    "HOSTINGER_VM_ID so the VPS API can resolve it. Do not buy a VPS."
                ),
            }
        if not os.environ.get("HOSTINGER_API_KEY"):
            return {
                **status,
                "ok": False,
                "applied": False,
                "target_ipv4": target,
                "status": "blocked",
                "error": (
                    "HOSTINGER_API_KEY missing. Cannot PUT DNS. "
                    f"In hPanel set A @ and A www on {domain} to {target}."
                ),
            }
        # www is often a CNAME. overwrite=true only replaces matching type, so
        # drop CNAME www before writing A www (CNAME cannot coexist).
        self._hostinger_request(
            "DELETE",
            f"/api/dns/v1/zones/{domain}",
            {"filters": [{"name": "www", "type": "CNAME"}]},
        )
        payload = {
            "overwrite": True,
            "zone": [
                {
                    "name": "@",
                    "type": "A",
                    "ttl": 300,
                    "records": [{"content": target}],
                },
                {
                    "name": "www",
                    "type": "A",
                    "ttl": 300,
                    "records": [{"content": target}],
                },
            ],
        }
        response = self._hostinger_request(
            "PUT",
            f"/api/dns/v1/zones/{domain}",
            payload,
        )
        if not response.get("ok"):
            return {
                **status,
                "ok": False,
                "applied": False,
                "target_ipv4": target,
                "status": "blocked",
                "request": payload,
                "error": response.get("error") or "Hostinger DNS PUT failed",
                "status_code": response.get("status_code"),
            }
        refreshed = self._dns_status(domain, requested_domain=requested_domain)
        return {
            **refreshed,
            "ok": True,
            "applied": True,
            "status": "applied",
            "target_ipv4": target,
        }

    def _resolve_ipv4(self, explicit: str | None) -> str | None:
        candidate = (explicit or os.environ.get("HOSTINGER_VPS_IP") or "").strip()
        if _looks_ipv4(candidate):
            return candidate
        vm_id = (os.environ.get("HOSTINGER_VM_ID") or "").strip()
        if not vm_id or not os.environ.get("HOSTINGER_API_KEY"):
            return None
        response = self._hostinger_request(
            "GET",
            f"/api/vps/v1/virtual-machines/{vm_id}",
        )
        if not response.get("ok"):
            return None
        return _extract_ipv4(response.get("body"))

    def _hostinger_request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        api_key = os.environ.get("HOSTINGER_API_KEY") or ""
        if not api_key:
            return {"ok": False, "status_code": 0, "error": "HOSTINGER_API_KEY missing"}
        _pin_hostinger_api_dns()
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = Request(f"{HOSTINGER_API}{path}", data=data, method=method)
        req.add_header("Authorization", f"Bearer {api_key}")
        req.add_header("Accept", "application/json")
        # Cloudflare 1010 bans the default Python-urllib user-agent.
        req.add_header(
            "User-Agent",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        )
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urlopen(req, timeout=20) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                try:
                    body = json.loads(raw) if raw else {}
                except json.JSONDecodeError:
                    body = {"raw": raw[:500]}
                return {
                    "ok": 200 <= int(getattr(resp, "status", 200)) < 300,
                    "status_code": int(getattr(resp, "status", 200)),
                    "body": body,
                }
        except HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")[:2000]
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                body = {"raw": raw}
            return {
                "ok": False,
                "status_code": int(exc.code),
                "error": f"Hostinger API {exc.code}",
                "body": body,
            }
        except URLError as exc:
            return {"ok": False, "status_code": 0, "error": str(exc.reason)}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "status_code": 0, "error": str(exc)}

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


_HOSTINGER_DNS_PINNED = False


def _pin_hostinger_api_dns() -> None:
    """System resolver on some Macs fails for developers.hostinger.com."""
    global _HOSTINGER_DNS_PINNED
    if _HOSTINGER_DNS_PINNED:
        return
    import socket

    try:
        socket.getaddrinfo("developers.hostinger.com", 443, socket.AF_INET)
        _HOSTINGER_DNS_PINNED = True
        return
    except OSError:
        pass
    ip = None
    dig = subprocess.run(
        ["dig", "+short", "developers.hostinger.com", "A", "@8.8.8.8"],
        capture_output=True,
        text=True,
        check=False,
    )
    for line in (dig.stdout or "").splitlines():
        candidate = line.strip()
        if _looks_ipv4(candidate):
            ip = candidate
            break
    if not ip:
        ip = "104.19.149.80"
    orig = socket.getaddrinfo

    def patched(host, port, *args, **kwargs):
        if host == "developers.hostinger.com":
            return orig(ip, port, *args, **kwargs)
        return orig(host, port, *args, **kwargs)

    socket.getaddrinfo = patched  # type: ignore[method-assign]
    _HOSTINGER_DNS_PINNED = True


def _looks_ipv4(value: str) -> bool:
    parts = value.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False


def _extract_ipv4(body: Any) -> str | None:
    if not isinstance(body, dict):
        return None
    for key in ("ipv4", "ip_address", "public_ip", "ipv4_address", "ip"):
        found = _coerce_ipv4(body.get(key))
        if found:
            return found
    for nested_key in ("network", "networks", "addresses"):
        found = _extract_ipv4(body.get(nested_key)) if isinstance(body.get(nested_key), dict) else None
        if found:
            return found
        nested = body.get(nested_key)
        if isinstance(nested, list):
            for item in nested:
                found = _extract_ipv4(item) if isinstance(item, dict) else _coerce_ipv4(item)
                if found:
                    return found
    return None


def _coerce_ipv4(value: Any) -> str | None:
    if isinstance(value, str) and _looks_ipv4(value):
        return value
    if isinstance(value, list) and value:
        return _coerce_ipv4(value[0])
    if isinstance(value, dict):
        for key in ("address", "ip", "content", "ipv4"):
            found = _coerce_ipv4(value.get(key))
            if found:
                return found
    return None


def _extract_a_records(body: Any) -> tuple[list[str], list[str]]:
    apex: list[str] = []
    www: list[str] = []
    for rec in _iter_zone_records(body):
        rtype = str(rec.get("type") or "").upper()
        name = str(rec.get("name") or "").rstrip(".")
        if rtype != "A":
            continue
        contents = rec.get("records") or rec.get("content") or rec.get("value") or rec.get("ipv4")
        ips = _contents_to_ips(contents)
        if name in {"@", "", DEFAULT_DOMAIN, f"{DEFAULT_DOMAIN}."}:
            apex.extend(ips)
        elif name in {"www", f"www.{DEFAULT_DOMAIN}"}:
            www.extend(ips)
    return apex, www


def _summarize_records(body: Any) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for rec in _iter_zone_records(body):
        summary.append(
            {
                "name": rec.get("name"),
                "type": rec.get("type"),
                "ttl": rec.get("ttl"),
            }
        )
        if len(summary) >= 40:
            break
    return summary


def _iter_zone_records(body: Any) -> list[dict[str, Any]]:
    if isinstance(body, list):
        return [item for item in body if isinstance(item, dict)]
    if isinstance(body, dict):
        for key in ("records", "zone", "data"):
            nested = body.get(key)
            if isinstance(nested, list):
                return [item for item in nested if isinstance(item, dict)]
    return []


def _contents_to_ips(contents: Any) -> list[str]:
    if isinstance(contents, str) and _looks_ipv4(contents):
        return [contents]
    if isinstance(contents, list):
        found: list[str] = []
        for item in contents:
            if isinstance(item, str) and _looks_ipv4(item):
                found.append(item)
            elif isinstance(item, dict):
                for key in ("content", "value", "ipv4", "ip"):
                    val = item.get(key)
                    if isinstance(val, str) and _looks_ipv4(val):
                        found.append(val)
        return found
    return []

