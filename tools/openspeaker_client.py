"""Shared HTTP client for the OpenSpeaker API (api.ai33.pro).

All OpenSpeaker generation endpoints are asynchronous: the create call returns a
`task_id`, and the caller polls `GET /v1/task/{task_id}` until the task reaches a
terminal state. This module centralises auth, polling, rate-limit handling, and
artifact download so the individual tools stay thin.

See docs/openspeaker-api.md for the full API surface.
"""

from __future__ import annotations

import os
import random
import time
from pathlib import Path
from typing import Any, Optional

import requests

# Importing base_tool loads .env into os.environ (module-level side effect), so
# this client works when used directly, not only via a BaseTool subclass.
# base_tool does not import this module, so there is no cycle.
import tools.base_tool  # noqa: F401

DEFAULT_BASE_URL = "https://api.ai33.pro"

# Terminal task states reported by GET /v1/task/{id}.
_DONE = "done"
_FAILED_STATES = {"failed", "error", "cancelled", "canceled"}

# Error codes that mean "try again", not "this request was wrong".
_TRANSIENT_CODES = {"server_busy", "rate_limited", "too_many_requests"}


class OpenSpeakerError(RuntimeError):
    """Raised when the OpenSpeaker API returns an unrecoverable error."""


def api_key() -> str:
    """Return the configured key, or "" when unset."""
    return (os.environ.get("OPENSPEAKER_API_KEY") or "").strip()


def base_url() -> str:
    return (os.environ.get("OPENSPEAKER_BASE_URL") or DEFAULT_BASE_URL).strip().rstrip("/")


def _headers() -> dict[str, str]:
    key = api_key()
    if not key:
        raise OpenSpeakerError(
            "OPENSPEAKER_API_KEY is not set. Add it to .env "
            "(see docs/openspeaker-api.md)."
        )
    return {"xi-api-key": key}


def _sleep_for_retry(response: requests.Response, attempt: int) -> float:
    """Honour Retry-After when present, else exponential backoff with jitter."""
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        try:
            return max(0.0, float(retry_after))
        except ValueError:
            pass
    return min(30.0, (2 ** attempt)) + random.uniform(0, 1)


def request(
    method: str,
    path: str,
    *,
    data: Optional[dict[str, Any]] = None,
    files: Optional[list] = None,
    json_body: Optional[dict[str, Any]] = None,
    params: Optional[dict[str, Any]] = None,
    timeout: int = 60,
    max_retries: int = 4,
) -> dict[str, Any]:
    """Make an authenticated request, retrying 429s and transient 5xxs.

    HTTP 429 is a rate-limit violation (honour Retry-After); HTTP 503 with code
    `server_busy` is capacity pressure and is also retryable per the API docs.
    """
    url = f"{base_url()}{path}"
    last_error = ""
    for attempt in range(max_retries + 1):
        try:
            response = requests.request(
                method,
                url,
                headers=_headers(),
                data=data,
                files=files,
                json=json_body,
                params=params,
                timeout=timeout,
            )
        except requests.RequestException as exc:
            last_error = f"network error: {exc}"
            if attempt >= max_retries:
                break
            time.sleep(min(30.0, 2 ** attempt) + random.uniform(0, 1))
            continue

        if response.status_code == 429 or (
            response.status_code == 503 and "server_busy" in response.text
        ):
            last_error = f"HTTP {response.status_code}: {response.text[:200]}"
            if attempt >= max_retries:
                break
            time.sleep(_sleep_for_retry(response, attempt))
            continue

        if response.status_code >= 400:
            raise OpenSpeakerError(f"HTTP {response.status_code}: {response.text[:400]}")

        try:
            payload = response.json()
        except ValueError as exc:
            raise OpenSpeakerError(f"Non-JSON response from {path}: {exc}") from exc

        # The API also signals back-pressure as HTTP 200 with an error body
        # ({"success": false, "code": "server_busy"}). Without this branch the
        # caller would treat the envelope as a task payload and poll forever.
        if isinstance(payload, dict) and payload.get("success") is False:
            code = str(payload.get("code") or "")
            message = str(payload.get("message") or "")
            if code in _TRANSIENT_CODES:
                last_error = f"{code}: {message}"
                if attempt >= max_retries:
                    break
                time.sleep(_sleep_for_retry(response, attempt))
                continue
            raise OpenSpeakerError(f"{path} returned {code or 'error'}: {message}")

        return payload

    raise OpenSpeakerError(f"{path} failed after {max_retries} retries. {last_error}")


_TRANSIENT_MARKERS = ("server_busy", "HTTP 503", "HTTP 429", "network error")


def poll_task(
    task_id: str,
    *,
    timeout_seconds: int = 900,
    interval_seconds: float = 3.0,
    on_progress=None,
) -> dict[str, Any]:
    """Poll GET /v1/task/{id} until terminal. Returns the final task payload.

    Detail polling costs 1 rate-limit token per call, so this uses a steady
    interval rather than a tight loop.

    A busy poll endpoint must not abort the whole wait: the generation task is
    already running and paid for. Transient poll failures (`server_busy`, 429,
    network blips) are absorbed and retried until the overall deadline; only a
    genuinely failed task, or repeated hard errors, stop the loop.
    """
    deadline = time.time() + timeout_seconds
    last_progress = -1
    hard_errors = 0
    while time.time() < deadline:
        try:
            # max_retries=0: this loop owns the retry cadence, not request().
            task = request("GET", f"/v1/task/{task_id}", timeout=30, max_retries=0)
            hard_errors = 0
        except OpenSpeakerError as exc:
            message = str(exc)
            if any(marker in message for marker in _TRANSIENT_MARKERS):
                time.sleep(min(15.0, interval_seconds * 2) + random.uniform(0, 1))
                continue
            hard_errors += 1
            if hard_errors >= 3:
                raise
            time.sleep(interval_seconds)
            continue

        status = str(task.get("status", "")).lower()
        progress = task.get("progress")
        if on_progress and progress is not None and progress != last_progress:
            last_progress = progress
            on_progress(progress, status)

        if status == _DONE:
            return task
        if status in _FAILED_STATES:
            raise OpenSpeakerError(
                f"Task {task_id} {status}: {task.get('error_message') or 'no error message'}"
            )
        time.sleep(interval_seconds)

    raise OpenSpeakerError(f"Task {task_id} did not finish within {timeout_seconds}s")


def download(url: str, output_path: Path, *, timeout: int = 300) -> Path:
    """Stream a result URL to disk. Result URLs are pre-signed — no auth header."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        with open(output_path, "wb") as handle:
            for chunk in response.iter_content(chunk_size=1 << 16):
                if chunk:
                    handle.write(chunk)
    return output_path


def credits_remaining() -> Optional[int]:
    """Return the account credit balance, or None when the call fails."""
    try:
        payload = request("GET", "/v1/credits", timeout=20)
    except OpenSpeakerError:
        return None
    value = payload.get("credits")
    return int(value) if isinstance(value, (int, float, str)) and str(value).isdigit() else value
