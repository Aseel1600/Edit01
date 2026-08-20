"""Tests for hostinger_deploy scaffold/status."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.publishers.hostinger_deploy import HostingerDeploy
from tools.tool_registry import ToolRegistry


def test_registry_discovers_hostinger_deploy():
    registry = ToolRegistry()
    registry.discover("tools")
    assert registry.get("hostinger_deploy") is not None


def test_status_and_scaffold():
    tool = HostingerDeploy()
    status = tool.execute({"action": "status", "domain": "hermestudios.com"})
    assert status.success is True
    assert status.data["compose_exists"] is True
    scaffold = tool.execute({"action": "scaffold", "domain": "hermestudios.com"})
    assert scaffold.success is True
    assert scaffold.data["missing"] == []


def test_deploy_without_keys_is_blocked(monkeypatch):
    monkeypatch.delenv("HOSTINGER_API_KEY", raising=False)
    monkeypatch.delenv("HOSTINGER_VM_ID", raising=False)
    result = HostingerDeploy().execute({"action": "deploy"})
    assert result.success is False
    assert "HOSTINGER_API_KEY" in (result.error or "")
