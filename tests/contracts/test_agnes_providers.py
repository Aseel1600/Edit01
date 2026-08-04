"""Contract tests for the Agnes AI (Sapiens AI) image and video provider tools.

These tests verify that both tools satisfy the BaseTool contract without
requiring a real AGNES_API_KEY or making any API calls.

Run: pytest tests/contracts/test_agnes_providers.py -v
"""

import pytest

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)
from tools.graphics.agnes_image import AgnesImage
from tools.video.agnes_video import AgnesVideo


# ------------------------------------------------------------------
# Contract compliance
# ------------------------------------------------------------------

class TestContract:

    def test_inherits_base_tool(self):
        assert issubclass(AgnesImage, BaseTool)
        assert issubclass(AgnesVideo, BaseTool)

    def test_has_required_identity(self):
        for tool in (AgnesImage(), AgnesVideo()):
            assert tool.name
            assert tool.version
            assert tool.provider == "agnes"
            assert tool.tier == ToolTier.GENERATE
            assert tool.stability == ToolStability.EXPERIMENTAL
            assert tool.runtime == ToolRuntime.API

    def test_image_identity(self):
        tool = AgnesImage()
        assert tool.name == "agnes_image"
        assert tool.capability == "image_generation"

    def test_video_identity(self):
        tool = AgnesVideo()
        assert tool.name == "agnes_video"
        assert tool.capability == "video_generation"

    def test_execution_modes(self):
        assert AgnesImage().execution_mode == ExecutionMode.SYNC
        assert AgnesVideo().execution_mode == ExecutionMode.SYNC

    def test_has_input_schema(self):
        for tool, expected_required in (
            (AgnesVideo(), ["prompt"]),
            (AgnesImage(), ["prompt", "size"]),
        ):
            schema = tool.input_schema
            assert schema.get("type") == "object"
            props = schema.get("properties", {})
            required = schema.get("required", [])
            assert required == expected_required
            for field in required:
                assert field in props

    def test_has_agent_skills(self):
        assert "agnes-image" in AgnesImage().agent_skills
        assert "agnes-video" in AgnesVideo().agent_skills

    def test_has_fallbacks(self):
        tool = AgnesVideo()
        assert "seedance_video" in tool.fallback_tools
        assert "kling_video" in tool.fallback_tools
        tool = AgnesImage()
        assert "flux_image" in tool.fallback_tools

    def test_has_install_instructions(self):
        for tool in (AgnesImage(), AgnesVideo()):
            assert "AGNES_API_KEY" in tool.install_instructions

    def test_declares_env_dependency(self):
        """env:AGNES_API_KEY must be declared so status/registry reflect it."""
        for tool in (AgnesImage(), AgnesVideo()):
            assert "env:AGNES_API_KEY" in tool.dependencies

    def test_get_info_returns_dict(self):
        info = AgnesVideo().get_info()
        assert isinstance(info, dict)
        assert info["name"] == "agnes_video"
        assert info["provider"] == "agnes"
        assert info["runtime"] == "api"

    def test_status_unavailable_without_key(self, monkeypatch):
        monkeypatch.delenv("AGNES_API_KEY", raising=False)
        assert AgnesImage().get_status() == ToolStatus.UNAVAILABLE
        assert AgnesVideo().get_status() == ToolStatus.UNAVAILABLE

    def test_status_available_with_key(self, monkeypatch):
        monkeypatch.setenv("AGNES_API_KEY", "fake-key")
        assert AgnesImage().get_status() == ToolStatus.AVAILABLE
        assert AgnesVideo().get_status() == ToolStatus.AVAILABLE

    def test_has_resource_profile(self):
        for tool in (AgnesImage(), AgnesVideo()):
            rp = tool.resource_profile
            assert rp.network_required is True
            assert rp.vram_mb == 0

    def test_has_retry_policy(self):
        for tool in (AgnesImage(), AgnesVideo()):
            assert tool.retry_policy.max_retries >= 0

    def test_has_side_effects(self):
        for tool in (AgnesImage(), AgnesVideo()):
            side = tool.side_effects
            assert len(side) > 0
            assert any("API" in s for s in side)

    def test_has_user_visible_verification(self):
        assert len(AgnesVideo().user_visible_verification) > 0

    def test_lazy_imports_requests(self, monkeypatch):
        import importlib
        import sys

        for mod_name in ("tools.video.agnes_video", "tools.graphics.agnes_image"):
            if "requests" in sys.modules:
                monkeypatch.delitem(sys.modules, "requests")
            importlib.reload(sys.modules[mod_name])

    def test_estimate_cost_returns_float(self):
        cost = AgnesVideo().estimate_cost({"prompt": "x", "num_frames": 121})
        assert isinstance(cost, float)
        assert cost == 0.0

    def test_dry_run_returns_dict(self):
        for tool in (AgnesImage(), AgnesVideo()):
            result = tool.dry_run({"prompt": "test"})
            assert isinstance(result, dict)
            assert result["tool"] == tool.name


# ------------------------------------------------------------------
# Idempotency keys
# ------------------------------------------------------------------

class TestIdempotencyKeys:

    def test_video_includes_output_affecting_fields(self):
        fields = AgnesVideo().idempotency_key_fields
        for field in (
            "prompt",
            "operation",
            "num_frames",
            "frame_rate",
            "seed",
            "aspect_ratio",
            "negative_prompt",
            "image_url",
            "image_path",
            "image_urls",
            "image_paths",
        ):
            assert field in fields, f"missing idempotency field: {field}"

    def test_video_excludes_execution_only_fields(self):
        fields = AgnesVideo().idempotency_key_fields
        for field in ("output_path",):
            assert field not in fields

    def test_image_includes_output_affecting_fields(self):
        fields = AgnesImage().idempotency_key_fields
        for field in ("prompt", "size", "model", "image_url", "image_path", "image_urls", "image_paths"):
            assert field in fields, f"missing idempotency field: {field}"

    def test_video_differs_on_operation(self):
        tool = AgnesVideo()
        base = {"prompt": "x"}
        assert tool.idempotency_key(base) != tool.idempotency_key(
            {**base, "operation": "image_to_video"}
        )

    def test_video_differs_on_num_frames(self):
        tool = AgnesVideo()
        base = {"prompt": "x"}
        assert tool.idempotency_key(base) != tool.idempotency_key(
            {**base, "num_frames": 241}
        )

    def test_image_differs_on_model(self):
        tool = AgnesImage()
        base = {"prompt": "x", "size": "1024x768"}
        assert tool.idempotency_key(base) != tool.idempotency_key(
            {**base, "model": "agnes-image-2.0-flash"}
        )

    def test_image_differs_on_source_image(self):
        tool = AgnesImage()
        base = {"prompt": "x", "size": "1024x768"}
        assert tool.idempotency_key(base) != tool.idempotency_key(
            {**base, "image_url": "https://example.com/img.png"}
        )


# ------------------------------------------------------------------
# Tool-specific behavior
# ------------------------------------------------------------------

class TestToolSpecific:

    def test_video_default_frames_is_121(self):
        tool = AgnesVideo()
        assert tool.input_schema["properties"]["num_frames"]["default"] == 121

    def test_video_default_frame_rate_is_24(self):
        tool = AgnesVideo()
        assert tool.input_schema["properties"]["frame_rate"]["default"] == 24

    def test_video_default_aspect_ratio_is_16_9(self):
        tool = AgnesVideo()
        assert tool.input_schema["properties"]["aspect_ratio"]["default"] == "16:9"

    def test_video_resolves_aspect(self):
        tool = AgnesVideo()
        assert tool._resolve_aspect("9:16") == (768, 1152)
        assert tool._resolve_aspect("16:9") == (1152, 768)

    def test_video_no_keys_returns_error(self, monkeypatch):
        monkeypatch.delenv("AGNES_API_KEY", raising=False)
        result = AgnesVideo().execute({"prompt": "test"})
        assert result.success is False
        assert "AGNES_API_KEY" in result.error

    def test_image_no_keys_returns_error(self, monkeypatch):
        monkeypatch.delenv("AGNES_API_KEY", raising=False)
        result = AgnesImage().execute({"prompt": "test"})
        assert result.success is False
        assert "AGNES_API_KEY" in result.error

    def test_video_validate_combo_accepts_valid(self):
        assert AgnesVideo()._validate_combo({"num_frames": 121, "frame_rate": 24}) is None

    def test_video_validate_combo_rejects_8n1_violation(self):
        err = AgnesVideo()._validate_combo({"num_frames": 120, "frame_rate": 24})
        assert err is not None
        assert "8n+1" in err

    def test_video_validate_combo_rejects_over_max(self):
        err = AgnesVideo()._validate_combo({"num_frames": 442, "frame_rate": 24})
        assert err is not None
        assert "441" in err

    def test_video_validate_combo_rejects_bad_fps(self):
        err = AgnesVideo()._validate_combo({"num_frames": 121, "frame_rate": 61})
        assert err is not None
        assert "frame_rate" in err

    def test_video_invalid_combo_fails_before_api(self, monkeypatch):
        """Invalid num_frames must be rejected before any remote request."""
        monkeypatch.setenv("AGNES_API_KEY", "fake-key")
        result = AgnesVideo().execute({"prompt": "test", "num_frames": 120})
        assert result.success is False
        assert "8n+1" in result.error

    def test_video_schema_bounds_num_frames(self):
        schema = AgnesVideo().input_schema
        nf = schema["properties"]["num_frames"]
        assert nf["minimum"] == 1
        assert nf["maximum"] == 441
        fr = schema["properties"]["frame_rate"]
        assert fr["minimum"] == 1
        assert fr["maximum"] == 60


# ------------------------------------------------------------------
# No cross-provider substitution
# ------------------------------------------------------------------

class TestNoCrossProviderSubstitution:

    def test_video_no_fal_upload_import(self):
        """The tool must not silently upload user assets to fal.ai."""
        import inspect

        source = inspect.getsource(AgnesVideo)
        assert "upload_image_fal" not in source
        assert "FAL" not in source

    def test_image_uses_agnes_only(self):
        import inspect

        source = inspect.getsource(AgnesImage)
        assert "upload_image_fal" not in source

    def test_video_local_image_falls_back_to_data_uri(self, monkeypatch):
        """If the Agnes upload relay fails, the image stays on Agnes as a data URI."""
        import tempfile
        from pathlib import Path

        monkeypatch.setenv("AGNES_API_KEY", "fake-key")
        tool = AgnesVideo()

        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp.write(b"\x89PNG\r\n\x1a\nfake")
        tmp.close()

        def boom(_self, _path):
            raise RuntimeError("relay down")

        monkeypatch.setattr(tool, "_upload_image_via_agnes", boom)
        assert tool._local_to_data_uri(tmp.name).startswith("data:image/png;base64,")
        Path(tmp.name).unlink()


# ------------------------------------------------------------------
# Registry discovery
# ------------------------------------------------------------------

class TestRegistryDiscovery:

    def test_discoverable(self):
        from tools.tool_registry import ToolRegistry

        registry = ToolRegistry()
        registry.discover()
        names = {t.name for t in registry._tools.values()}
        assert "agnes_image" in names
        assert "agnes_video" in names

    def test_single_instance_each(self):
        from tools.tool_registry import ToolRegistry

        registry = ToolRegistry()
        registry.discover()
        tools = [t for t in registry._tools.values() if t.provider == "agnes"]
        assert len(tools) == 2
        providers = {t.name: t.provider for t in tools}
        assert providers["agnes_image"] == "agnes"
        assert providers["agnes_video"] == "agnes"


# ------------------------------------------------------------------
# Selector routing
# ------------------------------------------------------------------

class TestSelectorRouting:

    def test_video_selector_can_route_to_agnes(self, monkeypatch):
        from tools.video.video_selector import VideoSelector

        monkeypatch.setenv("AGNES_API_KEY", "fake-key")
        selector = VideoSelector()
        providers = selector._providers()
        names = {t.name for t in providers}
        assert "agnes_video" in names

    def test_image_selector_can_route_to_agnes(self, monkeypatch):
        from tools.graphics.image_selector import ImageSelector

        monkeypatch.setenv("AGNES_API_KEY", "fake-key")
        selector = ImageSelector()
        names = {t.name for t in selector._providers()}
        assert "agnes_image" in names
