"""Grok/GPT tools become available via workstation OAuth without API keys."""

from __future__ import annotations

from tools.base_tool import ToolStatus
from tools.graphics.grok_image import GrokImage
from tools.graphics.openai_image import OpenAIImage
from tools.video.grok_video import GrokVideo
from tools.video.sora_video import SoraVideo
from tools.audio.openai_tts import OpenAITTS


def test_grok_image_available_via_oauth(monkeypatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.setattr(
        "lib.oauth_connectors.is_authenticated",
        lambda connector_id: connector_id == "grok",
    )
    assert GrokImage().get_status() == ToolStatus.AVAILABLE


def test_grok_video_available_via_oauth(monkeypatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.setattr(
        "lib.oauth_connectors.is_authenticated",
        lambda connector_id: connector_id == "grok",
    )
    assert GrokVideo().get_status() == ToolStatus.AVAILABLE


def test_openai_image_available_via_oauth(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(
        "lib.oauth_connectors.is_authenticated",
        lambda connector_id: connector_id == "gpt",
    )
    assert OpenAIImage().get_status() == ToolStatus.AVAILABLE


def test_sora_and_openai_tts_still_need_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr("lib.oauth_connectors.is_authenticated", lambda connector_id: True)
    assert SoraVideo().get_status() == ToolStatus.UNAVAILABLE
    assert OpenAITTS().get_status() == ToolStatus.UNAVAILABLE


def test_openai_oauth_execute_writes_bytes(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(
        "lib.oauth_connectors.is_authenticated",
        lambda connector_id: connector_id == "gpt",
    )
    monkeypatch.setattr(
        "lib.oauth_connectors.generate_gpt_oauth_image",
        lambda prompt, aspect_ratio="square", quality="medium": b"PNGDATA",
    )
    out = tmp_path / "oauth.png"
    result = OpenAIImage().execute({"prompt": "a lamp", "output_path": str(out)})
    assert result.success
    assert result.data["auth_source"] == "oauth"
    assert out.read_bytes() == b"PNGDATA"
    assert "PNGDATA" not in str(result.data)
    dumped = str(result.data)
    assert "access_token" not in dumped
    assert "Bearer" not in dumped
