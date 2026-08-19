"""OAuth connector helpers never expose tokens in public status."""

from __future__ import annotations

import json
import time

from lib import oauth_connectors as oauth


class _FakeKeyring:
    def __init__(self, stores: dict[tuple[str, str], str] | None = None):
        self.stores = stores or {}

    def get_password(self, service: str, account: str):
        return self.stores.get((service, account))

    def set_password(self, service: str, account: str, password: str):
        self.stores[(service, account)] = password


def test_auth_status_omits_tokens(monkeypatch):
    fake = _FakeKeyring(
        {
            ("com.cursor.grok-media-mcp", "xai-oauth:default"): json.dumps(
                {
                    "access_token": "secret-access",
                    "refresh_token": "secret-refresh",
                    "expires_at": time.time() + 3600,
                }
            )
        }
    )
    monkeypatch.setattr(oauth, "_load_raw", lambda connector_id: json.loads(
        fake.get_password(*oauth._store(connector_id))
    ))
    status = oauth.auth_status("grok")
    dumped = json.dumps(status)
    assert status["authenticated"] is True
    assert "secret-access" not in dumped
    assert "secret-refresh" not in dumped
    assert "access_token" not in dumped


def test_unauthenticated_when_store_empty(monkeypatch):
    monkeypatch.setattr(oauth, "_load_raw", lambda connector_id: None)
    assert oauth.is_authenticated("grok") is False
    assert oauth.auth_status("gpt")["authenticated"] is False


def test_grok_bearer_prefers_api_key(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "env-key")
    monkeypatch.setattr(oauth, "get_access_token", lambda connector_id: "oauth-token")
    assert oauth.grok_bearer_token() == "env-key"


def test_grok_bearer_uses_oauth_without_api_key(monkeypatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.setattr(oauth, "get_access_token", lambda connector_id: "oauth-token")
    assert oauth.grok_bearer_token() == "oauth-token"


def test_extract_image_b64_from_nested_event():
    event = {
        "type": "response.completed",
        "response": {
            "output": [
                {"type": "image_generation_call", "result": "abc123"}
            ]
        },
    }
    assert oauth._extract_image_b64(event) == "abc123"
