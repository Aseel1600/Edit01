"""Contract tests for ComfyUI provider tools.

These tests verify that the tools satisfy the BaseTool contract without
requiring a running ComfyUI server.  They check class attributes,
schemas, status reporting, and cost estimates.
"""

import json
from pathlib import Path

import pytest

from tools.base_tool import (
    BaseTool,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)
from tools.audio.comfyui_music import ComfyUIMusic
from tools.graphics.comfyui_image import ComfyUIImage
from tools.graphics.image_selector import ImageSelector
from tools.tool_registry import ToolRegistry
from tools.video.video_selector import VideoSelector
from tools.video.comfyui_video import ComfyUIVideo

TOOLS = [ComfyUIImage, ComfyUIVideo, ComfyUIMusic]
WORKFLOW_DIR = Path(__file__).resolve().parent.parent.parent / "tools" / "_comfyui" / "workflows"
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


# ------------------------------------------------------------------
# Contract compliance
# ------------------------------------------------------------------

@pytest.mark.parametrize("cls", TOOLS, ids=lambda c: c.name)
class TestContract:

    def test_inherits_base_tool(self, cls):
        assert issubclass(cls, BaseTool)

    def test_has_required_identity(self, cls):
        tool = cls()
        assert tool.name
        assert tool.version
        assert tool.capability
        assert tool.provider == "comfyui"
        assert tool.tier == ToolTier.GENERATE
        assert tool.stability == ToolStability.EXPERIMENTAL
        assert tool.runtime == ToolRuntime.LOCAL_GPU

    def test_has_input_schema(self, cls):
        tool = cls()
        schema = tool.input_schema
        assert schema.get("type") == "object"
        assert "prompt" in schema.get("properties", {})
        assert "prompt" in schema.get("required", [])

    def test_has_capabilities(self, cls):
        tool = cls()
        assert len(tool.capabilities) > 0

    def test_has_agent_skills(self, cls):
        tool = cls()
        assert tool.agent_skills
        assert "comfyui" in tool.agent_skills

    def test_comfyui_layer3_skill_exists(self, cls):
        skill_path = PROJECT_ROOT / ".agents" / "skills" / "comfyui" / "SKILL.md"
        assert skill_path.exists()
        assert "output_node" in skill_path.read_text(encoding="utf-8")

    def test_has_fallbacks(self, cls):
        tool = cls()
        assert tool.fallback or tool.fallback_tools

    def test_cost_is_zero(self, cls):
        tool = cls()
        assert tool.estimate_cost({"prompt": "test"}) == 0.0

    def test_runtime_estimate_positive(self, cls):
        tool = cls()
        assert tool.estimate_runtime({"prompt": "test"}) > 0

    def test_get_info_returns_dict(self, cls):
        tool = cls()
        info = tool.get_info()
        assert isinstance(info, dict)
        assert info["name"] == tool.name
        assert info["provider"] == "comfyui"
        assert info["runtime"] == "local_gpu"
        assert info["setup_offer"]["env_var"] == "COMFYUI_SERVER_URL"

    def test_video_resource_profile_does_not_mandate_16gb(self, cls):
        if cls is not ComfyUIVideo:
            return
        tool = ComfyUIVideo()
        info = tool.get_info()
        assert info["resource_profile"]["vram_mb"] == 8000
        assert info["resource_profiles"]["provider_floor"]["vram_mb"] == 8000
        assert info["resource_profiles"]["bundled_wan22_14b_fp8"]["vram_mb"] == 16000
        assert "not a ComfyUI provider-wide requirement" in (
            info["resource_profiles"]["bundled_wan22_14b_fp8"]["applies_to"]
        )

    def test_status_unavailable_without_server(self, cls):
        """Without a running server, status should be UNAVAILABLE."""
        tool = cls()
        # Point to a port that's almost certainly not running ComfyUI
        tool._client.server_url = "http://127.0.0.1:19999"
        assert tool.get_status() == ToolStatus.UNAVAILABLE

    def test_idempotency_key_fields(self, cls):
        tool = cls()
        assert len(tool.idempotency_key_fields) > 0
        assert "prompt" in tool.idempotency_key_fields

    def test_custom_workflow_schema_requires_output_node_contract(self, cls):
        tool = cls()
        props = tool.input_schema.get("properties", {})
        assert "workflow_json" in props
        assert "workflow_path" in props
        assert "output_node" in props

    def test_custom_workflow_requires_output_node(self, cls):
        tool = cls()
        result = tool.execute({"prompt": "test", "workflow_json": "{}"})
        assert result.success is False
        assert "output_node" in result.error


# ------------------------------------------------------------------
# Workflow files
# ------------------------------------------------------------------

EXPECTED_WORKFLOWS = [
    "flux2-txt2img.json",
    "wan22-i2v-4step.json",
    "wan22-t2v-4step.json",
    "ace-step-1-t2a.json",
]


@pytest.mark.parametrize("filename", EXPECTED_WORKFLOWS)
def test_workflow_exists_and_valid_json(filename):
    path = WORKFLOW_DIR / filename
    assert path.exists(), f"Missing workflow: {path}"
    with open(path) as f:
        data = json.load(f)
    assert isinstance(data, dict)
    assert len(data) > 0


def test_flux2_workflow_has_templated_nodes():
    with open(WORKFLOW_DIR / "flux2-txt2img.json") as f:
        w = json.load(f)
    assert "4" in w  # CLIPTextEncode (prompt)
    assert "7" in w  # RandomNoise (seed)
    assert "13" in w  # SaveImage (output)


def test_i2v_workflow_has_templated_nodes():
    with open(WORKFLOW_DIR / "wan22-i2v-4step.json") as f:
        w = json.load(f)
    assert "93" in w   # CLIPTextEncode (prompt)
    assert "97" in w   # LoadImage (reference)
    assert "86" in w   # KSamplerAdvanced (seed)
    assert "108" in w  # SaveVideo (output)


def test_t2v_workflow_has_templated_nodes():
    with open(WORKFLOW_DIR / "wan22-t2v-4step.json") as f:
        w = json.load(f)
    assert "2" in w   # CLIPTextEncode (prompt)
    assert "12" in w  # KSamplerAdvanced (seed)
    assert "16" in w  # SaveVideo (output)


def test_t2v_workflow_uses_14b_compatible_vae():
    with open(WORKFLOW_DIR / "wan22-t2v-4step.json") as f:
        w = json.load(f)
    assert w["4"]["inputs"]["vae_name"] == "wan_2.1_vae.safetensors"


def test_t2v_metadata_stack_uses_14b_compatible_vae():
    from tools._comfyui.metadata import BUNDLED_MODEL_STACKS

    vae_entry = next(item for item in BUNDLED_MODEL_STACKS["wan22-t2v-4step"] if item["role"] == "vae")
    assert vae_entry["name"] == "wan_2.1_vae.safetensors"
    assert "Wan_2.1_ComfyUI_repackaged" in vae_entry["download_url"]


# ------------------------------------------------------------------
# Client unit tests
# ------------------------------------------------------------------

class TestClientHelpers:

    def test_load_workflow(self):
        from tools._comfyui.client import ComfyUIClient
        w = ComfyUIClient.load_workflow(WORKFLOW_DIR / "flux2-txt2img.json")
        assert isinstance(w, dict)
        assert "1" in w

    def test_patch_workflow(self):
        from tools._comfyui.client import ComfyUIClient
        w = ComfyUIClient.load_workflow(WORKFLOW_DIR / "flux2-txt2img.json")
        patched = ComfyUIClient.patch_workflow(w, {
            "4": {"text": "hello world"},
            "7": {"noise_seed": 123},
        })
        assert patched["4"]["inputs"]["text"] == "hello world"
        assert patched["7"]["inputs"]["noise_seed"] == 123
        # Original unchanged
        assert w["4"]["inputs"]["text"] == ""

    def test_patch_workflow_bad_node(self):
        from tools._comfyui.client import ComfyUIClient, ComfyUIError
        w = {"1": {"inputs": {"x": 1}}}
        with pytest.raises(ComfyUIError, match="not found"):
            ComfyUIClient.patch_workflow(w, {"99": {"x": 2}})

    def test_submit_surfaces_node_errors_before_http_error(self, monkeypatch):
        from tools._comfyui.client import ComfyUIClient, ComfyUIError

        class FakeResponse:
            status_code = 400

            def json(self):
                return {
                    "error": {"message": "Prompt outputs failed validation"},
                    "node_errors": {"4": {"class_type": "MissingNode"}},
                }

            def raise_for_status(self):
                raise AssertionError("HTTPError should not hide node_errors")

        monkeypatch.setattr(
            "tools._comfyui.client.requests.post",
            lambda *args, **kwargs: FakeResponse(),
        )

        with pytest.raises(ComfyUIError, match="Node errors"):
            ComfyUIClient("http://comfy.test").submit({})

    def test_random_seed_range(self):
        from tools._comfyui.client import ComfyUIClient
        for _ in range(100):
            s = ComfyUIClient.random_seed()
            assert 0 <= s < 2**32

    def test_generate_passes_history_item_type_to_view(self, monkeypatch, tmp_path):
        from tools._comfyui.client import ComfyUIClient

        client = ComfyUIClient("http://comfy.test")
        seen = {}

        monkeypatch.setattr(client, "submit", lambda workflow: "prompt-1")
        monkeypatch.setattr(client, "poll", lambda prompt_id, **kwargs: {
            "outputs": {
                "9": {
                    "images": [{
                        "filename": "preview.png",
                        "subfolder": "previews",
                        "type": "temp",
                    }]
                }
            }
        })

        def fake_download(filename, subfolder, dest, folder_type="output"):
            seen["filename"] = filename
            seen["subfolder"] = subfolder
            seen["folder_type"] = folder_type
            return Path(dest)

        monkeypatch.setattr(client, "download", fake_download)

        client.generate({"9": {"inputs": {}}}, "9", tmp_path / "preview.png")

        assert seen == {
            "filename": "preview.png",
            "subfolder": "previews",
            "folder_type": "temp",
        }

    def test_poll_timeout_carries_prompt_id_for_recovery(self, monkeypatch):
        from tools._comfyui.client import ComfyUIClient, ComfyUIError

        client = ComfyUIClient("http://comfy.test")
        monkeypatch.setattr(
            "tools._comfyui.client.requests.get",
            lambda *a, **k: type("R", (), {
                "raise_for_status": lambda self: None,
                "json": lambda self: {},
            })(),
        )
        monkeypatch.setattr("tools._comfyui.client.time.sleep", lambda s: None)

        with pytest.raises(ComfyUIError) as excinfo:
            client.poll("prompt-timeout-1", timeout=0, interval=0)

        assert excinfo.value.prompt_id == "prompt-timeout-1"
        assert "prompt-timeout-1" in str(excinfo.value)

    def test_generate_resume_prompt_id_skips_resubmit(self, monkeypatch, tmp_path):
        from tools._comfyui.client import ComfyUIClient
        import sys

        client = ComfyUIClient("http://comfy.test")

        def fail_submit(workflow):
            raise AssertionError("submit() should not be called when resuming")

        monkeypatch.setattr(client, "submit", fail_submit)
        _install_fake_websocket(monkeypatch, frames=[])
        monkeypatch.setattr(
            sys.modules["websocket"],
            "create_connection",
            lambda *a, **k: (_ for _ in ()).throw(
                AssertionError("resumed jobs must use history polling")
            ),
        )
        monkeypatch.setattr(client, "poll", lambda prompt_id, **kwargs: {
            "outputs": {"9": {"images": [{
                "filename": "resumed.png", "subfolder": "", "type": "output",
            }]}}
        })
        monkeypatch.setattr(client, "download", lambda filename, subfolder, dest, folder_type="output": Path(dest))

        paths = client.generate(
            {"9": {"inputs": {}}}, "9", tmp_path / "out.png",
            resume_prompt_id="already-running-id",
        )
        assert paths == [tmp_path / "out.png"]

    def test_generate_reads_audio_key_from_savaudio_node(self, monkeypatch, tmp_path):
        """The native SaveAudio node writes outputs under "audio", not
        "images"/"gifs" -- comfyui_music depends on this being handled."""
        from tools._comfyui.client import ComfyUIClient

        client = ComfyUIClient("http://comfy.test")
        monkeypatch.setattr(client, "submit", lambda workflow: "p1")
        monkeypatch.setattr(client, "poll", lambda prompt_id, **kwargs: {
            "outputs": {"9": {"audio": [{
                "filename": "track.flac", "subfolder": "", "type": "output",
            }]}}
        })
        monkeypatch.setattr(client, "download", lambda filename, subfolder, dest, folder_type="output": Path(dest))

        paths = client.generate({"9": {"inputs": {}}}, "9", tmp_path / "out.flac")
        assert paths == [tmp_path / "out.flac"]

    def test_is_default_url_when_env_not_set(self, monkeypatch):
        from tools._comfyui.client import ComfyUIClient
        monkeypatch.delenv("COMFYUI_SERVER_URL", raising=False)
        client = ComfyUIClient()
        assert client.is_default_url is True

    def test_is_not_default_url_when_env_set(self, monkeypatch):
        from tools._comfyui.client import ComfyUIClient
        monkeypatch.setenv("COMFYUI_SERVER_URL", "http://myhost:9999")
        client = ComfyUIClient()
        assert client.is_default_url is False

    def test_unavailable_reason_default_url(self, monkeypatch):
        from tools._comfyui.client import ComfyUIClient
        monkeypatch.delenv("COMFYUI_SERVER_URL", raising=False)
        client = ComfyUIClient()
        msg = client.unavailable_reason()
        assert "COMFYUI_SERVER_URL" in msg
        assert ".env" in msg

    def test_unavailable_reason_custom_url(self, monkeypatch):
        from tools._comfyui.client import ComfyUIClient
        monkeypatch.setenv("COMFYUI_SERVER_URL", "http://myhost:9999")
        client = ComfyUIClient()
        msg = client.unavailable_reason()
        assert "myhost:9999" in msg
        assert "COMFYUI_SERVER_URL" not in msg

    def test_submit_includes_client_id_for_websocket_targeting(self, monkeypatch):
        from tools._comfyui.client import ComfyUIClient

        client = ComfyUIClient("http://comfy.test")
        seen = {}

        def fake_post(url, json=None, timeout=None, headers=None):
            seen.update(json)
            return type("R", (), {
                "raise_for_status": lambda self: None,
                "json": lambda self: {"prompt_id": "abc"},
            })()

        monkeypatch.setattr("tools._comfyui.client.requests.post", fake_post)
        client.submit({"1": {"inputs": {}}})
        assert seen["client_id"] == client.client_id


class TestMultiServer:

    def test_capability_env_var_takes_priority_over_shared(self, monkeypatch):
        from tools._comfyui.client import ComfyUIClient

        monkeypatch.setenv("COMFYUI_SERVER_URL", "http://shared:8188")
        monkeypatch.setenv("COMFYUI_VIDEO_SERVER_URL", "http://video-gpu:8188")
        client = ComfyUIClient(capability="video")
        assert client.server_url == "http://video-gpu:8188"

    def test_falls_back_to_shared_when_capability_var_unset(self, monkeypatch):
        from tools._comfyui.client import ComfyUIClient

        monkeypatch.setenv("COMFYUI_SERVER_URL", "http://shared:8188")
        monkeypatch.delenv("COMFYUI_IMAGE_SERVER_URL", raising=False)
        client = ComfyUIClient(capability="image")
        assert client.server_url == "http://shared:8188"

    def test_other_capability_env_var_does_not_leak_across_tools(self, monkeypatch):
        from tools._comfyui.client import ComfyUIClient

        monkeypatch.delenv("COMFYUI_SERVER_URL", raising=False)
        monkeypatch.setenv("COMFYUI_IMAGE_SERVER_URL", "http://image-gpu:8188")
        monkeypatch.delenv("COMFYUI_VIDEO_SERVER_URL", raising=False)
        video_client = ComfyUIClient(capability="video")
        assert video_client.server_url == "http://localhost:8188"

    def test_explicit_server_url_wins_over_capability_env_var(self, monkeypatch):
        from tools._comfyui.client import ComfyUIClient

        monkeypatch.setenv("COMFYUI_VIDEO_SERVER_URL", "http://video-gpu:8188")
        client = ComfyUIClient("http://explicit:1234", capability="video")
        assert client.server_url == "http://explicit:1234"

    def test_no_capability_behaves_as_before(self, monkeypatch):
        from tools._comfyui.client import ComfyUIClient

        monkeypatch.setenv("COMFYUI_SERVER_URL", "http://shared:8188")
        client = ComfyUIClient()
        assert client.server_url == "http://shared:8188"
        assert client.is_default_url is False

    def test_is_default_url_true_only_when_both_vars_unset(self, monkeypatch):
        from tools._comfyui.client import ComfyUIClient

        monkeypatch.delenv("COMFYUI_SERVER_URL", raising=False)
        monkeypatch.delenv("COMFYUI_IMAGE_SERVER_URL", raising=False)
        client = ComfyUIClient(capability="image")
        assert client.is_default_url is True

        monkeypatch.setenv("COMFYUI_IMAGE_SERVER_URL", "http://image-gpu:8188")
        client2 = ComfyUIClient(capability="image")
        assert client2.is_default_url is False

    def test_unavailable_reason_mentions_capability_and_shared_var(self, monkeypatch):
        from tools._comfyui.client import ComfyUIClient

        monkeypatch.delenv("COMFYUI_SERVER_URL", raising=False)
        monkeypatch.delenv("COMFYUI_VIDEO_SERVER_URL", raising=False)
        client = ComfyUIClient(capability="video")
        msg = client.unavailable_reason()
        assert "COMFYUI_VIDEO_SERVER_URL" in msg
        assert "COMFYUI_SERVER_URL" in msg

    def test_image_and_video_tools_use_independent_servers(self, monkeypatch):
        from tools.graphics.comfyui_image import ComfyUIImage
        from tools.video.comfyui_video import ComfyUIVideo

        monkeypatch.delenv("COMFYUI_SERVER_URL", raising=False)
        monkeypatch.setenv("COMFYUI_IMAGE_SERVER_URL", "http://image-gpu:8188")
        monkeypatch.setenv("COMFYUI_VIDEO_SERVER_URL", "http://video-gpu:8188")

        image_tool = ComfyUIImage()
        video_tool = ComfyUIVideo()

        assert image_tool._client.server_url == "http://image-gpu:8188"
        assert video_tool._client.server_url == "http://video-gpu:8188"


class _FakeWSTimeout(Exception):
    pass


class _FakeWSConn:
    def __init__(self, frames):
        self._frames = list(frames)

    def settimeout(self, value):
        pass

    def recv(self):
        if not self._frames:
            raise _FakeWSTimeout()
        return self._frames.pop(0)

    def close(self):
        pass


def _install_fake_websocket(monkeypatch, frames):
    """Inject a fake `websocket` module so wait_ws() runs without the real
    optional websocket-client dependency installed."""
    import sys
    import types

    fake_module = types.SimpleNamespace(
        WebSocketTimeoutException=_FakeWSTimeout,
        create_connection=lambda url, timeout=10: _FakeWSConn(frames),
    )
    monkeypatch.setitem(sys.modules, "websocket", fake_module)


class TestWebsocketWait:

    def test_wait_ws_returns_job_completed_before_connection(self, monkeypatch):
        from tools._comfyui.client import ComfyUIClient
        import sys

        client = ComfyUIClient("http://comfy.test")
        _install_fake_websocket(monkeypatch, frames=[])
        monkeypatch.setattr(
            sys.modules["websocket"],
            "create_connection",
            lambda *a, **k: (_ for _ in ()).throw(
                AssertionError("completed history must avoid websocket connection")
            ),
        )
        monkeypatch.setattr(
            "tools._comfyui.client.requests.get",
            lambda *a, **k: type("R", (), {
                "raise_for_status": lambda self: None,
                "json": lambda self: {"done": {"outputs": {"9": {}}}},
            })(),
        )

        assert client.wait_ws("done", timeout=5) == {"outputs": {"9": {}}}

    def test_wait_ws_completes_on_executing_none_node(self, monkeypatch, tmp_path):
        from tools._comfyui.client import ComfyUIClient

        client = ComfyUIClient("http://comfy.test")
        progress_events = []
        frames = [
            json.dumps({"type": "progress", "data": {
                "value": 2, "max": 20, "prompt_id": "p1",
            }}),
            json.dumps({"type": "executing", "data": {
                "node": None, "prompt_id": "p1",
            }}),
        ]
        _install_fake_websocket(monkeypatch, frames)
        history_calls = iter(({}, {}, {"p1": {"outputs": {"9": {}}}}))
        monkeypatch.setattr(
            "tools._comfyui.client.requests.get",
            lambda *a, **k: type("R", (), {
                "raise_for_status": lambda self: None,
                "json": lambda self: next(history_calls),
            })(),
        )

        entry = client.wait_ws("p1", timeout=5, on_progress=progress_events.append)

        assert entry == {"outputs": {"9": {}}}
        assert progress_events == [{"value": 2, "max": 20, "prompt_id": "p1"}]

    def test_wait_ws_execution_error_raises_with_prompt_id(self, monkeypatch):
        from tools._comfyui.client import ComfyUIClient, ComfyUIError

        client = ComfyUIClient("http://comfy.test")
        frames = [
            json.dumps({"type": "execution_error", "data": {
                "prompt_id": "p2", "exception_message": "boom",
            }}),
        ]
        _install_fake_websocket(monkeypatch, frames)

        with pytest.raises(ComfyUIError) as excinfo:
            client.wait_ws("p2", timeout=5)

        assert excinfo.value.prompt_id == "p2"

    def test_wait_ws_ignores_other_prompts_on_shared_connection(self, monkeypatch):
        from tools._comfyui.client import ComfyUIClient

        client = ComfyUIClient("http://comfy.test")
        frames = [
            # Another job's event on the same client_id -- must not trigger completion.
            json.dumps({"type": "executing", "data": {
                "node": None, "prompt_id": "someone-elses-job",
            }}),
            json.dumps({"type": "executing", "data": {
                "node": None, "prompt_id": "p3",
            }}),
        ]
        _install_fake_websocket(monkeypatch, frames)
        monkeypatch.setattr(
            "tools._comfyui.client.requests.get",
            lambda *a, **k: type("R", (), {
                "raise_for_status": lambda self: None,
                "json": lambda self: {"p3": {"outputs": {}}},
            })(),
        )

        entry = client.wait_ws("p3", timeout=5)
        assert entry == {"outputs": {}}

    def test_wait_ws_timeout_raises_comfyuierror_with_prompt_id(self, monkeypatch):
        from tools._comfyui.client import ComfyUIClient, ComfyUIError

        client = ComfyUIClient("http://comfy.test")
        _install_fake_websocket(monkeypatch, frames=[])  # recv() always times out

        with pytest.raises(ComfyUIError) as excinfo:
            client.wait_ws("p4", timeout=0)

        assert excinfo.value.prompt_id == "p4"

    def test_wait_falls_back_to_poll_when_websocket_unavailable(self, monkeypatch):
        """No websocket-client installed (or any transport failure) must
        silently fall back to REST polling, not blow up the whole call."""
        from tools._comfyui.client import ComfyUIClient
        import sys

        client = ComfyUIClient("http://comfy.test")
        monkeypatch.delitem(sys.modules, "websocket", raising=False)
        monkeypatch.setattr(
            "builtins.__import__",
            _raise_on_websocket_import(__import__),
        )
        monkeypatch.setattr(
            client, "poll", lambda prompt_id, **kwargs: {"outputs": {"used": "poll"}}
        )

        entry = client._wait("p5", timeout=5, interval=5)
        assert entry == {"outputs": {"used": "poll"}}

    def test_wait_does_not_swallow_genuine_comfyuierror_from_websocket(self, monkeypatch):
        """A real execution error detected over the websocket must propagate,
        not be masked by a fallback-to-poll retry."""
        from tools._comfyui.client import ComfyUIClient, ComfyUIError

        client = ComfyUIClient("http://comfy.test")
        frames = [
            json.dumps({"type": "execution_error", "data": {
                "prompt_id": "p6", "exception_message": "bad node",
            }}),
        ]
        _install_fake_websocket(monkeypatch, frames)

        def fail_poll(prompt_id, **kwargs):
            raise AssertionError("poll() should not be called after a real ws error")

        monkeypatch.setattr(client, "poll", fail_poll)

        with pytest.raises(ComfyUIError) as excinfo:
            client._wait("p6", timeout=5, interval=5)
        assert excinfo.value.prompt_id == "p6"


def _raise_on_websocket_import(real_import):
    def _import(name, *args, **kwargs):
        if name == "websocket":
            raise ImportError("no module named websocket")
        return real_import(name, *args, **kwargs)
    return _import


# ------------------------------------------------------------------
# Model discovery (offline, no server needed)
# ------------------------------------------------------------------

class TestModelRequirements:

    def test_image_tool_has_required_models(self):
        from tools.graphics.comfyui_image import _REQUIRED_MODELS
        assert len(_REQUIRED_MODELS) > 0
        assert any("flux" in m.lower() for m in _REQUIRED_MODELS)

    def test_video_tool_has_required_models_i2v(self):
        from tools.video.comfyui_video import _REQUIRED_MODELS_I2V
        assert len(_REQUIRED_MODELS_I2V) > 0
        assert any("i2v" in m.lower() for m in _REQUIRED_MODELS_I2V)

    def test_video_tool_has_required_models_t2v(self):
        from tools.video.comfyui_video import _REQUIRED_MODELS_T2V
        assert len(_REQUIRED_MODELS_T2V) > 0
        assert any("t2v" in m.lower() for m in _REQUIRED_MODELS_T2V)

    def test_music_tool_has_required_models(self):
        from tools.audio.comfyui_music import _REQUIRED_MODELS
        assert len(_REQUIRED_MODELS) > 0
        assert any("ace_step" in m.lower() for m in _REQUIRED_MODELS)


# ------------------------------------------------------------------
# Custom workflow contract and provenance
# ------------------------------------------------------------------

class TestCustomWorkflowContract:

    def test_image_custom_workflow_uses_caller_output_node_and_provenance(self, tmp_path):
        tool = ComfyUIImage()
        tool._client.is_available = lambda: True
        seen = {}

        def fake_generate(workflow, output_node, dest, **kwargs):
            seen["workflow"] = workflow
            seen["output_node"] = output_node
            return [Path(dest)]

        tool._client.generate = fake_generate

        result = tool.execute({
            "prompt": "test",
            "workflow_json": json.dumps({"99": {"inputs": {}}}),
            "output_node": "99",
            "workflow_model": "custom-flux",
            "output_path": str(tmp_path / "image.png"),
        })

        assert result.success is True
        assert seen["output_node"] == "99"
        assert result.model == "custom-flux"
        assert result.data["model"] == "custom-flux"
        assert result.data["workflow_provenance"]["source"] == "user_supplied"
        assert result.data["workflow_provenance"]["output_node"] == "99"
        assert result.data["workflow_provenance"]["workflow_hash_sha256"]
        assert result.data["workflow_provenance"]["model_stack_source"] == (
            "unknown_custom_workflow"
        )

    def test_video_custom_workflow_uses_caller_output_node_and_provenance(self, tmp_path):
        tool = ComfyUIVideo()
        tool._client.is_available = lambda: True
        seen = {}

        def fake_generate(workflow, output_node, dest, **kwargs):
            seen["workflow"] = workflow
            seen["output_node"] = output_node
            return [Path(dest)]

        tool._client.generate = fake_generate

        result = tool.execute({
            "prompt": "test",
            "workflow_json": json.dumps({"42": {"inputs": {}}}),
            "output_node": "42",
            "workflow_model": "custom-wan",
            "output_path": str(tmp_path / "video.mp4"),
        })

        assert result.success is True
        assert seen["output_node"] == "42"
        assert result.model == "custom-wan"
        assert result.data["model"] == "custom-wan"
        assert result.data["workflow_provenance"]["source"] == "user_supplied"
        assert result.data["workflow_provenance"]["output_node"] == "42"
        assert result.data["workflow_provenance"]["workflow_hash_sha256"]
        assert result.data["workflow_provenance"]["model_stack_source"] == (
            "unknown_custom_workflow"
        )

    def test_custom_workflow_accepts_model_stack_provenance(self, tmp_path):
        tool = ComfyUIVideo()
        tool._client.is_available = lambda: True
        tool._client.generate = lambda workflow, output_node, dest, **kwargs: [Path(dest)]

        result = tool.execute({
            "prompt": "test",
            "workflow_json": json.dumps({"42": {"inputs": {}}}),
            "output_node": "42",
            "workflow_model_stack": [{"role": "lora", "name": "style.safetensors"}],
            "output_path": str(tmp_path / "video.mp4"),
        })

        provenance = result.data["workflow_provenance"]
        assert provenance["model_stack"] == [{"role": "lora", "name": "style.safetensors"}]
        assert provenance["model_stack_source"] == "caller_supplied"

    def test_video_timeout_surfaces_resumable_prompt_id(self, tmp_path):
        from tools._comfyui.client import ComfyUIError

        tool = ComfyUIVideo()
        tool._client.is_available = lambda: True

        def fake_generate(workflow, output_node, dest, **kwargs):
            raise ComfyUIError("Prompt timed-out-id did not complete within 5s", prompt_id="timed-out-id")

        tool._client.generate = fake_generate

        result = tool.execute({
            "prompt": "test",
            "workflow_json": json.dumps({"42": {"inputs": {}}}),
            "output_node": "42",
            "output_path": str(tmp_path / "video.mp4"),
            "timeout_seconds": 5,
        })

        assert result.success is False
        assert result.data["prompt_id"] == "timed-out-id"
        assert "resume_prompt_id" in result.error
        assert "timed-out-id" in result.error

    def test_video_passes_timeout_and_resume_prompt_id_through(self, tmp_path):
        tool = ComfyUIVideo()
        tool._client.is_available = lambda: True
        seen = {}

        def fake_generate(workflow, output_node, dest, **kwargs):
            seen.update(kwargs)
            return [Path(dest)]

        tool._client.generate = fake_generate

        result = tool.execute({
            "prompt": "test",
            "workflow_json": json.dumps({"42": {"inputs": {}}}),
            "output_node": "42",
            "output_path": str(tmp_path / "video.mp4"),
            "timeout_seconds": 7200,
            "resume_prompt_id": "already-running-id",
        })

        assert result.success is True
        assert seen["timeout"] == 7200
        assert seen["resume_prompt_id"] == "already-running-id"

    def test_video_default_timeout_is_generous_not_900s(self, tmp_path):
        tool = ComfyUIVideo()
        tool._client.is_available = lambda: True
        seen = {}

        def fake_generate(workflow, output_node, dest, **kwargs):
            seen.update(kwargs)
            return [Path(dest)]

        tool._client.generate = fake_generate

        tool.execute({
            "prompt": "test",
            "workflow_json": json.dumps({"42": {"inputs": {}}}),
            "output_node": "42",
            "output_path": str(tmp_path / "video.mp4"),
        })

        # Regression guard: the old hardcoded 900s timeout false-failed real
        # renders on modest local GPUs (observed ~1360-1630s for non-accelerated
        # custom Wan 1.3B workflows at 832x480/81-97 frames).
        assert seen["timeout"] > 900

    def test_image_missing_models_are_structured(self):
        tool = ComfyUIImage()
        tool._client.is_available = lambda: True
        tool._client.check_models = lambda required: (
            [],
            ["flux2-vae.safetensors"],
        )

        result = tool.execute({"prompt": "test"})

        assert result.success is False
        assert result.data["provider"] == "comfyui"
        assert result.data["missing_models"][0]["name"] == "flux2-vae.safetensors"
        assert result.data["missing_models"][0]["destination_hint"] == "ComfyUI/models/vae/"
        assert result.data["missing_models"][0]["download_url"]

    def test_video_missing_models_are_structured(self):
        tool = ComfyUIVideo()
        tool._client.is_available = lambda: True
        tool._client.check_models = lambda required: (
            [],
            ["wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors"],
        )

        result = tool.execute({"prompt": "test", "operation": "text_to_video"})

        assert result.success is False
        assert result.data["operation"] == "text_to_video"
        assert result.data["missing_models"][0]["role"] == "diffusion_model_high_noise"
        assert result.data["missing_models"][0]["download_url"]

    def test_bundled_workflow_provenance_records_hash_and_stack(self, tmp_path):
        tool = ComfyUIImage()
        tool._client.is_available = lambda: True
        tool._client.check_models = lambda required: (list(required), [])
        tool._client.generate = lambda workflow, output_node, dest, **kwargs: [Path(dest)]

        result = tool.execute({
            "prompt": "test",
            "output_path": str(tmp_path / "image.png"),
        })

        provenance = result.data["workflow_provenance"]
        assert provenance["source"] == "bundled"
        assert provenance["workflow_hash_sha256"]
        assert any(item["role"] == "vae" for item in provenance["model_stack"])


class TestComfyUIMusic:

    def test_capability_and_provider(self):
        tool = ComfyUIMusic()
        assert tool.capability == "music_generation"
        assert tool.provider == "comfyui"

    def test_bundled_path_requires_no_workflow_json_or_output_node(self, tmp_path):
        """Without workflow_json/workflow_path it should attempt the bundled
        ACE-Step workflow, not demand a custom one."""
        tool = ComfyUIMusic()
        tool._client.is_available = lambda: True
        tool._client.check_models = lambda required: (list(required), [])
        tool._client.generate = lambda workflow, output_node, dest, **kwargs: [Path(dest)]

        result = tool.execute({
            "prompt": "ambient pad",
            "output_path": str(tmp_path / "music.mp3"),
        })

        assert result.success is True
        assert result.data["workflow_provenance"]["source"] == "bundled"

    def test_custom_workflow_without_output_node_errors(self):
        tool = ComfyUIMusic()
        tool._client.is_available = lambda: True

        result = tool.execute({
            "prompt": "ambient pad",
            "workflow_json": json.dumps({"9": {"inputs": {}}}),
        })

        assert result.success is False
        assert "output_node" in result.error

    def test_bundled_missing_models_returns_structured_payload(self):
        tool = ComfyUIMusic()
        tool._client.is_available = lambda: True
        tool._client.check_models = lambda required: ([], list(required))

        result = tool.execute({"prompt": "ambient pad"})

        assert result.success is False
        assert result.data["missing_models"][0]["name"] == "ace_step_v1_3.5b.safetensors"
        assert result.data["missing_models"][0]["download_url"]

    def test_bundled_generation_patches_tags_lyrics_and_seed(self, tmp_path):
        tool = ComfyUIMusic()
        tool._client.is_available = lambda: True
        tool._client.check_models = lambda required: (list(required), [])
        seen = {}

        def fake_generate(workflow, output_node, dest, **kwargs):
            seen["workflow"] = workflow
            seen["output_node"] = output_node
            return [Path(dest)]

        tool._client.generate = fake_generate

        result = tool.execute({
            "prompt": "lofi hip hop, chill, rain sounds",
            "lyrics": "[verse]\nquiet streets",
            "duration_seconds": 45,
            "seed": 777,
            "output_path": str(tmp_path / "music.mp3"),
        })

        assert result.success is True
        assert seen["output_node"] == "10"
        assert seen["workflow"]["2"]["inputs"]["tags"] == "lofi hip hop, chill, rain sounds"
        assert seen["workflow"]["2"]["inputs"]["lyrics"] == "[verse]\nquiet streets"
        assert seen["workflow"]["4"]["inputs"]["seconds"] == 45
        assert seen["workflow"]["8"]["inputs"]["seed"] == 777
        assert result.data["model"] == "ace-step-v1-3.5b"

    def test_bundled_generation_preserves_seed_zero(self, tmp_path):
        tool = ComfyUIMusic()
        tool._client.is_available = lambda: True
        tool._client.check_models = lambda required: (list(required), [])
        seen = {}

        def fake_generate(workflow, output_node, dest, **kwargs):
            seen["seed"] = workflow["8"]["inputs"]["seed"]
            return [Path(dest)]

        tool._client.generate = fake_generate
        result = tool.execute({
            "prompt": "deterministic test",
            "seed": 0,
            "output_path": str(tmp_path / "music.mp3"),
        })

        assert result.success is True
        assert result.seed == 0
        assert seen["seed"] == 0

    def test_get_status_degraded_when_model_missing(self):
        tool = ComfyUIMusic()
        tool._client.is_available = lambda: True
        tool._client.check_models = lambda required: ([], list(required))
        assert tool.get_status() == ToolStatus.DEGRADED

    def test_unavailable_server_reports_unavailable_reason(self):
        tool = ComfyUIMusic()
        tool._client.is_available = lambda: False
        tool._client.unavailable_reason = lambda: "no server here"

        result = tool.execute({
            "prompt": "ambient pad",
            "workflow_json": json.dumps({"9": {"inputs": {}}}),
            "output_node": "9",
        })

        assert result.success is False
        assert result.error == "no server here"

    def test_successful_generation_returns_provenance_and_duration(self, tmp_path, monkeypatch):
        tool = ComfyUIMusic()
        tool._client.is_available = lambda: True

        dest_file = tmp_path / "music.mp3"

        def fake_generate(workflow, output_node, dest, **kwargs):
            Path(dest).write_bytes(b"fake-audio-bytes")
            return [Path(dest)]

        tool._client.generate = fake_generate
        monkeypatch.setattr("shutil.which", lambda name: None)  # no ffprobe in test env

        result = tool.execute({
            "prompt": "upbeat synthwave",
            "workflow_json": json.dumps({"9": {"inputs": {}}}),
            "output_node": "9",
            "output_path": str(dest_file),
            "workflow_name": "my-ace-step-graph",
            "workflow_model": "ace-step-v1-3.5b",
        })

        assert result.success is True
        assert result.data["provider"] == "comfyui"
        assert result.data["model"] == "ace-step-v1-3.5b"
        assert result.data["output"] == str(dest_file)
        assert result.data["format"] == "mp3"
        assert result.data["duration_seconds"] is None  # ffprobe unavailable
        provenance = result.data["workflow_provenance"]
        assert provenance["source"] == "user_supplied"
        assert provenance["output_node"] == "9"
        assert provenance["workflow_hash_sha256"]

    def test_timeout_surfaces_resumable_prompt_id(self, tmp_path):
        from tools._comfyui.client import ComfyUIError

        tool = ComfyUIMusic()
        tool._client.is_available = lambda: True

        def fake_generate(workflow, output_node, dest, **kwargs):
            raise ComfyUIError("timed out", prompt_id="music-prompt-id")

        tool._client.generate = fake_generate

        result = tool.execute({
            "prompt": "ambient pad",
            "workflow_json": json.dumps({"9": {"inputs": {}}}),
            "output_node": "9",
            "output_path": str(tmp_path / "music.mp3"),
        })

        assert result.success is False
        assert result.data["prompt_id"] == "music-prompt-id"
        assert "resume_prompt_id" in result.error

    def test_passes_timeout_and_resume_prompt_id_through(self, tmp_path):
        tool = ComfyUIMusic()
        tool._client.is_available = lambda: True
        seen = {}

        def fake_generate(workflow, output_node, dest, **kwargs):
            seen.update(kwargs)
            return [Path(dest)]

        tool._client.generate = fake_generate

        tool.execute({
            "prompt": "ambient pad",
            "workflow_json": json.dumps({"9": {"inputs": {}}}),
            "output_node": "9",
            "output_path": str(tmp_path / "music.mp3"),
            "timeout_seconds": 3600,
            "resume_prompt_id": "already-running-id",
        })

        assert seen["timeout"] == 3600
        assert seen["resume_prompt_id"] == "already-running-id"

    def test_registry_discovers_comfyui_music_under_music_generation(self):
        registry = ToolRegistry()
        tool = ComfyUIMusic()
        registry.register(tool)
        registry._discovered_packages.add("tools")

        by_capability = registry.get_by_capability("music_generation")
        assert any(t.name == "comfyui_music" for t in by_capability)

    def test_uses_music_capability_env_var_for_multi_server(self, monkeypatch):
        monkeypatch.delenv("COMFYUI_SERVER_URL", raising=False)
        monkeypatch.setenv("COMFYUI_MUSIC_SERVER_URL", "http://music-gpu:8188")
        tool = ComfyUIMusic()
        assert tool._client.server_url == "http://music-gpu:8188"


class TestComfyUISetupOffer:

    def test_provider_menu_summary_includes_structured_setup_offer(self):
        registry = ToolRegistry()
        tool = ComfyUIImage()
        tool._client.is_available = lambda: False
        registry.register(tool)
        registry._discovered_packages.add("tools")

        summary = registry.provider_menu_summary()

        offer = summary["setup_offers"][0]
        assert offer["tool"] == "comfyui_image"
        assert offer["env_var"] == "COMFYUI_SERVER_URL"
        assert offer["default_url"] == "http://localhost:8188"
        assert offer["health_check"] == "GET /system_stats"


# ------------------------------------------------------------------
# Operation-specific video readiness
# ------------------------------------------------------------------

class TestVideoOperationReadiness:

    def test_video_tool_reports_partial_operation_readiness(self):
        from tools.video.comfyui_video import _REQUIRED_MODELS_I2V, _REQUIRED_MODELS_T2V

        tool = ComfyUIVideo()
        tool._client.is_available = lambda: True

        def fake_check_models(required):
            if required == _REQUIRED_MODELS_T2V:
                return list(required), []
            if required == _REQUIRED_MODELS_I2V:
                return [], list(required)
            return [], list(required)

        tool._client.check_models = fake_check_models

        assert tool.get_status() == ToolStatus.AVAILABLE
        assert tool.is_operation_available("text_to_video") is True
        assert tool.is_operation_available("image_to_video") is False
        assert tool.operation_statuses() == {
            "text_to_video": "available",
            "image_to_video": "degraded",
        }

    def test_video_selector_filters_operation_unready_tools(self):
        class PartialVideoTool(BaseTool):
            name = "partial_video"
            capability = "video_generation"
            provider = "partial"
            supports = {"image_to_video": True}
            input_schema = {"type": "object", "properties": {}}

            def is_operation_available(self, operation):
                return operation == "text_to_video"

            def execute(self, inputs):
                raise AssertionError("not used")

        selector = VideoSelector()
        candidates = [PartialVideoTool()]

        assert selector._filter_candidates(
            {"operation": "image_to_video"}, candidates
        ) == []

    def test_video_selector_rank_uses_target_operation_for_readiness(self):
        class PartialVideoTool(BaseTool):
            name = "partial_video"
            capability = "video_generation"
            provider = "partial"
            supports = {"image_to_video": True}
            input_schema = {"type": "object", "properties": {}}

            def is_operation_available(self, operation):
                return operation == "text_to_video"

            def execute(self, inputs):
                raise AssertionError("not used")

        selector = VideoSelector()
        candidates = [PartialVideoTool()]
        rank_inputs = selector._rank_inputs({
            "operation": "rank",
            "target_operation": "image_to_video",
        })

        assert rank_inputs["operation"] == "image_to_video"
        assert selector._filter_candidates(rank_inputs, candidates) == []


# ------------------------------------------------------------------
# Custom-workflow selector eligibility
# ------------------------------------------------------------------

class _DegradedComfyVideo(BaseTool):
    """Server reachable, but bundled WAN models missing -> DEGRADED, no
    operation ready. Stands in for comfyui_video on a low-VRAM box."""

    name = "comfyui_video"
    capability = "video_generation"
    provider = "comfyui"
    supports = {"custom_workflow": True, "image_to_video": True}
    input_schema = {"type": "object", "properties": {"workflow_json": {"type": "string"}}}

    def get_status(self):
        return ToolStatus.DEGRADED

    def is_operation_available(self, operation):
        return False

    def execute(self, inputs):
        raise AssertionError("not used")


class _DegradedComfyImage(BaseTool):
    name = "comfyui_image"
    capability = "image_generation"
    provider = "comfyui"
    supports = {"custom_workflow": True}
    input_schema = {"type": "object", "properties": {"workflow_json": {"type": "string"}}}

    def get_status(self):
        return ToolStatus.DEGRADED

    def execute(self, inputs):
        raise AssertionError("not used")


class TestCustomWorkflowSelectorEligibility:

    def test_video_selector_passes_degraded_tool_for_custom_workflow(self):
        selector = VideoSelector()
        candidates = [_DegradedComfyVideo()]
        inputs = {
            "prompt": "x",
            "operation": "text_to_video",
            "workflow_json": "{}",
            "output_node": "14",
        }
        # Without the custom-workflow path this DEGRADED, operation-unready tool
        # would be filtered out; with it, it is eligible and selectable.
        filtered = selector._filter_candidates(inputs, candidates)
        assert [t.name for t in filtered] == ["comfyui_video"]
        assert selector._tool_selectable(candidates[0], inputs) is True

    def test_video_selector_custom_workflow_requires_output_node(self):
        selector = VideoSelector()
        candidates = [_DegradedComfyVideo()]
        inputs = {"prompt": "x", "operation": "text_to_video", "workflow_json": "{}"}
        # output_node missing -> not eligible -> filtered out.
        assert selector._filter_candidates(inputs, candidates) == []
        assert selector._tool_selectable(candidates[0], inputs) is False

    def test_video_selector_custom_workflow_needs_server(self):
        class _OfflineComfyVideo(_DegradedComfyVideo):
            def get_status(self):
                return ToolStatus.UNAVAILABLE

        selector = VideoSelector()
        candidates = [_OfflineComfyVideo()]
        inputs = {
            "prompt": "x",
            "operation": "text_to_video",
            "workflow_json": "{}",
            "output_node": "14",
        }
        assert selector._filter_candidates(inputs, candidates) == []

    def test_image_selector_passes_degraded_tool_for_custom_workflow(self):
        selector = ImageSelector()
        candidates = [_DegradedComfyImage()]
        inputs = {"prompt": "x", "workflow_json": "{}", "output_node": "13"}
        filtered = selector._filter_candidates(inputs, candidates)
        assert [t.name for t in filtered] == ["comfyui_image"]
        assert selector._tool_selectable(candidates[0], inputs) is True

    def test_image_selector_custom_workflow_requires_output_node(self):
        selector = ImageSelector()
        candidates = [_DegradedComfyImage()]
        inputs = {"prompt": "x", "workflow_json": "{}"}
        assert selector._filter_candidates(inputs, candidates) == []
        assert selector._tool_selectable(candidates[0], inputs) is False

    def test_selector_schemas_expose_custom_workflow_inputs(self):
        for selector in (VideoSelector(), ImageSelector()):
            props = selector.input_schema["properties"]
            for field in (
                "workflow_json",
                "workflow_path",
                "output_node",
                "workflow_name",
                "workflow_model",
                "workflow_model_stack",
            ):
                assert field in props, f"{selector.name} missing {field}"


class TestBackendResolution:
    """A configured local server always wins; a lone cloud key means cloud."""

    @pytest.mark.parametrize(
        "local_url,cloud_key,expected",
        [
            ("http://box:8188", None, "local"),
            ("http://box:8188", "k", "local"),   # both set -> cloud is ignored
            (None, "k", "cloud"),
            (None, None, "local"),
        ],
    )
    def test_auto_resolution_table(self, monkeypatch, local_url, cloud_key, expected):
        from tools._comfyui.cloud_client import resolve_backend

        monkeypatch.delenv("COMFYUI_BACKEND", raising=False)
        for var in ("COMFYUI_SERVER_URL", "COMFYUI_IMAGE_SERVER_URL",
                    "COMFYUI_VIDEO_SERVER_URL", "COMFYUI_MUSIC_SERVER_URL",
                    "COMFY_CLOUD_API_KEY"):
            monkeypatch.delenv(var, raising=False)
        if local_url:
            monkeypatch.setenv("COMFYUI_SERVER_URL", local_url)
        if cloud_key:
            monkeypatch.setenv("COMFY_CLOUD_API_KEY", cloud_key)
        assert resolve_backend() == expected

    def test_a_per_capability_local_url_also_counts_as_configured(self, monkeypatch):
        from tools._comfyui.cloud_client import resolve_backend

        monkeypatch.delenv("COMFYUI_BACKEND", raising=False)
        monkeypatch.delenv("COMFYUI_SERVER_URL", raising=False)
        monkeypatch.setenv("COMFYUI_VIDEO_SERVER_URL", "http://gpu:8188")
        monkeypatch.setenv("COMFY_CLOUD_API_KEY", "k")
        assert resolve_backend() == "local"

    def test_explicit_argument_and_env_override(self, monkeypatch):
        from tools._comfyui.cloud_client import resolve_backend

        monkeypatch.setenv("COMFYUI_SERVER_URL", "http://box:8188")
        assert resolve_backend("cloud") == "cloud"
        monkeypatch.setenv("COMFYUI_BACKEND", "cloud")
        assert resolve_backend() == "cloud"
        assert resolve_backend("local") == "local"

    def test_invalid_backend_rejected(self):
        from tools._comfyui.cloud_client import resolve_backend

        with pytest.raises(ValueError):
            resolve_backend("gpu-farm")

    def test_factory_returns_the_right_class(self, monkeypatch):
        from tools._comfyui.client import ComfyUIClient
        from tools._comfyui.cloud_client import ComfyCloudClient, make_client

        monkeypatch.setenv("COMFY_CLOUD_API_KEY", "k")
        assert isinstance(make_client("image", "cloud"), ComfyCloudClient)
        local = make_client("image", "local")
        assert isinstance(local, ComfyUIClient)
        assert not isinstance(local, ComfyCloudClient)


class TestLocalClientKnowsNothingOfCloud:
    """The point of the subclass split: the local client is cloud-free."""

    def test_local_client_source_never_mentions_cloud(self):
        from pathlib import Path
        import tools._comfyui.client as mod

        source = Path(mod.__file__).read_text().lower()
        for term in ("comfy_cloud_api_key", "x-api-key", "extra_data",
                     "cloud.comfy.org", "/api/"):
            assert term not in source, f"local client references {term!r}"

    def test_local_client_defaults(self, monkeypatch):
        from tools._comfyui.client import ComfyUIClient

        monkeypatch.setenv("COMFY_CLOUD_API_KEY", "k")
        client = ComfyUIClient(server_url="http://box:8188")
        assert client.backend == "local"
        assert client.is_cloud is False
        assert client.server_url == "http://box:8188"
        assert client.recovery_hint("p1") == "GET http://box:8188/history/p1"


class TestCloudClient:

    def test_api_prefix_and_auth_header(self, monkeypatch):
        from tools._comfyui.cloud_client import ComfyCloudClient

        monkeypatch.setenv("COMFY_CLOUD_API_KEY", "k-123")
        client = ComfyCloudClient()
        assert client.is_cloud is True
        assert client.backend == "cloud"
        assert client.server_url == "https://cloud.comfy.org/api"
        assert client._headers == {"X-API-Key": "k-123"}
        assert "/api/jobs/p1" in client.recovery_hint("p1")

    def test_unavailable_without_key(self, monkeypatch):
        from tools._comfyui.cloud_client import ComfyCloudClient

        monkeypatch.delenv("COMFY_CLOUD_API_KEY", raising=False)
        client = ComfyCloudClient()
        assert client.is_available() is False
        assert "COMFY_CLOUD_API_KEY" in client.unavailable_reason()

    def test_normalizer_maps_job_record_to_local_shape(self):
        """execution_status IS the local status dict — a rename, not a translation.

        Reading the flat record's top-level `status` yields the bare string
        "completed", and the caller's status_str == "error" check would
        never fire.
        """
        from tools._comfyui.cloud_client import ComfyCloudClient

        entry = ComfyCloudClient.normalize_job({
            "status": "completed",
            "execution_status": {"status_str": "success", "completed": True,
                                 "messages": [["execution_start", {}]]},
            "execution_meta": {"215": {"node_id": "215"}},
            "outputs": {"215": {"audio": [{"filename": "a.mp3",
                                           "subfolder": "audio",
                                           "type": "output"}]}},
        })
        assert entry["status"]["status_str"] == "success"
        assert entry["meta"] == {"215": {"node_id": "215"}}
        assert entry["outputs"]["215"]["audio"][0]["filename"] == "a.mp3"

    def test_normalizer_preserves_failure_signal(self):
        from tools._comfyui.cloud_client import ComfyCloudClient

        entry = ComfyCloudClient.normalize_job({
            "status": "completed",
            "execution_status": {"status_str": "error", "messages": ["boom"]},
            "outputs": {},
        })
        assert entry["status"]["status_str"] == "error"

    @pytest.mark.parametrize("code,needle", [
        (401, "COMFY_CLOUD_API_KEY"),
        (402, "out of credits"),
        (429, "subscription is inactive"),
    ])
    def test_billing_and_auth_errors_are_explicit_blockers(self, code, needle):
        """402 and 429 look like throttling; retrying them can never work."""
        from tools._comfyui.client import ComfyUIError
        from tools._comfyui.cloud_client import ComfyCloudClient

        resp = type("R", (), {
            "status_code": code,
            "json": lambda self: {"code": "X", "message": "nope"},
            "text": "nope",
        })()
        with pytest.raises(ComfyUIError) as exc:
            ComfyCloudClient()._raise_for_error(resp)
        assert needle in str(exc.value)

    def test_failed_job_error_names_the_node(self):
        from tools._comfyui.cloud_client import describe_cloud_error

        described = describe_cloud_error({"error_message": json.dumps({
            "exception_message": "Unauthorized: Please login first to use this node.",
            "node_id": "208", "node_type": "ElevenLabsTextToSpeech",
        })})
        assert "ElevenLabsTextToSpeech" in described
        assert "Unauthorized" in described

    def test_failed_status_is_terminal(self):
        """'failed' is undocumented but real; polling it forever is a hang."""
        from tools._comfyui.cloud_client import CLOUD_TERMINAL

        assert "failed" in CLOUD_TERMINAL

    def test_submit_carries_the_partner_credential(self, monkeypatch):
        """Partner nodes read the key from extra_data, not the header."""
        from tools._comfyui.cloud_client import ComfyCloudClient

        monkeypatch.setenv("COMFY_CLOUD_API_KEY", "k-777")
        seen = {}

        def fake_post(url, json=None, timeout=None, headers=None):
            seen.update(json or {})
            return type("R", (), {
                "status_code": 200,
                "raise_for_status": lambda self: None,
                "json": lambda self: {"prompt_id": "p1"},
            })()

        monkeypatch.setattr(
            "tools._comfyui.cloud_client.requests.post", fake_post)
        ComfyCloudClient().submit({"1": {"inputs": {}}})
        assert seen["extra_data"] == {"api_key_comfy_org": "k-777"}

    def test_object_info_is_fetched_once(self, monkeypatch):
        """Cloud only serves the full ~10MB payload — memoize it."""
        from tools._comfyui.cloud_client import ComfyCloudClient

        monkeypatch.setenv("COMFY_CLOUD_API_KEY", "k")
        calls = []

        def fake_get(url, headers=None, timeout=None, params=None):
            calls.append(url)
            return type("R", (), {
                "status_code": 200,
                "raise_for_status": lambda self: None,
                "json": lambda self: {"UNETLoader": {"input": {"required": {
                    "unet_name": [["a.safetensors"]]}}}},
            })()

        monkeypatch.setattr("tools._comfyui.cloud_client.requests.get", fake_get)
        client = ComfyCloudClient()
        client.list_models()
        client.has_node("UNETLoader")
        client.check_models(["a.safetensors"])
        assert all(u.endswith("/api/object_info") for u in calls)
        assert len(calls) == 1, f"object_info fetched {len(calls)} times"


class TestPartnerNodeGraphs:
    """Partner API nodes have tighter input ranges than the local graphs."""

    def test_partner_seed_is_clamped_to_int32(self):
        """random_seed() draws UINT32; partner nodes cap at INT32_MAX."""
        workflow, _ = ComfyUIVideo._build_partner_t2v(
            {"prompt": "a wave", "duration": 5},
            4_161_237_130,  # a real UINT32 seed that failed validation
            Path("out.mp4"),
            "seedance_2.5",
        )
        assert workflow["1"]["inputs"]["seed"] <= 2_147_483_647

    def test_partner_seed_left_alone_when_already_in_range(self):
        workflow, _ = ComfyUIVideo._build_partner_t2v(
            {"prompt": "a wave"}, 42, Path("out.mp4"), "seedance_2.5"
        )
        assert workflow["1"]["inputs"]["seed"] == 42

    def test_model_uses_flattened_dynamic_combo_keys(self):
        """COMFY_DYNAMICCOMBO_V3 takes the combo key plus `model.<name>`.

        Nesting the parameters passes submit-time validation and then dies
        at execution with "missing 1 required positional argument".
        """
        workflow, _ = ComfyUIVideo._build_partner_t2v(
            {"prompt": "a wave"}, 1, Path("o.mp4"), "seedance_2.5"
        )
        node = workflow["1"]["inputs"]
        assert node["model"] == "Seedance 2.5"
        assert node["model.prompt"] == "a wave"
        assert not isinstance(node["model"], dict)

    def test_seedance_25_sends_required_output_format(self):
        workflow, _ = ComfyUIVideo._build_partner_t2v(
            {"prompt": "a wave"}, 1, Path("o.mp4"), "seedance_2.5"
        )
        assert workflow["1"]["inputs"]["model.output_format"] == "mp4"

    def test_every_partner_family_flattens(self):
        for family in ("gemini_omni_flash", "seedance_2.5", "minimax_h3_api"):
            workflow, out = ComfyUIVideo._build_partner_t2v(
                {"prompt": "x"}, 1, Path("o.mp4"), family
            )
            node = workflow["1"]["inputs"]
            assert isinstance(node["model"], str), family
            assert any(k.startswith("model.") for k in node), family
            assert out == "2"


class TestNegativePrompt:

    def test_appends_rather_than_replaces(self):
        """The bundled quality negative must survive a caller's additions."""
        tool = ComfyUIVideo()
        base, _ = tool._build_t2v({"prompt": "x"}, 1, Path("o.mp4"))
        stock = base["3"]["inputs"]["text"]

        merged, _ = tool._build_t2v(
            {"prompt": "x", "negative_prompt": "people, crew"}, 1, Path("o.mp4")
        )
        text = merged["3"]["inputs"]["text"]
        assert text.startswith(stock)
        assert "people, crew" in text

    def test_optional(self):
        tool = ComfyUIVideo()
        a, _ = tool._build_t2v({"prompt": "x"}, 1, Path("o.mp4"))
        b, _ = tool._build_t2v({"prompt": "x", "negative_prompt": ""}, 1, Path("o.mp4"))
        assert a["3"]["inputs"]["text"] == b["3"]["inputs"]["text"]


class TestBackendSurfaceOnTools:

    def test_tools_expose_backend_input(self):
        for cls in (ComfyUIImage, ComfyUIVideo, ComfyUIMusic):
            prop = cls.input_schema["properties"]["backend"]
            assert prop["enum"] == ["local", "cloud", "auto"]
            assert prop["default"] == "auto"

    def test_cloud_runs_cost_money_local_is_free(self, monkeypatch):
        monkeypatch.setenv("COMFY_CLOUD_API_KEY", "k")
        for cls in (ComfyUIImage, ComfyUIVideo, ComfyUIMusic):
            tool = cls()
            assert tool.estimate_cost({"backend": "local"}) == 0.0
            assert tool.estimate_cost({"backend": "cloud"}) > 0.0

    def test_cloud_swaps_models_the_hosted_catalog_has(self):
        """Cloud has no NVFP4 build; the graph must name what exists there."""
        from tools._comfyui.metadata import apply_backend_models, backend_models

        workflow = {
            "1": {"class_type": "UNETLoader",
                  "inputs": {"unet_name": "flux2-dev-nvfp4.safetensors"}},
            "3": {"class_type": "VAELoader",
                  "inputs": {"vae_name": "flux2-vae.safetensors"}},
        }
        patched = apply_backend_models(
            workflow, workflow_key="flux2-txt2img", backend="cloud")
        assert patched["1"]["inputs"]["unet_name"] == "flux2-dev.safetensors"
        assert patched["3"]["inputs"]["vae_name"] == "flux2-vae.safetensors"
        assert backend_models(["flux2-dev-nvfp4.safetensors"],
                              workflow_key="flux2-txt2img",
                              backend="cloud") == ["flux2-dev.safetensors"]

    def test_local_backend_leaves_workflow_untouched(self):
        from tools._comfyui.metadata import apply_backend_models

        workflow = {"1": {"class_type": "UNETLoader",
                          "inputs": {"unet_name": "flux2-dev-nvfp4.safetensors"}}}
        patched = apply_backend_models(
            workflow, workflow_key="flux2-txt2img", backend="local")
        assert patched["1"]["inputs"]["unet_name"] == "flux2-dev-nvfp4.safetensors"


class TestSetupMetadataMentionsCloud:
    """AGENT_GUIDE has agents build the setup menu from this metadata.

    If install_instructions only describes standing up a local server, a
    user with no GPU is told to install ComfyUI and never learns a cloud key
    is an option — the provider menu would be accurate but incomplete.
    """

    def test_install_instructions_offer_the_cloud_path(self):
        for cls in (ComfyUIImage, ComfyUIVideo, ComfyUIMusic):
            text = cls.install_instructions
            assert "COMFY_CLOUD_API_KEY" in text, cls.__name__
            assert "platform.comfy.org" in text, cls.__name__
            # and must still explain precedence, or users will assume the
            # key alone switches them over
            assert "COMFYUI_BACKEND" in text, cls.__name__

    def test_setup_offer_carries_the_hosted_alternative(self):
        from tools._comfyui.metadata import COMFYUI_SETUP_OFFER

        alt = COMFYUI_SETUP_OFFER["alternative"]
        assert alt["env_var"] == "COMFY_CLOUD_API_KEY"
        assert alt["kind"] == "hosted"
        # Cost honesty is a review-guide requirement for paid providers.
        assert "metered" in alt["billing"]

    def test_supports_flags_declare_the_cloud_backend(self):
        for cls in (ComfyUIImage, ComfyUIVideo, ComfyUIMusic):
            assert cls.supports.get("comfy_cloud_backend") is True, cls.__name__

    def test_local_setup_offer_is_unchanged(self):
        """The hosted option is additive — it must not displace the local one."""
        from tools._comfyui.metadata import COMFYUI_SETUP_OFFER

        assert COMFYUI_SETUP_OFFER["kind"] == "local_server"
        assert COMFYUI_SETUP_OFFER["env_var"] == "COMFYUI_SERVER_URL"
        assert COMFYUI_SETUP_OFFER["health_check"] == "GET /system_stats"
