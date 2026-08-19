"""Workstation Grok/GPT OAuth credentials for OpenMontage tools.

Reads the same macOS Keychain items as `grok-media-mcp` and `gpt-media-mcp`.
Never logs, prints, or returns raw OAuth tokens to callers except
`get_access_token`, which tools must use only as an Authorization header.
"""

from __future__ import annotations

import base64
import json
import threading
import time
from typing import Any

GROK_CONNECTOR = "grok"
GPT_CONNECTOR = "gpt"

_GROK_STORE = ("com.cursor.grok-media-mcp", "xai-oauth:default")
_GPT_STORE = ("com.cursor.gpt-media-mcp", "openai-codex:default")

_XAI_CLIENT_ID = "b1a00492-073a-47ea-816f-4c329264a828"
_XAI_TOKEN_ENDPOINT = "https://auth.x.ai/oauth2/token"

_OPENAI_CODEX_CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"
_OPENAI_TOKEN_ENDPOINT = "https://auth.openai.com/oauth/token"
_CODEX_RESPONSES_URL = "https://chatgpt.com/backend-api/codex/responses"
_CODEX_HOST_MODEL = "gpt-5.5"
_CODEX_IMAGE_MODEL = "gpt-image-2"
_CODEX_SIZES = {
    "landscape": "1536x1024",
    "square": "1024x1024",
    "portrait": "1024x1536",
}
_MAX_IMAGE_BYTES = 50 * 1024 * 1024

_locks = {
    GROK_CONNECTOR: threading.Lock(),
    GPT_CONNECTOR: threading.Lock(),
}


class OAuthError(RuntimeError):
    pass


class OAuthEntitlementError(OAuthError):
    pass


def _store(connector_id: str) -> tuple[str, str]:
    if connector_id == GROK_CONNECTOR:
        return _GROK_STORE
    if connector_id == GPT_CONNECTOR:
        return _GPT_STORE
    raise OAuthError(f"unsupported oauth connector: {connector_id}")


def _jwt_exp(token: str) -> float:
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload))
        return float(claims.get("exp", 0))
    except (IndexError, TypeError, ValueError, json.JSONDecodeError):
        return 0.0


def _chatgpt_account_id(access_token: str) -> str | None:
    try:
        payload = access_token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload))
        auth_claims = claims.get("https://api.openai.com/auth")
        value = auth_claims.get("chatgpt_account_id") if isinstance(auth_claims, dict) else None
        return value if isinstance(value, str) and value else None
    except (IndexError, TypeError, ValueError, json.JSONDecodeError):
        return None


def _load_raw(connector_id: str) -> dict[str, Any] | None:
    import keyring

    service, account = _store(connector_id)
    raw = keyring.get_password(service, account)
    if not raw:
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise OAuthError("The saved OAuth credential is malformed; log in again.") from exc
    if not isinstance(value, dict):
        raise OAuthError("The saved OAuth credential has an invalid shape.")
    return value


def _save_raw(connector_id: str, value: dict[str, Any]) -> None:
    import keyring

    service, account = _store(connector_id)
    keyring.set_password(service, account, json.dumps(value, separators=(",", ":")))


def auth_status(connector_id: str) -> dict[str, Any]:
    """Public status only. Never includes tokens."""
    try:
        credentials = _load_raw(connector_id)
    except OAuthError as exc:
        return {"authenticated": False, "connector": connector_id, "error": str(exc)}
    except Exception as exc:
        return {
            "authenticated": False,
            "connector": connector_id,
            "error": f"OAuth store unavailable: {exc.__class__.__name__}",
        }
    if not credentials:
        return {"authenticated": False, "connector": connector_id}
    expires_at = float(credentials.get("expires_at") or _jwt_exp(str(credentials.get("access_token") or "")))
    return {
        "authenticated": True,
        "connector": connector_id,
        "expires_in": max(0, int(expires_at - time.time())) if expires_at else None,
        "credential_store": _store(connector_id)[0],
    }


def is_authenticated(connector_id: str) -> bool:
    return bool(auth_status(connector_id).get("authenticated"))


def get_access_token(connector_id: str) -> str | None:
    """Return a valid access token, or None when the user has not signed in."""
    lock = _locks.get(connector_id)
    if lock is None:
        raise OAuthError(f"unsupported oauth connector: {connector_id}")
    with lock:
        credentials = _load_raw(connector_id)
        if not credentials:
            return None
        access_token = str(credentials.get("access_token") or "")
        expires_at = float(credentials.get("expires_at") or _jwt_exp(access_token))
        if access_token and (not expires_at or expires_at - time.time() > 180):
            return access_token
        refresh_token = str(credentials.get("refresh_token") or "")
        if not refresh_token:
            raise OAuthError("No refresh token is available. Log in again.")
        if connector_id == GROK_CONNECTOR:
            next_credentials = _refresh_grok(refresh_token)
        else:
            next_credentials = _refresh_gpt(refresh_token)
        credentials.update(next_credentials)
        _save_raw(connector_id, credentials)
        return str(credentials["access_token"])


def _refresh_grok(refresh_token: str) -> dict[str, Any]:
    import requests

    response = requests.post(
        _XAI_TOKEN_ENDPOINT,
        data={
            "grant_type": "refresh_token",
            "client_id": _XAI_CLIENT_ID,
            "refresh_token": refresh_token,
        },
        timeout=30,
    )
    if response.status_code == 403:
        raise OAuthEntitlementError(
            "xAI denied OAuth API access for this subscription (HTTP 403)."
        )
    if response.status_code != 200:
        raise OAuthError(f"xAI token refresh failed with HTTP {response.status_code}.")
    payload = response.json()
    access_token = payload.get("access_token")
    if not access_token:
        raise OAuthError("xAI refresh returned no access token.")
    expires_in = max(60, int(payload.get("expires_in", 3600)))
    return {
        "access_token": access_token,
        "refresh_token": payload.get("refresh_token") or refresh_token,
        "expires_at": time.time() + expires_in,
    }


def _refresh_gpt(refresh_token: str) -> dict[str, Any]:
    import requests

    response = requests.post(
        _OPENAI_TOKEN_ENDPOINT,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": _OPENAI_CODEX_CLIENT_ID,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    if response.status_code != 200:
        raise OAuthError(f"Codex token refresh failed with HTTP {response.status_code}.")
    payload = response.json()
    access_token = payload.get("access_token")
    if not access_token:
        raise OAuthError("Codex refresh returned no access token.")
    return {
        "access_token": access_token,
        "refresh_token": payload.get("refresh_token") or refresh_token,
        "expires_at": _jwt_exp(str(access_token)),
    }


def grok_bearer_token() -> str | None:
    """API key wins if set; otherwise the Grok OAuth access token."""
    import os

    api_key = os.environ.get("XAI_API_KEY")
    if api_key:
        return api_key
    return get_access_token(GROK_CONNECTOR)


def grok_auth_available() -> bool:
    import os

    return bool(os.environ.get("XAI_API_KEY") or is_authenticated(GROK_CONNECTOR))


def gpt_image_auth_available() -> bool:
    import os

    return bool(os.environ.get("OPENAI_API_KEY") or is_authenticated(GPT_CONNECTOR))


def _iter_sse_json(response: Any) -> Any:
    event_name: str | None = None
    data_lines: list[str] = []

    def flush() -> dict[str, Any] | None:
        nonlocal event_name, data_lines
        if not data_lines:
            event_name = None
            return None
        raw = "\n".join(data_lines).strip()
        event = event_name
        event_name = None
        data_lines = []
        if not raw or raw == "[DONE]":
            return None
        value = json.loads(raw)
        if not isinstance(value, dict):
            return None
        if event and "type" not in value:
            value["type"] = event
        return value

    for line in response.iter_lines():
        if isinstance(line, bytes):
            line = line.decode("utf-8", errors="replace")
        if line == "":
            value = flush()
            if value is not None:
                yield value
        elif line.startswith(":"):
            continue
        elif line.startswith("event:"):
            event_name = line[6:].strip()
        elif line.startswith("data:"):
            data_lines.append(line[5:].lstrip())
    value = flush()
    if value is not None:
        yield value


def _extract_image_b64(value: Any) -> str | None:
    found: str | None = None
    if isinstance(value, dict):
        if value.get("type") == "image_generation_call":
            result = value.get("result")
            if isinstance(result, str) and result:
                found = result
        partial = value.get("partial_image_b64")
        if isinstance(partial, str) and partial:
            found = partial
        for child in value.values():
            nested = _extract_image_b64(child)
            if nested:
                found = nested
    elif isinstance(value, list):
        for child in value:
            nested = _extract_image_b64(child)
            if nested:
                found = nested
    return found


def generate_gpt_oauth_image(
    prompt: str,
    *,
    aspect_ratio: str = "square",
    quality: str = "medium",
) -> bytes:
    """Best-effort GPT Image 2 via ChatGPT/Codex OAuth. No API key."""
    import requests

    prompt = prompt.strip()
    if not prompt or len(prompt) > 20_000:
        raise OAuthError("Prompt must contain 1–20,000 characters.")
    if aspect_ratio not in _CODEX_SIZES:
        raise OAuthError("aspect_ratio must be landscape, square, or portrait.")
    if quality not in {"low", "medium", "high"}:
        raise OAuthError("quality must be low, medium, or high.")

    token = get_access_token(GPT_CONNECTOR)
    if not token:
        raise OAuthError("GPT OAuth is not signed in. Run gpt-media-mcp login.")

    headers = {
        "Accept": "text/event-stream",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "codex_cli_rs/0.0.0 (OpenMontage)",
        "originator": "codex_cli_rs",
    }
    account_id = _chatgpt_account_id(token)
    if account_id:
        headers["ChatGPT-Account-ID"] = account_id

    body = {
        "model": _CODEX_HOST_MODEL,
        "store": False,
        "instructions": (
            "You are an assistant that must fulfill image generation and image "
            "editing requests by using the image_generation tool when provided."
        ),
        "input": [
            {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}],
            }
        ],
        "tools": [
            {
                "type": "image_generation",
                "model": _CODEX_IMAGE_MODEL,
                "size": _CODEX_SIZES[aspect_ratio],
                "quality": quality,
                "output_format": "png",
                "background": "opaque",
                "partial_images": 1,
            }
        ],
        "stream": True,
    }

    image_b64: str | None = None
    with requests.post(
        _CODEX_RESPONSES_URL,
        headers=headers,
        json=body,
        stream=True,
        timeout=300,
    ) as response:
        if response.status_code >= 400:
            raise OAuthError(
                f"Codex Responses API returned HTTP {response.status_code}."
            )
        for event in _iter_sse_json(response):
            found = _extract_image_b64(event)
            if found:
                image_b64 = found

    if not image_b64:
        raise OAuthError(
            "Codex returned no image. The hosted model may decline image_generation; "
            "this path is best-effort and is not an API-key fallback."
        )
    raw = base64.b64decode(image_b64)
    if len(raw) > _MAX_IMAGE_BYTES:
        raise OAuthError("Generated image exceeds the 50 MiB safety limit.")
    return raw
