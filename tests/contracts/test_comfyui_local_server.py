"""End-to-end tests for the LOCAL ComfyUI path against a fake ComfyUI server.

The Comfy Cloud work refactored code shared by both backends — `is_available`,
`list_models`/`has_node` (now routed through `_object_info`), `submit`,
`_history_entry`, `download` and `upload_image` all gained branches. Mocked
unit tests can pin the branch that was taken, but they cannot prove the local
path still speaks the protocol correctly end to end, and not everyone
reviewing this has a GPU box to point it at.

So this stands up a real HTTP server implementing ComfyUI's local REST
contract and drives the three tools against it for real: URL construction,
headers, polling, artifact discovery and download all execute unmodified.
The session network guard permits loopback precisely for fixtures like this.

What the fake deliberately does NOT do is accept an X-API-Key or an /api
prefix — if the cloud branch ever leaks into the local path, these fail.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

from tools.audio.comfyui_music import ComfyUIMusic
from tools.graphics.comfyui_image import ComfyUIImage
from tools.video.comfyui_video import ComfyUIVideo

# Every model filename the three bundled workflows ask for.
_INSTALLED_MODELS = [
    "flux2-dev-nvfp4.safetensors",
    "mistral_3_small_flux2_fp4_mixed.safetensors",
    "flux2-vae.safetensors",
    "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
    "wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors",
    "wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors",
    "wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors",
    "wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors",
    "wan_2.1_vae.safetensors",
    "wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors",
    "wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors",
    "wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors",
    "wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors",
    "ace_step_v1_3.5b.safetensors",
]

# Which media key a Save* node reports its artifact under, mirroring ComfyUI.
_SAVE_NODE_KEYS = {
    "SaveImage": "images",
    "SaveVideo": "gifs",
    "SaveAudioMP3": "audio",
    "SaveAudio": "audio",
}

_ARTIFACT_BYTES = b"OPENMONTAGE-FAKE-ARTIFACT-PAYLOAD" * 4


class _State:
    """Everything the fake server records, for assertions."""

    def __init__(self) -> None:
        self.paths: list[str] = []
        self.saw_auth_header = False
        self.submitted: list[dict] = []
        self.uploads: list[str] = []
        self.outputs: dict[str, dict] = {}


def _node_defs(node_class: str) -> dict:
    field = {
        "CheckpointLoaderSimple": "ckpt_name",
        "UNETLoader": "unet_name",
        "VAELoader": "vae_name",
        "CLIPLoader": "clip_name",
        "LoraLoaderModelOnly": "lora_name",
    }.get(node_class, "value")
    return {node_class: {"input": {"required": {field: [_INSTALLED_MODELS, {}]}}}}


def _make_handler(state: _State):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # keep pytest output clean
            pass

        def _record(self) -> None:
            state.paths.append(self.path)
            if self.headers.get("X-API-Key"):
                state.saw_auth_header = True

        def _send(self, payload, status=200, raw=False):
            body = payload if raw else json.dumps(payload).encode()
            self.send_response(status)
            self.send_header(
                "Content-Type",
                "application/octet-stream" if raw else "application/json",
            )
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):  # noqa: N802
            self._record()
            route = urlparse(self.path).path
            if route == "/system_stats":
                return self._send({"system": {"comfyui_version": "fake"}})
            if route.startswith("/object_info/"):
                return self._send(_node_defs(route.rsplit("/", 1)[1]))
            if route.startswith("/history/"):
                prompt_id = route.rsplit("/", 1)[1]
                entry = state.outputs.get(prompt_id)
                # ComfyUI returns {} until the job finishes; returning the
                # entry immediately keeps the test fast while still exercising
                # the "entry appears means done" contract the local path uses.
                return self._send({prompt_id: entry} if entry else {})
            if route == "/view":
                return self._send(_ARTIFACT_BYTES, raw=True)
            return self._send({"error": "not found"}, status=404)

        def do_POST(self):  # noqa: N802
            self._record()
            route = urlparse(self.path).path
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else b""

            if route == "/prompt":
                payload = json.loads(body)
                state.submitted.append(payload)
                prompt_id = f"fake-{len(state.submitted)}"
                workflow = payload.get("prompt", {})
                outputs = {}
                for node_id, node in workflow.items():
                    key = _SAVE_NODE_KEYS.get(node.get("class_type", ""))
                    if key:
                        outputs[node_id] = {key: [{
                            "filename": f"{node_id}_00001.bin",
                            "subfolder": "",
                            "type": "output",
                        }]}
                state.outputs[prompt_id] = {
                    "outputs": outputs,
                    "status": {"status_str": "success", "completed": True,
                               "messages": []},
                    "meta": {},
                }
                return self._send({"prompt_id": prompt_id})

            if route == "/upload/image":
                name = f"uploaded_{len(state.uploads)}.png"
                state.uploads.append(name)
                return self._send({"name": name, "subfolder": ""})

            return self._send({"error": "not found"}, status=404)

    return Handler


@pytest.fixture()
def fake_comfyui(monkeypatch):
    """Run a fake local ComfyUI and point the tools at it."""
    state = _State()
    server = ThreadingHTTPServer(("127.0.0.1", 0), _make_handler(state))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_address[1]}"

    monkeypatch.setenv("COMFYUI_SERVER_URL", url)
    monkeypatch.setenv("COMFYUI_BACKEND", "local")
    for var in ("COMFYUI_IMAGE_SERVER_URL", "COMFYUI_VIDEO_SERVER_URL",
                "COMFYUI_MUSIC_SERVER_URL", "COMFY_CLOUD_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    try:
        yield state, url
    finally:
        server.shutdown()
        server.server_close()


class TestLocalDiscovery:

    def test_tools_report_available_against_a_local_server(self, fake_comfyui):
        for cls in (ComfyUIImage, ComfyUIVideo, ComfyUIMusic):
            tool = cls()
            assert tool._client.backend == "local"
            assert tool._client.is_available() is True
            assert tool.get_status().value == "available", cls.__name__

    def test_model_discovery_uses_the_per_node_route(self, fake_comfyui):
        state, _ = fake_comfyui
        tool = ComfyUIImage()
        found, missing = tool._client.check_models(
            ["flux2-dev-nvfp4.safetensors", "not-installed.safetensors"]
        )
        assert found == ["flux2-dev-nvfp4.safetensors"]
        assert missing == ["not-installed.safetensors"]
        assert any(p.startswith("/object_info/") for p in state.paths)
        assert not any(p.startswith("/api/") for p in state.paths)

    def test_missing_models_degrade_rather_than_fail(self, fake_comfyui, monkeypatch):
        monkeypatch.setitem(
            __import__("tools.graphics.comfyui_image", fromlist=["x"]).__dict__,
            "_REQUIRED_MODELS", ["absent.safetensors"],
        )
        assert ComfyUIImage().get_status().value == "degraded"


class TestLocalGeneration:
    """The whole local cycle: submit, poll, locate artifact, download."""

    def test_image_writes_a_real_file(self, fake_comfyui, tmp_path):
        state, _ = fake_comfyui
        out = tmp_path / "img.png"
        result = ComfyUIImage().execute({
            "prompt": "a lighthouse", "width": 512, "height": 512, "seed": 3,
            "output_path": str(out), "timeout_seconds": 15,
        })
        assert result.success, result.error
        assert out.read_bytes() == _ARTIFACT_BYTES
        assert result.cost_usd == 0.0
        assert result.data["model"] == "flux2-dev-nvfp4"

        submitted = state.submitted[0]["prompt"]
        assert submitted["4"]["inputs"]["text"] == "a lighthouse"
        assert submitted["7"]["inputs"]["noise_seed"] == 3
        # Local must keep the NVFP4 filename — the swap is cloud-only.
        assert submitted["1"]["inputs"]["unet_name"] == "flux2-dev-nvfp4.safetensors"
        assert "extra_data" not in state.submitted[0]
        assert state.saw_auth_header is False

    def test_text_to_video_writes_a_real_file(self, fake_comfyui, tmp_path):
        state, _ = fake_comfyui
        out = tmp_path / "clip.mp4"
        result = ComfyUIVideo().execute({
            "operation": "text_to_video", "prompt": "waves", "seed": 5,
            "output_path": str(out), "timeout_seconds": 15,
        })
        assert result.success, result.error
        assert out.read_bytes() == _ARTIFACT_BYTES
        submitted = state.submitted[0]["prompt"]
        assert submitted["2"]["inputs"]["text"] == "waves"
        assert submitted["12"]["inputs"]["noise_seed"] == 5

    def test_image_to_video_uploads_the_reference(self, fake_comfyui, tmp_path):
        state, _ = fake_comfyui
        ref = tmp_path / "ref.png"
        ref.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 32)
        out = tmp_path / "clip.mp4"

        result = ComfyUIVideo().execute({
            "operation": "image_to_video", "prompt": "drift",
            "reference_image_path": str(ref), "seed": 7,
            "output_path": str(out), "timeout_seconds": 15,
        })
        assert result.success, result.error
        assert out.read_bytes() == _ARTIFACT_BYTES
        assert state.uploads, "reference image was never uploaded"
        submitted = state.submitted[0]["prompt"]
        assert submitted["97"]["inputs"]["image"] == state.uploads[0]

    def test_music_writes_a_real_file(self, fake_comfyui, tmp_path):
        out = tmp_path / "track.mp3"
        result = ComfyUIMusic().execute({
            "prompt": "ambient drone", "duration_seconds": 10, "seed": 11,
            "output_path": str(out), "timeout_seconds": 15,
        })
        assert result.success, result.error
        assert out.read_bytes() == _ARTIFACT_BYTES
        assert result.cost_usd == 0.0

    def test_custom_workflow_with_output_node(self, fake_comfyui, tmp_path):
        """The override contract must keep working on local."""
        out = tmp_path / "custom.png"
        workflow = {
            "1": {"class_type": "SaveImage",
                  "inputs": {"filename_prefix": "custom"}},
        }
        result = ComfyUIImage().execute({
            "prompt": "unused by the custom graph",
            "workflow_json": json.dumps(workflow),
            "output_node": "1",
            "output_path": str(out), "timeout_seconds": 15, "timeout_seconds": 15,
        })
        assert result.success, result.error
        assert out.read_bytes() == _ARTIFACT_BYTES

    def test_custom_workflow_without_output_node_is_rejected(self, fake_comfyui):
        result = ComfyUIImage().execute({
            "prompt": "x", "workflow_json": "{}",
        })
        assert result.success is False
        assert "output_node" in result.error


class TestLocalStaysLocal:
    """Guard against the cloud branch leaking into the local path."""

    def test_no_api_prefix_and_no_auth_header_anywhere(self, fake_comfyui, tmp_path):
        state, _ = fake_comfyui
        ComfyUIImage().execute({
            "prompt": "x", "output_path": str(tmp_path / "a.png"),
            "timeout_seconds": 15,
        })
        ComfyUIMusic().execute({
            "prompt": "y", "output_path": str(tmp_path / "b.mp3"),
            "timeout_seconds": 15,
        })
        assert state.paths, "the fake server was never contacted"
        assert not any(p.startswith("/api/") for p in state.paths)
        assert state.saw_auth_header is False
        assert all("extra_data" not in s for s in state.submitted)

    def test_unreachable_local_server_reports_a_local_reason(self, monkeypatch):
        monkeypatch.setenv("COMFYUI_SERVER_URL", "http://127.0.0.1:1")
        monkeypatch.setenv("COMFYUI_BACKEND", "local")
        monkeypatch.delenv("COMFY_CLOUD_API_KEY", raising=False)
        tool = ComfyUIImage()
        assert tool._client.is_available() is False
        reason = tool._client.unavailable_reason()
        assert "127.0.0.1:1" in reason
        assert "Comfy Cloud" not in reason
