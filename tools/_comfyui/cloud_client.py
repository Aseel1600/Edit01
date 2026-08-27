"""Comfy Cloud transport for the ComfyUI tools.

Comfy Cloud runs real ComfyUI behind an ``/api`` prefix and an ``X-API-Key``
header, so most of :class:`~tools._comfyui.client.ComfyUIClient` applies
verbatim. Five things genuinely differ, and each is overridden here rather
than branched inside the local client — the local path is what most users
depend on and the hardest for a reviewer to regression-test, so it is left
untouched:

* **health** — there is no ``/system_stats``; ``/api/user`` is the ping.
* **polling** — local treats "a history entry exists" as done. Cloud
  publishes explicit states and a queued job already has a record, so the
  terminal state must be read before the outputs.
* **outputs** — ``/api/jobs/{id}`` is flat and its top-level ``status`` is
  the bare string ``"completed"``. The local-shaped dict sits beside it
  under ``execution_status``, so the mapping is a three-key rename. Reading
  the top-level field instead makes every failure look like a success.
* **download** — ``/api/view`` 302s to a short-lived signed URL that must be
  fetched *without* the auth header.
* **node metadata** — the per-node ``/object_info/{class}`` route 404s; only
  the full ~10MB payload is served, so it is fetched once and memoized.

Partner API nodes (ElevenLabs, Kling, Veo, Recraft, ...) additionally read
the account credential from the submit payload's ``extra_data``, not from
the request header.
"""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any, Callable

import requests

from tools._comfyui.client import ComfyUIClient, ComfyUIError

CLOUD_BASE_URL = "https://cloud.comfy.org"

#: Terminal values of ``GET /api/job/{id}/status``. ``failed`` is not in the
#: published list but is what the API returns for a node that raised —
#: omitting it polls a dead job until the caller's timeout.
CLOUD_TERMINAL = {
    "success",
    "error",
    "failed",
    "non_retryable_error",
    "lost",
    "cancelled",
}


def describe_cloud_error(payload: dict) -> str:
    """Readable cause from a failed job's status payload.

    A failed job has no ``execution_status`` at all; the detail lives in
    ``error_message`` as a JSON *string*.
    """
    raw = payload.get("error_message")
    if not raw:
        return ""
    try:
        detail = json.loads(raw) if isinstance(raw, str) else raw
    except (ValueError, TypeError):
        return str(raw)[:300]
    node = detail.get("node_type") or detail.get("node_id")
    message = str(detail.get("exception_message", "")).strip()
    return f"Node {node}: {message}" if node else message[:300]


class ComfyCloudClient(ComfyUIClient):
    """ComfyUIClient speaking Comfy Cloud's hosted API."""

    backend = "cloud"
    is_cloud = True

    def __init__(self, capability: str | None = None, **_ignored: Any) -> None:
        # Deliberately does not call super().__init__: the base resolves a
        # local server URL from env vars that mean nothing here.
        self.capability = capability
        self._capability_env_var = None
        self._object_info_cache: dict[str, Any] | None = None
        base = (os.environ.get("COMFY_CLOUD_BASE_URL") or CLOUD_BASE_URL).rstrip("/")
        self.server_url = f"{base}/api"
        key = os.environ.get("COMFY_CLOUD_API_KEY", "")
        self._headers = {"X-API-Key": key} if key else {}
        self.client_id = str(uuid.uuid4())

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    @property
    def is_default_url(self) -> bool:
        return False

    def unavailable_reason(self) -> str:
        if not os.environ.get("COMFY_CLOUD_API_KEY"):
            return (
                "Comfy Cloud selected but COMFY_CLOUD_API_KEY is not set.\n"
                "Get a key at https://platform.comfy.org and add it to .env."
            )
        return (
            f"Comfy Cloud not reachable at {self.server_url}.\n"
            "Check the key is valid and the workspace subscription is active."
        )

    def is_available(self) -> bool:
        if not os.environ.get("COMFY_CLOUD_API_KEY"):
            return False
        try:
            resp = requests.get(
                f"{self.server_url}/user", headers=self._headers, timeout=10
            )
            return resp.status_code == 200
        except Exception:
            return False

    def recovery_hint(self, prompt_id: str) -> str:
        # Cloud has no /history route; sending a user there 404s.
        return f"GET {self.server_url}/jobs/{prompt_id} (with X-API-Key)"

    # ------------------------------------------------------------------
    # Errors
    # ------------------------------------------------------------------

    def _raise_for_error(self, resp: requests.Response) -> None:
        """Map a Cloud error response onto ComfyUIError.

        Two envelope shapes are in play: validation errors return
        ``{"error": {...}}`` while auth and billing errors return
        ``{"code", "message"}``. 402 and 429 both look like throttling and
        neither is retryable, so they are named explicitly.
        """
        if resp.status_code < 400:
            return
        try:
            body = resp.json()
        except Exception:
            body = {}
        detail = (
            (body.get("error") or {}).get("message")
            if isinstance(body.get("error"), dict)
            else None
        ) or body.get("message") or resp.text[:300]
        hint = {
            401: "COMFY_CLOUD_API_KEY is missing or invalid.",
            402: "Comfy Cloud workspace is out of credits — add credits to continue.",
            429: "Comfy Cloud subscription is inactive — reactivate it to continue.",
        }.get(resp.status_code)
        msg = f"Comfy Cloud HTTP {resp.status_code}: {detail}"
        raise ComfyUIError(f"{msg}\n{hint}" if hint else msg)

    # ------------------------------------------------------------------
    # Node metadata
    # ------------------------------------------------------------------

    def _object_info(self, node_class: str) -> dict:
        if self._object_info_cache is None:
            resp = requests.get(
                f"{self.server_url}/object_info", headers=self._headers, timeout=180
            )
            self._raise_for_error(resp)
            self._object_info_cache = resp.json()
        cache = self._object_info_cache or {}
        return {node_class: cache[node_class]} if node_class in cache else {}

    def list_models(self) -> dict[str, list[str]]:
        node_to_key = {
            "CheckpointLoaderSimple": ("ckpt_name", "checkpoints"),
            "UNETLoader": ("unet_name", "diffusion_models"),
            "VAELoader": ("vae_name", "vae"),
            "CLIPLoader": ("clip_name", "clip"),
            "LoraLoaderModelOnly": ("lora_name", "loras"),
        }
        result: dict[str, list[str]] = {}
        for node_class, (field, group) in node_to_key.items():
            try:
                options = (
                    self._object_info(node_class)
                    .get(node_class, {})
                    .get("input", {})
                    .get("required", {})
                    .get(field, [[]])[0]
                )
                result[group] = options if isinstance(options, list) else []
            except Exception:
                result[group] = []
        return result

    def has_node(self, node_class: str) -> bool:
        try:
            return node_class in self._object_info(node_class)
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Core cycle
    # ------------------------------------------------------------------

    def submit(self, workflow: dict) -> str:
        payload: dict[str, Any] = {
            "prompt": workflow,
            "client_id": self.client_id,
        }
        key = os.environ.get("COMFY_CLOUD_API_KEY")
        if key:
            # Partner API nodes bill through the Comfy account and read the
            # credential from here, not the header. Without it they fail at
            # execution with "Unauthorized: Please login first to use this node."
            payload["extra_data"] = {"api_key_comfy_org": key}

        resp = requests.post(
            f"{self.server_url}/prompt",
            json=payload,
            headers=self._headers,
            timeout=30,
        )
        self._raise_for_error(resp)
        try:
            data = resp.json()
        except ValueError:
            data = {}
        if data.get("node_errors"):
            raise ComfyUIError(f"Node errors: {json.dumps(data['node_errors'])}")
        prompt_id = data.get("prompt_id")
        if not prompt_id:
            raise ComfyUIError(f"No prompt_id in response: {data}")
        return prompt_id

    def _history_entry(self, prompt_id: str) -> dict | None:
        resp = requests.get(
            f"{self.server_url}/job/{prompt_id}/status",
            headers=self._headers,
            timeout=20,
        )
        self._raise_for_error(resp)
        payload = resp.json()
        state = str(payload.get("status", ""))
        if state not in CLOUD_TERMINAL:
            return None
        if state != "success":
            raise ComfyUIError(
                f"Comfy Cloud job {state}. {describe_cloud_error(payload)}".strip(),
                prompt_id=prompt_id,
            )

        job = requests.get(
            f"{self.server_url}/jobs/{prompt_id}", headers=self._headers, timeout=30
        )
        self._raise_for_error(job)
        entry = self.normalize_job(job.json())
        status = entry.get("status", {})
        if status.get("status_str") == "error":
            raise ComfyUIError(
                f"Execution error: {status.get('messages', [])}", prompt_id=prompt_id
            )
        return entry

    @staticmethod
    def normalize_job(job: dict) -> dict:
        """Map a ``/api/jobs/{id}`` record onto the local history shape.

        ``execution_status`` is already the local
        ``{status_str, completed, messages}`` dict, so this is a rename, not
        a translation. Using the flat record's top-level ``status`` instead
        yields the bare string ``"completed"`` and the caller's
        ``status_str == "error"`` check would never fire.
        """
        return {
            "outputs": job.get("outputs", {}),
            "status": job.get("execution_status", {}),
            "meta": job.get("execution_meta", {}),
        }

    def _wait(
        self,
        prompt_id: str,
        *,
        timeout: int,
        interval: int,
        on_progress: Callable[[dict], None] | None = None,
    ) -> dict:
        # Cloud's websocket needs token auth and a different event contract.
        # REST polling is already the supported fallback, so it is used
        # directly rather than carrying a second websocket implementation.
        return self.poll(prompt_id, timeout=timeout, interval=interval)

    def download(
        self,
        filename: str,
        subfolder: str,
        dest: Path,
        folder_type: str = "output",
    ) -> Path:
        resp = requests.get(
            f"{self.server_url}/view",
            params={
                "filename": filename,
                "subfolder": subfolder,
                "type": folder_type,
            },
            headers=self._headers,
            allow_redirects=False,
            timeout=120,
        )
        if resp.status_code in (301, 302, 303, 307, 308):
            location = resp.headers.get("Location")
            if not location:
                raise ComfyUIError(
                    f"Comfy Cloud returned {resp.status_code} for {filename} "
                    "with no Location header."
                )
            # The signed storage URL rejects the auth header — fetch it bare.
            resp = requests.get(location, timeout=300)
        else:
            self._raise_for_error(resp)
        resp.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(resp.content)
        return dest

    def upload_image(self, local_path: Path, name: str) -> str:
        with open(local_path, "rb") as handle:
            resp = requests.post(
                f"{self.server_url}/upload/image",
                files={"image": (name, handle, "image/png")},
                headers=self._headers,
                timeout=60,
            )
        self._raise_for_error(resp)
        resp.raise_for_status()
        return resp.json()["name"]


def resolve_backend(explicit: str | None = None) -> str:
    """Decide which ComfyUI transport to use: ``"local"`` or ``"cloud"``.

    Resolution, in order:

    1. an explicit ``backend`` argument (``"local"`` / ``"cloud"``),
    2. ``COMFYUI_BACKEND`` (same values, plus ``"auto"``),
    3. auto, which is decided by what is configured:

       ==========================  ==========================  =======
       local server URL            COMFY_CLOUD_API_KEY          result
       ==========================  ==========================  =======
       set                         --                           local
       set                         set                          local
       --                          set                          cloud
       --                          --                           local
       ==========================  ==========================  =======

    A configured local server always wins. Cloud is metered and a local
    server is not, so when someone has gone to the trouble of standing one
    up, silently billing them for a hosted run would be the wrong default —
    an unreachable local server is a fault to report, not a reason to spend.
    With no local server configured at all, a cloud key is an unambiguous
    statement of intent and is used.
    """
    choice = (explicit or os.environ.get("COMFYUI_BACKEND") or "auto").strip().lower()
    if choice in ("local", "cloud"):
        return choice
    if choice != "auto":
        raise ValueError(
            f"Invalid backend {choice!r}. Expected 'local', 'cloud', or 'auto'."
        )
    local_configured = any(
        os.environ.get(var)
        for var in (
            "COMFYUI_SERVER_URL",
            "COMFYUI_IMAGE_SERVER_URL",
            "COMFYUI_VIDEO_SERVER_URL",
            "COMFYUI_MUSIC_SERVER_URL",
        )
    )
    if local_configured:
        return "local"
    return "cloud" if os.environ.get("COMFY_CLOUD_API_KEY") else "local"


def make_client(
    capability: str | None = None, backend: str | None = None
) -> ComfyUIClient:
    """Return the client for *backend*, resolving ``auto`` first."""
    if resolve_backend(backend) == "cloud":
        return ComfyCloudClient(capability=capability)
    return ComfyUIClient(capability=capability)
