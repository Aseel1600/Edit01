"""Shared fixtures for contract tests."""

from __future__ import annotations

import pytest

from tools.tool_registry import ToolRegistry


@pytest.fixture(autouse=True)
def neutral_backend_env(monkeypatch) -> None:
    """Pin provider-selecting env vars so contract tests are deterministic.

    A developer's real ``.env`` can route the ComfyUI tools at Comfy Cloud
    (``COMFYUI_BACKEND=cloud``), which would otherwise change what these
    tests observe -- server URLs, cost estimates -- depending on whose
    machine they run on. Contract tests assert the default local contract,
    so the ambient values are cleared here. Tests that mean to exercise the
    cloud path set the backend explicitly.
    """
    for var in ("COMFYUI_BACKEND", "COMFY_CLOUD_API_KEY"):
        monkeypatch.delenv(var, raising=False)


@pytest.fixture()
def isolated_tool_registry(monkeypatch) -> ToolRegistry:
    """Provide a registry singleton replacement scoped to one test."""
    test_registry = ToolRegistry()
    monkeypatch.setattr("tools.tool_registry.registry", test_registry)
    return test_registry
