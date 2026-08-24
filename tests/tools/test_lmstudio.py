"""Tests for the LM Studio local client tool."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.llm.lmstudio import LMStudio
from tools.tool_registry import ToolRegistry


class _FakeResp:
    status = 200

    def read(self):
        return json.dumps({"data": [{"id": "qwen/qwen3-coder-30b"}]}).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_registry_discovers_lmstudio():
    registry = ToolRegistry()
    registry.discover("tools")
    assert registry.get("lmstudio") is not None


def test_health_success():
    with patch("tools.llm.lmstudio.urlopen", return_value=_FakeResp()):
        result = LMStudio().execute({"action": "health"})
    assert result.success is True
    assert result.data["reachable"] is True
    assert "qwen/qwen3-coder-30b" in result.data["models"]
    assert result.cost_usd == 0.0


def test_chat_requires_prompt():
    result = LMStudio().execute({"action": "chat"})
    assert result.success is False
    assert "messages or prompt" in (result.error or "")
