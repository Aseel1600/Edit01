"""Tests for the Hermes API FastAPI app."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

APP_PATH = PROJECT_ROOT / "services" / "hermes-api" / "app.py"


def _load_app():
    spec = importlib.util.spec_from_file_location("hermes_api_app", APP_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def client(monkeypatch):
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    monkeypatch.setenv("PUBLIC_DOMAIN", "localhost")
    monkeypatch.delenv("HERMES_API_KEY", raising=False)
    monkeypatch.delenv("HERMES_REQUIRE_AUTH", raising=False)
    monkeypatch.delenv("INFERENCE_BASE_URL", raising=False)
    monkeypatch.delenv("INFERENCE_BACKEND", raising=False)
    monkeypatch.delenv("HERMES_MAX_INFLIGHT", raising=False)
    module = _load_app()
    return TestClient(module.app), module


def test_health_and_landing(client):
    http, _ = client
    livez = http.get("/livez")
    assert livez.status_code == 200
    assert livez.json()["ok"] is True
    readyz = http.get("/readyz")
    assert readyz.status_code == 200
    health = http.get("/health")
    assert health.status_code == 200
    body = health.json()
    assert body["ok"] is True
    assert body["service"] == "hermes-api"
    landing = http.get("/")
    assert landing.status_code == 200
    assert b"Hermes Studios" in landing.content
    assert "inference" in body
    assert body["inference"]["backend"] == "lm_studio"
    assert body["inference"]["max_inflight"] == 32


def test_unauthenticated_chat_rejected_when_key_set(monkeypatch):
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    monkeypatch.setenv("PUBLIC_DOMAIN", "hermestudios.com")
    monkeypatch.setenv("HERMES_API_KEY", "secret-test-key")
    module = _load_app()
    http = TestClient(module.app)
    res = http.post("/v1/chat/completions", json={"messages": [{"role": "user", "content": "hi"}]})
    assert res.status_code == 401


def test_missing_production_key_refuses_inference(monkeypatch):
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    monkeypatch.setenv("PUBLIC_DOMAIN", "hermestudios.com")
    monkeypatch.delenv("HERMES_API_KEY", raising=False)
    module = _load_app()
    http = TestClient(module.app)
    res = http.post("/v1/chat/completions", json={"messages": [{"role": "user", "content": "hi"}]})
    assert res.status_code == 503
    livez = http.get("/livez")
    assert livez.status_code == 200
    readyz = http.get("/readyz")
    assert readyz.status_code == 503


def test_inference_base_url_preferred(monkeypatch):
    monkeypatch.setenv("INFERENCE_BASE_URL", "http://vllm.internal:8000/v1")
    monkeypatch.setenv("INFERENCE_BACKEND", "vllm")
    monkeypatch.setenv("LM_STUDIO_BASE_URL", "http://127.0.0.1:1234/v1")
    module = _load_app()
    assert module._inference_base() == "http://vllm.internal:8000/v1"
    assert module._inference_backend() == "vllm"
    assert module._lm_base() == "http://vllm.internal:8000/v1"
