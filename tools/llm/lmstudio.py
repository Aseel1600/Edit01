"""LM Studio local inference (OpenAI-compatible HTTP API).

Talks to the server that LM Studio starts on the Mac, default
``http://127.0.0.1:1234/v1``. Free, local, no cloud tokens.

Actions: health, models, chat.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)

DEFAULT_BASE_URL = "http://127.0.0.1:1234/v1"
DEFAULT_TIMEOUT = 8


def _env_base_url() -> str:
    return (
        os.environ.get("LM_STUDIO_BASE_URL")
        or os.environ.get("OPENAI_BASE_URL")
        or DEFAULT_BASE_URL
    ).rstrip("/")


def _env_api_key() -> str:
    return os.environ.get("LM_STUDIO_API_KEY") or os.environ.get("OPENAI_API_KEY") or "lm-studio"


class LMStudio(BaseTool):
    name = "lmstudio"
    version = "1.0.0"
    tier = ToolTier.CORE
    capability = "llm"
    provider = "lmstudio"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.LOCAL

    dependencies = []
    install_instructions = (
        "Install LM Studio, load a model (e.g. Qwen coder), and start the local "
        "server on port 1234. Optional: set LM_STUDIO_BASE_URL and LM_STUDIO_MODEL."
    )
    agent_skills = ["creative/hermes-hostinger"]

    capabilities = ["chat_completions", "list_models", "health"]
    supports = {
        "openai_compatible": True,
        "local_offline": True,
        "free": True,
        "streaming": True,
    }
    best_for = [
        "local coding models without token cost",
        "Hermes Hostinger inference backend",
    ]
    not_good_for = [
        "cloud agents that cannot reach the user's localhost",
        "guaranteed uptime (the Mac must be awake with the server running)",
    ]

    input_schema = {
        "type": "object",
        "required": ["action"],
        "properties": {
            "action": {"type": "string", "enum": ["health", "models", "chat"]},
            "base_url": {"type": "string"},
            "model": {"type": "string"},
            "messages": {"type": "array"},
            "prompt": {"type": "string"},
            "temperature": {"type": "number"},
            "max_tokens": {"type": "integer"},
            "timeout_seconds": {"type": "number"},
        },
    }
    output_schema = {
        "type": "object",
        "properties": {
            "reachable": {"type": "boolean"},
            "base_url": {"type": "string"},
            "models": {"type": "array"},
            "message": {"type": "object"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=64, vram_mb=0, disk_mb=0, network_required=False
    )
    retry_policy = RetryPolicy(max_retries=1, backoff_seconds=0.5, retryable_errors=["timeout"])
    side_effects = ["HTTP calls to the local LM Studio server"]
    user_visible_verification = [
        "LM Studio Developer > Local Server shows Running on port 1234",
    ]

    def get_status(self) -> ToolStatus:
        result = self._request("GET", "/models", timeout=2.5)
        if result.get("ok"):
            return ToolStatus.AVAILABLE
        return ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        started = time.monotonic()
        action = (inputs.get("action") or "health").strip().lower()
        base_url = (inputs.get("base_url") or _env_base_url()).rstrip("/")
        timeout = float(inputs.get("timeout_seconds") or DEFAULT_TIMEOUT)

        if action == "health":
            ping = self._request("GET", "/models", base_url=base_url, timeout=timeout)
            models = self._parse_models(ping.get("json"))
            return ToolResult(
                success=bool(ping.get("ok")),
                data={
                    "reachable": bool(ping.get("ok")),
                    "base_url": base_url,
                    "models": models,
                    "model": os.environ.get("LM_STUDIO_MODEL") or (models[0] if models else None),
                    "error": ping.get("error"),
                },
                error=None if ping.get("ok") else ping.get("error") or "LM Studio not reachable",
                duration_seconds=time.monotonic() - started,
                cost_usd=0.0,
                model=os.environ.get("LM_STUDIO_MODEL"),
            )

        if action == "models":
            ping = self._request("GET", "/models", base_url=base_url, timeout=timeout)
            models = self._parse_models(ping.get("json"))
            return ToolResult(
                success=bool(ping.get("ok")),
                data={"base_url": base_url, "models": models, "raw": ping.get("json")},
                error=None if ping.get("ok") else ping.get("error"),
                duration_seconds=time.monotonic() - started,
                cost_usd=0.0,
            )

        if action == "chat":
            model = inputs.get("model") or os.environ.get("LM_STUDIO_MODEL")
            messages = inputs.get("messages")
            if not messages:
                prompt = inputs.get("prompt")
                if not prompt:
                    return ToolResult(success=False, error="chat requires messages or prompt")
                messages = [{"role": "user", "content": str(prompt)}]
            if not model:
                listed = self._request("GET", "/models", base_url=base_url, timeout=timeout)
                models = self._parse_models(listed.get("json"))
                if not models:
                    return ToolResult(
                        success=False,
                        error="No LM Studio model loaded. Start the local server and load a model.",
                    )
                model = models[0]
            body = {
                "model": model,
                "messages": messages,
                "temperature": inputs.get("temperature", 0.7),
                "max_tokens": inputs.get("max_tokens", 1024),
            }
            ping = self._request(
                "POST",
                "/chat/completions",
                base_url=base_url,
                payload=body,
                timeout=max(timeout, 60.0),
            )
            data = ping.get("json") or {}
            choice = (data.get("choices") or [{}])[0]
            return ToolResult(
                success=bool(ping.get("ok")),
                data={
                    "base_url": base_url,
                    "model": model,
                    "message": choice.get("message"),
                    "raw": data,
                },
                error=None if ping.get("ok") else ping.get("error"),
                duration_seconds=time.monotonic() - started,
                cost_usd=0.0,
                model=model,
            )

        return ToolResult(success=False, error=f"Unknown action: {action}")

    @staticmethod
    def _parse_models(payload: Any) -> list[str]:
        if not isinstance(payload, dict):
            return []
        items = payload.get("data") or payload.get("models") or []
        names: list[str] = []
        for item in items:
            if isinstance(item, dict) and item.get("id"):
                names.append(str(item["id"]))
            elif isinstance(item, str):
                names.append(item)
        return names

    def _request(
        self,
        method: str,
        path: str,
        *,
        base_url: str | None = None,
        payload: dict[str, Any] | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> dict[str, Any]:
        url = f"{(base_url or _env_base_url()).rstrip('/')}{path}"
        headers = {
            "Authorization": f"Bearer {_env_api_key()}",
            "Content-Type": "application/json",
        }
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                parsed: Any
                try:
                    parsed = json.loads(raw) if raw else {}
                except json.JSONDecodeError:
                    parsed = {"raw": raw}
                return {"ok": 200 <= getattr(resp, "status", 200) < 300, "json": parsed}
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:500]
            return {"ok": False, "error": f"HTTP {exc.code}: {body}"}
        except URLError as exc:
            return {"ok": False, "error": f"unreachable: {exc.reason}"}
        except Exception as exc:  # noqa: BLE001 — tool boundary
            return {"ok": False, "error": str(exc)}
