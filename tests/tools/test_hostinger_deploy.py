"""Tests for hostinger_deploy scaffold/status."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.publishers.hostinger_deploy import HostingerDeploy, SCAFFOLD_FILES, canonical_domain
from tools.tool_registry import ToolRegistry


def test_registry_discovers_hostinger_deploy():
    registry = ToolRegistry()
    registry.discover("tools.publishers")
    assert registry.get("hostinger_deploy") is not None


def test_status_and_scaffold():
    tool = HostingerDeploy()
    status = tool.execute({"action": "status", "domain": "hermestudios.com"})
    assert status.success is True
    assert status.data["compose_exists"] is True
    assert status.data["caddy_exists"] is True
    scaffold = tool.execute({"action": "scaffold", "domain": "hermestudios.com"})
    assert scaffold.success is True
    assert scaffold.data["missing"] == []
    assert scaffold.data["deployed"] is False
    for name in SCAFFOLD_FILES:
        assert (PROJECT_ROOT / "services" / "hermes-api" / name).is_file()
    if scaffold.data.get("compose_valid") is False:
        raise AssertionError(scaffold.data.get("compose_error"))


def test_deploy_without_production_key_is_blocked(monkeypatch):
    monkeypatch.delenv("HERMES_API_KEY", raising=False)
    monkeypatch.setenv("HOSTINGER_API_KEY", "fake")
    monkeypatch.setenv("HOSTINGER_VM_ID", "123")
    result = HostingerDeploy().execute({"action": "deploy"})
    assert result.success is False
    assert "HERMES_API_KEY" in (result.error or "")
    assert result.data["deployed"] is False


def test_deploy_without_hostinger_keys_is_blocked(monkeypatch):
    monkeypatch.setenv("HERMES_API_KEY", "secret-test-key")
    monkeypatch.delenv("HOSTINGER_API_KEY", raising=False)
    monkeypatch.delenv("HOSTINGER_VM_ID", raising=False)
    result = HostingerDeploy().execute({"action": "deploy"})
    assert result.success is False
    assert "HOSTINGER_API_KEY" in (result.error or "")


def test_canonical_domain_maps_hermestudio_shorthand():
    assert canonical_domain("hermestudio.com") == "hermestudios.com"
    assert canonical_domain("https://www.hermestudios.com/health") == "hermestudios.com"
    assert canonical_domain("hermestudios.org") == "hermestudios.com"


def test_dns_status_without_key_is_blocked(monkeypatch):
    monkeypatch.delenv("HOSTINGER_API_KEY", raising=False)
    result = HostingerDeploy().execute(
        {"action": "dns_status", "domain": "hermestudio.com"}
    )
    assert result.success is False
    assert result.data["canonical_domain"] == "hermestudios.com"
    assert result.data["requested_domain"] == "hermestudio.com"
    assert result.data["applied"] is False


def test_dns_apply_without_ipv4_is_blocked(monkeypatch):
    monkeypatch.setenv("HOSTINGER_API_KEY", "fake")
    monkeypatch.delenv("HOSTINGER_VPS_IP", raising=False)
    monkeypatch.delenv("HOSTINGER_VM_ID", raising=False)
    result = HostingerDeploy().execute({"action": "dns_apply", "domain": "hermestudios.com"})
    assert result.success is False
    assert "IPv4" in (result.error or "")


def test_dns_apply_puts_apex_and_www(monkeypatch):
    calls: list[dict] = []

    def fake(self, method, path, payload=None):
        calls.append({"method": method, "path": path, "payload": payload})
        if method == "GET":
            return {
                "ok": True,
                "status_code": 200,
                "body": [
                    {"name": "@", "type": "A", "records": [{"content": "203.0.113.10"}]},
                    {
                        "name": "www",
                        "type": "A",
                        "records": [{"content": "203.0.113.10"}],
                    },
                ],
            }
        return {"ok": True, "status_code": 200, "body": {}}

    monkeypatch.setenv("HOSTINGER_API_KEY", "fake")
    monkeypatch.setattr(HostingerDeploy, "_hostinger_request", fake)
    result = HostingerDeploy().execute(
        {"action": "dns_apply", "domain": "hermestudio.com", "ipv4": "203.0.113.10"}
    )
    assert result.success is True
    put = next(call for call in calls if call["method"] == "PUT")
    assert put["path"] == "/api/dns/v1/zones/hermestudios.com"
    names = [item["name"] for item in put["payload"]["zone"]]
    assert names == ["@", "www"]
    assert result.data["applied"] is True
    assert result.data["target_ipv4"] == "203.0.113.10"
    assert result.data["canonical_domain"] == "hermestudios.com"
