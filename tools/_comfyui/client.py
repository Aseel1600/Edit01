"""Thin REST client for a running ComfyUI server.

Handles the full generation cycle: submit workflow, poll for completion,
download artifacts.  Used by comfyui_image, comfyui_video, and comfyui_music.
"""

from __future__ import annotations

import copy
import json
import os
import random
import time
import uuid
from pathlib import Path
from typing import Any, Callable

import requests


CLOUD_BASE_URL = "https://cloud.comfy.org"

#: Terminal values of ``GET /api/job/{id}/status`` on Comfy Cloud.
#: ``failed`` is not in the published list but is what the API actually
#: returns for a node that raised — omitting it would poll a dead job until
#: the caller's timeout.
_CLOUD_TERMINAL = {
    "success",
    "error",
    "failed",
    "non_retryable_error",
    "lost",
    "cancelled",
}


def _describe_cloud_error(payload: dict) -> str:
    """Extract a readable cause from a failed Comfy Cloud job status payload.

    ``error_message`` is a JSON *string* holding the node id, node type and
    exception. Falls back to the raw text when it isn't parseable.
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


def resolve_backend(explicit: str | None = None) -> str:
    """Resolve which ComfyUI backend to use: ``"local"`` or ``"cloud"``.

    Order of precedence:

    1. an explicit ``backend`` argument (``"local"`` / ``"cloud"``),
    2. the ``COMFYUI_BACKEND`` env var (same values, plus ``"auto"``),
    3. ``auto`` — always local.

    ``auto`` never selects cloud. Cloud is metered, so choosing it must be
    a deliberate act: an unreachable local server is a fault to report, not
    a reason to start spending the user's credits. Opt in per call with
    ``backend="cloud"``, or globally with ``COMFYUI_BACKEND=cloud``.
    """
    choice = (explicit or os.environ.get("COMFYUI_BACKEND") or "auto").strip().lower()
    if choice in ("local", "cloud"):
        return choice
    if choice != "auto":
        raise ValueError(
            f"Invalid backend {choice!r}. Expected 'local', 'cloud', or 'auto'."
        )
    return "local"


class ComfyUIError(Exception):
    """Raised when ComfyUI returns an error or times out.

    ``prompt_id`` is set when the error follows a successful ``submit()``,
    so callers can recover a timed-out-but-still-running job instead of
    losing track of it: poll ``GET /history/{prompt_id}`` directly, or
    pass ``resume_prompt_id`` back into ``ComfyUIVideo.execute()``.
    """

    def __init__(self, message: str, prompt_id: str | None = None) -> None:
        super().__init__(message)
        self.prompt_id = prompt_id


class ComfyUIClient:
    """Client for the ComfyUI REST API.

    The protocol is simple and battle-tested:
      1. POST /prompt           → queue a workflow, get a prompt_id
      2. GET  /history/{id}     → poll until outputs appear
      3. GET  /view?filename=…  → download the generated artifact
      4. POST /upload/image     → stage a local image for I2V workflows
    """

    def __init__(
        self,
        server_url: str | None = None,
        capability: str | None = None,
        backend: str | None = None,
    ) -> None:
        """*capability*, if given (e.g. ``"image"``, ``"video"``), lets a
        per-capability env var (``COMFYUI_{CAPABILITY}_SERVER_URL``) point
        this client at its own ComfyUI instance -- useful when image and
        video generation are split across separate servers/GPUs. Falls back
        to the shared ``COMFYUI_SERVER_URL`` when the capability-specific
        var isn't set, so single-server setups need no extra configuration.

        *backend* selects the transport: ``"local"`` (a ComfyUI server you
        run) or ``"cloud"`` (Comfy Cloud, authenticated with
        ``COMFY_CLOUD_API_KEY``). Pass ``None`` to take the value verbatim
        without auto-resolution -- callers that want ``auto`` should call
        :func:`resolve_backend` first. Cloud puts the ``/api`` prefix into
        ``server_url``, so every route below is shared between backends.
        """
        self.capability = capability
        self._capability_env_var = (
            f"COMFYUI_{capability.upper()}_SERVER_URL" if capability else None
        )
        self.backend = (backend or "local").strip().lower()
        self._headers: dict[str, str] = {}
        self._object_info_cache: dict[str, Any] | None = None

        if self.backend == "cloud":
            base = (
                os.environ.get("COMFY_CLOUD_BASE_URL") or CLOUD_BASE_URL
            ).rstrip("/")
            self.server_url = f"{base}/api"
            api_key = os.environ.get("COMFY_CLOUD_API_KEY", "")
            if api_key:
                self._headers = {"X-API-Key": api_key}
        else:
            resolved = (
                server_url
                or self._capability_url()
                or os.environ.get("COMFYUI_SERVER_URL")
            )
            self.server_url = (resolved or "http://localhost:8188").rstrip("/")
        # Scopes websocket execution events to this client (see wait_ws) and
        # is echoed back on /prompt so the server targets messages to us.
        self.client_id = str(uuid.uuid4())

    @property
    def is_cloud(self) -> bool:
        return self.backend == "cloud"

    def _capability_url(self) -> str | None:
        if self._capability_env_var:
            return os.environ.get(self._capability_env_var)
        return None

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    @property
    def is_default_url(self) -> bool:
        """True if neither the capability-specific nor shared env var is set."""
        return not (self._capability_url() or os.environ.get("COMFYUI_SERVER_URL"))

    def unavailable_reason(self) -> str:
        """Human-readable explanation of why the server can't be reached."""
        if self.is_cloud:
            if not os.environ.get("COMFY_CLOUD_API_KEY"):
                return (
                    "Comfy Cloud selected but COMFY_CLOUD_API_KEY is not set.\n"
                    "Get a key at https://platform.comfy.org and add it to .env."
                )
            return (
                f"Comfy Cloud not reachable at {self.server_url}.\n"
                "Check the key is valid and the workspace subscription is active."
            )
        env_var_hint = self._capability_env_var or "COMFYUI_SERVER_URL"
        if self._capability_env_var:
            env_var_hint += " (or the shared COMFYUI_SERVER_URL)"
        if self.is_default_url:
            return (
                f"No ComfyUI server found at {self.server_url} "
                f"(default — no server URL configured).\n"
                f"Set {env_var_hint} in your .env file to the address of "
                f"your ComfyUI server (e.g. http://localhost:8188)."
            )
        return (
            f"ComfyUI server not reachable at {self.server_url}.\n"
            f"Check that ComfyUI is running and the URL is correct."
        )

    def is_available(self) -> bool:
        """Return True if the ComfyUI backend is reachable."""
        # Cloud has no /system_stats; /api/user is the cheap authenticated ping.
        probe = "/user" if self.is_cloud else "/system_stats"
        if self.is_cloud and not os.environ.get("COMFY_CLOUD_API_KEY"):
            return False
        try:
            resp = requests.get(
                f"{self.server_url}{probe}", headers=self._headers, timeout=10
            )
            return resp.status_code == 200
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Errors
    # ------------------------------------------------------------------

    def _raise_for_cloud_error(self, resp: requests.Response) -> None:
        """Turn a Comfy Cloud error response into a ComfyUIError.

        Cloud uses two envelope shapes: validation errors return
        ``{"error": {"message", "type"}}`` while auth/billing errors return
        ``{"code", "message"}``. 402 and 429 both look like throttling and
        are not -- retrying either can never succeed, so they are surfaced
        as explicit blockers.
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

        hints = {
            401: "COMFY_CLOUD_API_KEY is missing or invalid.",
            402: "Comfy Cloud workspace is out of credits — add credits to continue.",
            429: "Comfy Cloud subscription is inactive — reactivate it to continue.",
        }
        hint = hints.get(resp.status_code)
        msg = f"Comfy Cloud HTTP {resp.status_code}: {detail}"
        if hint:
            msg = f"{msg}\n{hint}"
        raise ComfyUIError(msg)

    # ------------------------------------------------------------------
    # Model discovery
    # ------------------------------------------------------------------

    def list_models(self) -> dict[str, list[str]]:
        """Query ComfyUI for available models, grouped by type.

        Returns a dict like::

            {
                "checkpoints": ["sd_xl_base.safetensors", ...],
                "diffusion_models": ["flux2-dev-nvfp4.safetensors", ...],
                "vae": ["ae.safetensors", ...],
                "clip": ["clip_l.safetensors", ...],
                "loras": ["my_lora.safetensors", ...],
            }
        """
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
                data = self._object_info(node_class)
                options = (
                    data.get(node_class, {})
                    .get("input", {})
                    .get("required", {})
                    .get(field, [[]])[0]
                )
                if isinstance(options, list):
                    result[group] = options
            except Exception:
                result[group] = []
        return result

    def _object_info(self, node_class: str) -> dict:
        """Return ``{node_class: definition}`` for *node_class*.

        Local ComfyUI serves a per-node route. Comfy Cloud does not -- it
        404s ``/object_info/{node_class}`` and only answers the full
        ``/api/object_info``, which is ~10 MB across ~3,700 node classes.
        Fetch that once per client and slice it.
        """
        if not self.is_cloud:
            resp = requests.get(
                f"{self.server_url}/object_info/{node_class}", timeout=10
            )
            resp.raise_for_status()
            return resp.json()

        if self._object_info_cache is None:
            resp = requests.get(
                f"{self.server_url}/object_info", headers=self._headers, timeout=180
            )
            self._raise_for_cloud_error(resp)
            self._object_info_cache = resp.json()
        cache = self._object_info_cache or {}
        return {node_class: cache[node_class]} if node_class in cache else {}

    def check_models(self, required: list[str]) -> tuple[list[str], list[str]]:
        """Check which of *required* model filenames are available.

        Returns ``(found, missing)`` — two lists of filenames.
        """
        all_models: set[str] = set()
        for names in self.list_models().values():
            all_models.update(names)

        found = [m for m in required if m in all_models]
        missing = [m for m in required if m not in all_models]
        return found, missing

    def has_node(self, node_class: str) -> bool:
        """Return whether the connected server exposes a node class."""
        try:
            return node_class in self._object_info(node_class)
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Core cycle
    # ------------------------------------------------------------------

    def submit(self, workflow: dict) -> str:
        """Queue a workflow for execution.  Returns the ``prompt_id``."""
        payload: dict[str, Any] = {
            "prompt": workflow,
            "client_id": self.client_id,
        }
        if self.is_cloud:
            # Partner API nodes (ElevenLabs, Kling, Veo, Recraft, ...) run
            # inside the graph but bill through the Comfy account, and they
            # read the credential from extra_data — not the request header.
            # Without this they fail at execution with "Unauthorized: Please
            # login first to use this node."
            key = os.environ.get("COMFY_CLOUD_API_KEY")
            if key:
                payload["extra_data"] = {"api_key_comfy_org": key}

        resp = requests.post(
            f"{self.server_url}/prompt",
            json=payload,
            headers=self._headers,
            timeout=30,
        )
        if self.is_cloud:
            # Cloud rejects invalid graphs and auth/billing problems with
            # envelopes that carry no node_errors — map them first.
            self._raise_for_cloud_error(resp)
        try:
            data = resp.json()
        except ValueError:
            data = {}
        if data.get("node_errors"):
            raise ComfyUIError(f"Node errors: {json.dumps(data['node_errors'])}")
        if data.get("error"):
            raise ComfyUIError(f"Prompt error: {json.dumps(data['error'])}")
        resp.raise_for_status()
        prompt_id = data.get("prompt_id")
        if not prompt_id:
            raise ComfyUIError(f"No prompt_id in response: {data}")
        return prompt_id

    def poll(
        self,
        prompt_id: str,
        *,
        timeout: int = 600,
        interval: int = 5,
    ) -> dict:
        """Block until *prompt_id* finishes.  Returns the history entry."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            entry = self._history_entry(prompt_id)
            if entry is not None:
                return entry
            time.sleep(interval)
        raise ComfyUIError(
            f"Prompt {prompt_id} did not complete within {timeout}s. "
            f"The job is very likely still running on the ComfyUI server "
            f"(local/custom workflows on modest GPUs routinely exceed the "
            f"client wait) — it was not cancelled. Poll "
            f"{self.recovery_hint(prompt_id)} directly, or call "
            f"generate()/execute() again with a longer timeout and this "
            f"prompt_id to resume waiting without resubmitting.",
            prompt_id=prompt_id,
        )

    def recovery_hint(self, prompt_id: str) -> str:
        """The request a caller can run by hand to check on a job.

        Backend-specific: cloud has no ``/history`` route, so telling a cloud
        user to poll it sends them somewhere that 404s.
        """
        if self.is_cloud:
            return f"GET {self.server_url}/jobs/{prompt_id} (with X-API-Key)"
        return f"GET {self.server_url}/history/{prompt_id}"

    @staticmethod
    def _normalize_cloud_job(job: dict) -> dict:
        """Map a Comfy Cloud ``/api/jobs/{id}`` record to the local shape.

        The flat record's top-level ``status`` is a bare string
        (``"completed"``), but ``execution_status`` beside it is already the
        local ``{status_str, completed, messages}`` dict -- so this is a
        rename, not a translation. Without it, the caller's
        ``status_str == "error"`` check reads every failure as a success.
        """
        return {
            "outputs": job.get("outputs", {}),
            "status": job.get("execution_status", {}),
            "meta": job.get("execution_meta", {}),
        }

    def _cloud_history_entry(self, prompt_id: str) -> dict | None:
        """Cloud equivalent of :meth:`_history_entry`.

        Local ComfyUI treats "a history entry exists" as "the job is done".
        Cloud publishes explicit states, and a queued job already has a
        record -- so the terminal state must be read before the outputs.
        """
        resp = requests.get(
            f"{self.server_url}/job/{prompt_id}/status",
            headers=self._headers,
            timeout=20,
        )
        self._raise_for_cloud_error(resp)
        payload = resp.json()
        state = str(payload.get("status", ""))
        if state not in _CLOUD_TERMINAL:
            return None
        if state != "success":
            # A failed job has no execution_status at all — the detail lives
            # in error_message on this payload, as a JSON string. Surface the
            # node and exception rather than a bare "job failed".
            raise ComfyUIError(
                f"Comfy Cloud job {state}. {_describe_cloud_error(payload)}".strip(),
                prompt_id=prompt_id,
            )

        job = requests.get(
            f"{self.server_url}/jobs/{prompt_id}", headers=self._headers, timeout=30
        )
        self._raise_for_cloud_error(job)
        entry = self._normalize_cloud_job(job.json())
        status = entry.get("status", {})
        if status.get("status_str") == "error":
            raise ComfyUIError(
                f"Execution error: {status.get('messages', [])}", prompt_id=prompt_id
            )
        return entry

    def _history_entry(self, prompt_id: str) -> dict | None:
        """Return a completed history entry, or ``None`` while it is absent."""
        if self.is_cloud:
            return self._cloud_history_entry(prompt_id)
        resp = requests.get(f"{self.server_url}/history/{prompt_id}", timeout=10)
        resp.raise_for_status()
        entry = resp.json().get(prompt_id)
        if entry is None:
            return None
        status = entry.get("status", {})
        if status.get("status_str") == "error":
            msgs = status.get("messages", [])
            raise ComfyUIError(f"Execution error: {msgs}", prompt_id=prompt_id)
        return entry

    def _history_entry_if_reachable(self, prompt_id: str) -> dict | None:
        """Best-effort history probe while the websocket remains usable."""
        try:
            return self._history_entry(prompt_id)
        except ComfyUIError:
            raise
        except Exception:
            return None

    def wait_ws(
        self,
        prompt_id: str,
        *,
        timeout: int = 600,
        interval: int = 5,
        on_progress: Callable[[dict], None] | None = None,
    ) -> dict:
        """Block until *prompt_id* finishes, watching ComfyUI's websocket feed.

        Reacts to server-pushed ``executing``/``progress``/``execution_error``
        events instead of sleeping between REST polls, so completion and
        errors are detected immediately rather than up to *interval* seconds
        late. *on_progress*, if given, is called with each ``progress``
        message's ``data`` dict (``value``, ``max``, ``node``, ``prompt_id``).

        Requires the optional ``websocket-client`` package. Any transport
        failure (missing dependency, connection refused, dropped socket,
        malformed frame) propagates as a plain exception — callers should
        catch it and fall back to :meth:`poll`, which is what :meth:`generate`
        does. A genuine ComfyUI-side execution error or an unmet deadline is
        raised as :class:`ComfyUIError` with ``prompt_id`` set, exactly like
        :meth:`poll`, so ``resume_prompt_id`` recovery works the same way
        regardless of which wait strategy was used.
        """
        import websocket  # websocket-client; optional, see docstring

        # History is authoritative and websocket events are not replayed. The
        # job may already have finished between submit() and this wait call.
        entry = self._history_entry_if_reachable(prompt_id)
        if entry is not None:
            return entry

        ws_url = self.server_url.replace("http://", "ws://", 1).replace(
            "https://", "wss://", 1
        )
        conn = websocket.create_connection(
            f"{ws_url}/ws?clientId={self.client_id}", timeout=10
        )
        try:
            conn.settimeout(interval)
            deadline = time.time() + timeout
            finished = False
            # Close the remaining race between the first history probe and
            # websocket connection establishment. Events after this point are
            # queued on the open socket; earlier completion is in history.
            entry = self._history_entry_if_reachable(prompt_id)
            if entry is not None:
                return entry
            while time.time() < deadline:
                try:
                    raw = conn.recv()
                except websocket.WebSocketTimeoutException:
                    entry = self._history_entry_if_reachable(prompt_id)
                    if entry is not None:
                        return entry
                    continue
                if not isinstance(raw, str):
                    continue  # binary preview-image frame, not a status message
                try:
                    message = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                data = message.get("data", {})
                if data.get("prompt_id") not in (None, prompt_id):
                    continue  # another job sharing this connection
                msg_type = message.get("type")
                if msg_type == "progress":
                    if on_progress:
                        on_progress(data)
                elif msg_type == "execution_error":
                    raise ComfyUIError(f"Execution error: {data}", prompt_id=prompt_id)
                elif msg_type == "executing" and data.get("node") is None:
                    finished = True
                    break
        finally:
            conn.close()

        if not finished:
            entry = self._history_entry_if_reachable(prompt_id)
            if entry is not None:
                return entry
            raise ComfyUIError(
                f"Prompt {prompt_id} did not complete within {timeout}s "
                f"(websocket wait). The job was not cancelled — resume with "
                f"resume_prompt_id={prompt_id!r} and a longer timeout.",
                prompt_id=prompt_id,
            )

        entry = self._history_entry(prompt_id)
        if entry is None:
            raise ComfyUIError(
                f"No history entry for {prompt_id} after completion",
                prompt_id=prompt_id,
            )
        return entry

    def _wait(
        self,
        prompt_id: str,
        *,
        timeout: int,
        interval: int,
        on_progress: Callable[[dict], None] | None = None,
    ) -> dict:
        """Wait for *prompt_id*, preferring the websocket feed over polling.

        Falls back to :meth:`poll` when ``websocket-client`` isn't installed
        or the websocket can't be established/maintained. A genuine
        :class:`ComfyUIError` (execution error or deadline reached) is never
        swallowed by the fallback — only transport-level failures are. The
        fallback gets whatever's left of *timeout*, not a fresh budget, so a
        mid-wait websocket drop can't double the caller's worst-case wait.
        """
        # Cloud's websocket needs token auth and a different event contract;
        # REST polling is already the supported fallback path, so cloud takes
        # it directly rather than carrying a second websocket implementation.
        if self.is_cloud:
            return self.poll(prompt_id, timeout=timeout, interval=interval)

        started = time.time()
        try:
            return self.wait_ws(
                prompt_id, timeout=timeout, interval=interval, on_progress=on_progress
            )
        except ComfyUIError:
            raise
        except Exception:
            remaining = max(timeout - (time.time() - started), 0)
            return self.poll(prompt_id, timeout=remaining, interval=interval)

    def download(
        self,
        filename: str,
        subfolder: str,
        dest: Path,
        folder_type: str = "output",
    ) -> Path:
        """Download an output artifact from the ComfyUI server."""
        resp = requests.get(
            f"{self.server_url}/view",
            params={
                "filename": filename,
                "subfolder": subfolder,
                "type": folder_type,
            },
            headers=self._headers,
            # Cloud answers with a 302 to a short-lived signed storage URL
            # that must be fetched WITHOUT the auth header, so the redirect
            # is followed by hand rather than by requests.
            allow_redirects=not self.is_cloud,
            timeout=120,
        )
        if self.is_cloud and resp.status_code in (301, 302, 303, 307, 308):
            location = resp.headers.get("Location")
            if not location:
                raise ComfyUIError(
                    f"Comfy Cloud returned {resp.status_code} for {filename} "
                    "with no Location header."
                )
            resp = requests.get(location, timeout=300)
        elif self.is_cloud:
            self._raise_for_cloud_error(resp)
        resp.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(resp.content)
        return dest

    def upload_image(self, local_path: Path, name: str) -> str:
        """Upload a local image so it can be referenced by LoadImage nodes.

        Returns the server-side filename.
        """
        with open(local_path, "rb") as f:
            resp = requests.post(
                f"{self.server_url}/upload/image",
                files={"image": (name, f, "image/png")},
                headers=self._headers,
                timeout=60,
            )
        if self.is_cloud:
            self._raise_for_cloud_error(resp)
        resp.raise_for_status()
        return resp.json()["name"]

    # ------------------------------------------------------------------
    # High-level helper
    # ------------------------------------------------------------------

    def generate(
        self,
        workflow: dict,
        output_node: str,
        dest: Path,
        *,
        timeout: int = 600,
        interval: int = 5,
        resume_prompt_id: str | None = None,
        on_progress: Callable[[dict], None] | None = None,
    ) -> list[Path]:
        """Submit → wait → download.  Returns list of artifact paths.

        Pass ``resume_prompt_id`` (from a previous ``ComfyUIError.prompt_id``)
        to skip re-submitting an already-queued/running job and just resume
        waiting on it — the common recovery path after a timeout.

        Waiting prefers ComfyUI's websocket feed (immediate completion/error
        detection, optional live ``on_progress`` callback) and transparently
        falls back to REST polling if ``websocket-client`` isn't installed or
        the connection can't be used. See :meth:`_wait`.
        """
        prompt_id = resume_prompt_id or self.submit(workflow)
        if resume_prompt_id:
            # A prompt resumed by a new client instance was submitted with the
            # original instance's client_id, so its websocket events are not
            # guaranteed to reach this socket. Poll authoritative history.
            entry = self.poll(prompt_id, timeout=timeout, interval=interval)
        else:
            entry = self._wait(
                prompt_id, timeout=timeout, interval=interval, on_progress=on_progress
            )

        outputs = entry.get("outputs", {})
        node_output = outputs.get(output_node, {})

        # ComfyUI stores images/video frames under "images", legacy GIFs
        # under "gifs", and the native SaveAudio node's output under "audio".
        items = (
            node_output.get("images", [])
            or node_output.get("gifs", [])
            or node_output.get("audio", [])
            or node_output.get("video", [])
        )
        if not items:
            raise ComfyUIError(
                f"No output artifacts on node {output_node}. "
                f"Available nodes: {list(outputs.keys())}"
            )

        paths: list[Path] = []
        for i, item in enumerate(items):
            suffix = Path(item["filename"]).suffix
            if len(items) == 1:
                target = dest
            else:
                target = dest.with_stem(f"{dest.stem}_{i:03d}").with_suffix(suffix)
            self.download(
                item["filename"],
                item.get("subfolder", ""),
                target,
                item.get("type", "output"),
            )
            paths.append(target)
        return paths

    # ------------------------------------------------------------------
    # Workflow helpers
    # ------------------------------------------------------------------

    @staticmethod
    def load_workflow(path: Path) -> dict:
        """Load a workflow JSON template from disk."""
        with open(path) as f:
            return json.load(f)

    @staticmethod
    def patch_workflow(workflow: dict, patches: dict[str, dict[str, Any]]) -> dict:
        """Deep-copy *workflow* and apply *patches*.

        *patches* maps ``node_id`` → ``{input_name: value, ...}``.
        """
        w = copy.deepcopy(workflow)
        for node_id, values in patches.items():
            if node_id not in w:
                raise ComfyUIError(
                    f"Node {node_id!r} not found in workflow. "
                    f"Available: {list(w.keys())}"
                )
            for key, val in values.items():
                w[node_id]["inputs"][key] = val
        return w

    @staticmethod
    def random_seed() -> int:
        """Return a random seed suitable for ComfyUI noise nodes."""
        return random.randint(0, 2**32 - 1)
