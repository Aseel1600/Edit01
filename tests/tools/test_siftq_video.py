"""Contract coverage for the independent SiftQ MiniMax-H3 provider."""

from __future__ import annotations

import base64

import pytest
import requests

from tools.base_tool import ToolStatus


class _FakeResponse:
    def __init__(
        self,
        *,
        status_code=200,
        json_data=None,
        content=b"",
        headers=None,
        json_error=None,
    ):
        self.status_code = status_code
        self._json = json_data
        self.content = content
        self.headers = headers or {}
        self._json_error = json_error

    def json(self):
        if self._json_error:
            raise self._json_error
        return self._json


@pytest.fixture(autouse=True)
def _isolate_siftq_environment(monkeypatch):
    monkeypatch.delenv("SIFTQ_API_KEY", raising=False)
    monkeypatch.delenv("SIFTQ_BASE_URL", raising=False)


def _success_task(task_id="task-123", *, resolution="2K", image_count=0):
    return {
        "task": {
            "id": task_id,
            "model": "MiniMax-H3",
            "status": "succeeded",
            "error": None,
            "content": {"url": "https://cdn.example/output.mp4?token=secret"},
            "resolution": resolution,
            "duration": 5,
            "ratio": "16:9",
            "task_type": "generation",
            "modality": "video",
            "usage": {
                "total_seconds": 5,
                "input_seconds": 0,
                "output_seconds": 5,
                "input_image_count": image_count,
            },
        }
    }


def _mock_success(monkeypatch, *, task=None):
    calls = {"get": []}

    def fake_post(url, headers=None, json=None, timeout=None):
        calls["post_url"] = url
        calls["headers"] = headers
        calls["payload"] = json
        calls["post_timeout"] = timeout
        return _FakeResponse(json_data={"task_id": "task-123"})

    def fake_get(url, headers=None, timeout=None):
        calls["get"].append((url, headers, timeout))
        if "/v2/query/video_generation/" in url:
            return _FakeResponse(json_data=task or _success_task())
        return _FakeResponse(
            content=b"\x00\x00\x00\x18ftypisomvideo",
            headers={"Content-Type": "video/mp4"},
        )

    monkeypatch.setattr(requests, "post", fake_post)
    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr("tools.video.siftq_video.time.sleep", lambda _seconds: None)
    return calls


def test_siftq_video_is_discovered_as_independent_provider():
    from tools.tool_registry import ToolRegistry
    from tools.video.siftq_video import SiftQVideo

    registry = ToolRegistry()
    registry.discover()

    tool = registry.get("siftq_video")
    assert isinstance(tool, SiftQVideo)
    assert tool.provider == "siftq"
    assert tool.capability == "video_generation"
    assert tool.dependencies == ["env:SIFTQ_API_KEY"]
    assert tool.agent_skills == ["siftq-video", "ai-video-gen"]
    assert "native_audio" not in tool.supports
    assert "$0.015/sec" in tool.best_for[0]
    assert "$0.025/sec" in tool.best_for[0]
    assert "81%" in tool.best_for[1]
    assert "$0.015/sec" in tool.install_instructions
    assert "$0.025/sec" in tool.install_instructions


def test_siftq_video_availability_and_base_url(monkeypatch):
    from tools.video.siftq_video import SiftQVideo

    tool = SiftQVideo()
    assert tool.get_status() == ToolStatus.UNAVAILABLE
    monkeypatch.setenv("SIFTQ_API_KEY", "siftq-test-key")
    assert tool.get_status() == ToolStatus.AVAILABLE
    assert tool._endpoint("v2/video_generation") == (
        "https://siftq.com/api/minimax/v2/video_generation"
    )

    monkeypatch.setenv("SIFTQ_BASE_URL", "https://gateway.example.test/custom")
    assert tool._endpoint("/v2/video_generation") == (
        "https://gateway.example.test/custom/v2/video_generation"
    )
    monkeypatch.setenv("SIFTQ_BASE_URL", "https://gateway.example.test/custom/")
    assert tool._endpoint("v2/video_generation") == (
        "https://gateway.example.test/custom/v2/video_generation"
    )

    monkeypatch.setenv("SIFTQ_BASE_URL", "not-a-url")
    with pytest.raises(ValueError, match="absolute HTTP"):
        tool._endpoint("v2/video_generation")


def test_missing_key_fails_before_network(monkeypatch):
    from tools.video.siftq_video import SiftQVideo

    monkeypatch.setattr(
        requests,
        "post",
        lambda *args, **kwargs: pytest.fail("missing credentials must not call network"),
    )
    result = SiftQVideo().execute({"prompt": "x"})
    assert not result.success
    assert "SIFTQ_API_KEY not set" in result.error


def test_text_to_video_payload_and_download(monkeypatch, tmp_path):
    from tools.video.siftq_video import SiftQVideo

    monkeypatch.setenv("SIFTQ_API_KEY", "siftq-test-key")
    calls = _mock_success(monkeypatch)
    output_path = tmp_path / "result.mp4"

    result = SiftQVideo().execute(
        {
            "prompt": "A slow product dolly-in",
            "duration": "5",
            "resolution": "768P",
            "ratio": "16:9",
            "poll_interval_seconds": 0,
            "output_path": str(output_path),
        }
    )

    assert result.success, result.error
    assert calls["post_url"] == "https://siftq.com/api/minimax/v2/video_generation"
    assert calls["headers"] == {
        "Authorization": "Bearer siftq-test-key",
        "Content-Type": "application/json",
    }
    assert calls["payload"] == {
        "model": "MiniMax-H3",
        "content": [{"type": "text", "text": "A slow product dolly-in"}],
        "resolution": "768P",
        "duration": 5,
        "ratio": "16:9",
    }
    assert calls["get"][0][0].endswith("/v2/query/video_generation/task-123")
    assert calls["get"][1][0].startswith("https://cdn.example/output.mp4")
    assert output_path.read_bytes().startswith(b"\x00\x00\x00\x18ftyp")
    assert result.data["provider"] == "siftq"
    assert result.data["task_id"] == "task-123"
    assert "source_url" not in result.data
    assert result.cost_usd == pytest.approx(0.125)


def test_image_and_first_last_payloads_force_adaptive_ratio(monkeypatch):
    from tools.video.siftq_video import SiftQVideo

    tool = SiftQVideo()
    monkeypatch.setattr(tool, "_media_url", lambda value, kind: f"media:{value}")

    image_payload = tool._build_payload(
        {
            "prompt": "Animate the portrait",
            "operation": "image_to_video",
            "reference_image_path": "portrait.png",
            "aspect_ratio": "9:16",
        }
    )
    assert image_payload["ratio"] == "adaptive"
    assert image_payload["content"][1] == {
        "type": "image_url",
        "image_url": {"url": "media:portrait.png"},
        "role": "first_frame",
    }

    first_last = tool._build_payload(
        {
            "prompt": "Move between frames",
            "operation": "first_last_frame_to_video",
            "first_frame_image": "first.png",
            "last_image_path": "last.png",
            "ratio": "1:1",
        }
    )
    assert first_last["ratio"] == "adaptive"
    assert [item.get("role") for item in first_last["content"]] == [
        None,
        "first_frame",
        "last_frame",
    ]


def test_reference_payload_supports_images_videos_and_audio(monkeypatch):
    from tools.video.siftq_video import SiftQVideo

    tool = SiftQVideo()
    monkeypatch.setattr(tool, "_media_url", lambda value, kind: f"{kind}:{value}")
    payload = tool._build_payload(
        {
            "prompt": "Follow the visual identity and rhythm",
            "operation": "reference_to_video",
            "reference_image_urls": ["https://example.test/one.png"],
            "reference_video_path": "reference.mp4",
            "reference_audio_urls": ["https://example.test/beat.mp3"],
            "ratio": "9:16",
        }
    )

    assert payload["ratio"] == "9:16"
    assert [(item["type"], item.get("role")) for item in payload["content"]] == [
        ("text", None),
        ("image_url", "reference_image"),
        ("video_url", "reference_video"),
        ("audio_url", "reference_audio"),
    ]


@pytest.mark.parametrize(
    ("inputs", "message"),
    [
        ({"prompt": ""}, "non-empty"),
        ({"prompt": "x" * 7001}, "7000"),
        ({"prompt": "x", "model": "other"}, "model"),
        ({"prompt": "x", "resolution": "1080P"}, "resolution"),
        ({"prompt": "x", "duration": 0}, "4 to 15"),
        ({"prompt": "x", "duration": True}, "4 to 15"),
        ({"prompt": "x", "duration": 4.5}, "4 to 15"),
        ({"prompt": "x", "ratio": "adaptive"}, "concrete ratio"),
        (
            {"prompt": "x", "operation": "image_to_video"},
            "first-frame image",
        ),
        (
            {
                "prompt": "x",
                "operation": "first_last_frame_to_video",
                "first_frame_image": "https://example.test/first.png",
            },
            "last-frame image",
        ),
        (
            {"prompt": "x", "operation": "reference_to_video"},
            "at least one reference",
        ),
        (
            {
                "prompt": "x",
                "operation": "reference_to_video",
                "reference_audio_urls": ["https://example.test/audio.mp3"],
            },
            "requires at least one reference image or video",
        ),
    ],
)
def test_payload_validation(inputs, message):
    from tools.video.siftq_video import SiftQVideo

    with pytest.raises(ValueError, match=message):
        SiftQVideo()._build_payload(inputs)


def test_reference_count_limits(monkeypatch):
    from tools.video.siftq_video import SiftQVideo

    tool = SiftQVideo()
    monkeypatch.setattr(tool, "_media_url", lambda value, kind: str(value))
    base = {"prompt": "x", "operation": "reference_to_video"}
    with pytest.raises(ValueError, match="at most 9"):
        tool._build_payload(
            {**base, "reference_image_urls": [f"https://x/{i}.png" for i in range(10)]}
        )
    with pytest.raises(ValueError, match="at most 3 reference videos"):
        tool._build_payload(
            {**base, "reference_video_urls": [f"https://x/{i}.mp4" for i in range(4)]}
        )
    with pytest.raises(ValueError, match="at most 3 reference audio"):
        tool._build_payload(
            {
                **base,
                "reference_image_url": "https://x/image.png",
                "reference_audio_urls": [f"https://x/{i}.mp3" for i in range(4)],
            }
        )


def test_known_reference_durations_cannot_exceed_total_limit(monkeypatch):
    from tools.video.siftq_video import SiftQVideo

    tool = SiftQVideo()
    monkeypatch.setattr(tool, "_media_url", lambda value, kind: str(value))
    monkeypatch.setattr(tool, "_known_media_duration", lambda value, kind: 8.0)
    with pytest.raises(ValueError, match="total local reference video duration"):
        tool._build_payload(
            {
                "prompt": "x",
                "operation": "reference_to_video",
                "reference_video_urls": [
                    "https://x/one.mp4",
                    "https://x/two.mp4",
                ],
            }
        )


def test_data_uri_validation_rejects_wrong_mime_and_invalid_base64():
    from tools.video.siftq_video import SiftQVideo

    tool = SiftQVideo()
    with pytest.raises(ValueError, match="lowercase"):
        tool._validate_data_uri("data:IMAGE/PNG;base64,AAAA", "image")
    with pytest.raises(ValueError, match="unsupported image"):
        tool._validate_data_uri("data:image/gif;base64,AAAA", "image")
    with pytest.raises(ValueError, match="invalid base64"):
        tool._validate_data_uri("data:audio/mp3;base64,abc", "audio")


def test_local_file_becomes_lowercase_data_uri(monkeypatch, tmp_path):
    from tools.video.siftq_video import SiftQVideo

    source = tmp_path / "reference.MP3"
    source.write_bytes(b"audio")
    tool = SiftQVideo()
    monkeypatch.setattr(tool, "_validate_local_timed_media", lambda path, kind: None)

    value = tool._media_url(source, "audio")
    assert value == "data:audio/mp3;base64," + base64.b64encode(b"audio").decode("ascii")


def test_cost_uses_siftq_rates_and_usage():
    from tools.video.siftq_video import (
        INCLUDED_REFERENCE_IMAGES,
        PRICE_PER_SECOND_USD,
        REFERENCE_IMAGE_PRICE_USD,
        SiftQVideo,
    )

    tool = SiftQVideo()
    assert PRICE_PER_SECOND_USD == {"768P": 0.015, "2K": 0.025}
    assert INCLUDED_REFERENCE_IMAGES == 5
    assert REFERENCE_IMAGE_PRICE_USD == 0.008
    refs = [f"https://x/{index}.png" for index in range(7)]
    assert tool.estimate_cost(
        {
            "duration": 10,
            "resolution": "768P",
            "reference_image_urls": refs,
            "reference_video_duration_seconds": 4,
        }
    ) == pytest.approx(0.226)
    task = _success_task(resolution="2K", image_count=7)["task"]
    task["usage"]["input_seconds"] = 3
    assert tool._cost_from_task(task, {}) == pytest.approx(0.216)


def test_siftq_skill_metadata_uses_official_logo_and_current_rates():
    from pathlib import Path

    skill_dir = Path(".agents/skills/siftq-video")
    skill = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    metadata = (skill_dir / "agents/openai.yaml").read_text(encoding="utf-8")
    logo = (skill_dir / "assets/siftq-logo-symbol.png").read_bytes()

    assert "$0.015/sec" in skill
    assert "$0.025/sec" in skill
    assert "81%" in skill
    assert "lowest" in skill.lower()
    assert metadata.count("./assets/siftq-logo-symbol.png") == 2
    assert logo.startswith(b"\x89PNG\r\n\x1a\n")


def test_polling_accepts_queued_running_and_lowercase_success(monkeypatch):
    from tools.video.siftq_video import SiftQVideo

    statuses = iter(["queued", "running", "succeeded"])
    tool = SiftQVideo()
    monkeypatch.setattr(
        tool,
        "_query_task",
        lambda task_id, api_key: {
            "status": next(statuses),
            "content": {"url": "https://x/video.mp4"},
        },
    )
    monkeypatch.setattr("tools.video.siftq_video.time.sleep", lambda _seconds: None)
    assert tool._poll_task("id", "key", interval=0, timeout=10)["status"] == "succeeded"


def test_polling_rejects_unknown_or_legacy_status(monkeypatch):
    from tools.video.siftq_video import SiftQVideo

    tool = SiftQVideo()
    monkeypatch.setattr(
        tool, "_query_task", lambda task_id, api_key: {"status": "Success"}
    )
    with pytest.raises(RuntimeError, match="unknown task status"):
        tool._poll_task("id", "key", interval=0, timeout=10)


def test_task_query_url_encodes_id_and_retries_safe_get(monkeypatch):
    from tools.video.siftq_video import SiftQVideo

    responses = iter(
        [
            _FakeResponse(
                status_code=529,
                json_data={
                    "type": "error",
                    "error": {"type": "overloaded_error", "message": "busy"},
                },
            ),
            _FakeResponse(json_data={"task": {"status": "queued"}}),
        ]
    )
    urls = []

    def fake_get(url, **kwargs):
        urls.append(url)
        return next(responses)

    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr("tools.video.siftq_video.time.sleep", lambda _seconds: None)
    task = SiftQVideo()._query_task("task/with slash", "key")
    assert task["status"] == "queued"
    assert len(urls) == 2
    assert urls[0].endswith("/task%2Fwith%20slash")


def test_timeout_preserves_task_id(monkeypatch):
    import tools.video.siftq_video as siftq_module
    from tools.video.siftq_video import SiftQVideo

    monkeypatch.setenv("SIFTQ_API_KEY", "siftq-test-key")
    monkeypatch.setattr(SiftQVideo, "_create_task", lambda self, payload, key: "recover-me")
    monkeypatch.setattr(
        SiftQVideo,
        "_query_task",
        lambda self, task_id, key: {"status": "queued"},
    )

    class _Clock:
        def __init__(self):
            self.values = iter([0.0, 2.0])

        @staticmethod
        def time():
            return 0.0

        def monotonic(self):
            return next(self.values)

        @staticmethod
        def sleep(_seconds):
            return None

    monkeypatch.setattr(siftq_module, "time", _Clock())
    result = SiftQVideo().execute({"prompt": "x", "timeout_seconds": 1})
    assert not result.success
    assert result.data["task_id"] == "recover-me"
    assert result.data["status"] == "timed_out"
    assert "may still complete" in result.error


@pytest.mark.parametrize(
    ("status_code", "error_type"),
    [
        (400, "bad_request_error"),
        (401, "authorized_error"),
        (402, "insufficient_balance_error"),
        (422, "unprocessable_entity_error"),
        (429, "rate_limit_error"),
        (500, "server_error"),
        (529, "overloaded_error"),
    ],
)
def test_http_error_envelopes_are_mapped_and_redacted(
    monkeypatch, status_code, error_type
):
    from tools.video.siftq_video import SiftQVideo

    monkeypatch.setenv("SIFTQ_API_KEY", "never-print-this-key")

    def fake_post(*args, **kwargs):
        return _FakeResponse(
            status_code=status_code,
            json_data={
                "type": "error",
                "error": {
                    "type": error_type,
                    "message": "request failed; token never-print-this-key",
                    "http_code": status_code,
                },
                "request_id": "req-123",
            },
        )

    monkeypatch.setattr(requests, "post", fake_post)
    result = SiftQVideo().execute({"prompt": "x"})
    assert not result.success
    assert result.data["http_status"] == status_code
    assert result.data["error_type"] == error_type
    assert result.data["request_id"] == "req-123"
    assert "never-print-this-key" not in result.error
    assert "[redacted]" in result.error


def test_malformed_json_missing_task_id_and_missing_content(monkeypatch, tmp_path):
    from tools.video.siftq_video import SiftQVideo

    monkeypatch.setenv("SIFTQ_API_KEY", "siftq-test-key")
    monkeypatch.setattr(
        requests,
        "post",
        lambda *args, **kwargs: _FakeResponse(
            json_error=ValueError("bad"), status_code=200
        ),
    )
    malformed = SiftQVideo().execute({"prompt": "x"})
    assert not malformed.success
    assert "malformed JSON" in malformed.error

    monkeypatch.setattr(
        requests,
        "post",
        lambda *args, **kwargs: _FakeResponse(json_data={}, status_code=200),
    )
    missing_id = SiftQVideo().execute({"prompt": "x"})
    assert not missing_id.success
    assert "task_id" in missing_id.error

    task = _success_task()
    task["task"]["content"] = None
    _mock_success(monkeypatch, task=task)
    missing_content = SiftQVideo().execute(
        {"prompt": "x", "output_path": str(tmp_path / "never.mp4")}
    )
    assert not missing_content.success
    assert "content.url" in missing_content.error


def test_failed_and_cancelled_tasks_surface_remote_error(monkeypatch):
    from tools.video.siftq_video import SiftQVideo

    monkeypatch.setenv("SIFTQ_API_KEY", "siftq-test-key")
    for status in ("failed", "cancelled"):
        task = _success_task()
        task["task"].update(
            {"status": status, "content": None, "error": {"code": "E7", "message": "nope"}}
        )
        _mock_success(monkeypatch, task=task)
        result = SiftQVideo().execute({"prompt": "x"})
        assert not result.success
        assert status in result.error
        assert "E7: nope" in result.error


def test_download_rejects_empty_or_non_video_response(monkeypatch, tmp_path):
    from tools.video.siftq_video import SiftQVideo

    tool = SiftQVideo()
    monkeypatch.setattr(
        requests,
        "get",
        lambda *args, **kwargs: _FakeResponse(content=b"", headers={}),
    )
    with pytest.raises(RuntimeError, match="empty body"):
        tool._download("https://x/output", tmp_path / "empty.mp4")

    monkeypatch.setattr(
        requests,
        "get",
        lambda *args, **kwargs: _FakeResponse(
            content=b"<html>error</html>", headers={"Content-Type": "text/html"}
        ),
    )
    with pytest.raises(RuntimeError, match="invalid content type"):
        tool._download("https://x/output", tmp_path / "invalid.mp4")


def test_video_selector_uses_siftq_local_reference_without_fal_upload(
    monkeypatch, tmp_path
):
    from tools.video.siftq_video import SiftQVideo
    from tools.video.video_selector import VideoSelector

    monkeypatch.setenv("SIFTQ_API_KEY", "siftq-test-key")
    calls = _mock_success(monkeypatch)
    tool = SiftQVideo()
    monkeypatch.setattr(tool, "_media_url", lambda value, kind: "data:image/png;base64,AAAA")
    selector = VideoSelector()
    monkeypatch.setattr(selector, "_providers", lambda: [tool])
    monkeypatch.setattr(
        selector,
        "_select_best_tool",
        lambda inputs, candidates, context: (tool, None),
    )
    monkeypatch.setattr(
        "tools.video._shared.upload_image_fal",
        lambda path: pytest.fail("SiftQ must not use the fal.ai uploader"),
    )

    result = selector.execute(
        {
            "prompt": "Animate this image",
            "operation": "image_to_video",
            "reference_image_path": "local-reference.png",
            "poll_interval_seconds": 0,
            "output_path": str(tmp_path / "selector.mp4"),
            "preferred_provider": "siftq",
        }
    )
    assert result.success, result.error
    assert calls["payload"]["content"][1]["image_url"]["url"].startswith("data:")
    assert result.data["selected_tool"] == "siftq_video"
    assert result.data["selected_provider"] == "siftq"


def test_video_selector_advertises_first_last_frame_as_motion_required():
    from tools.video.video_selector import VideoSelector

    selector = VideoSelector()
    operations = selector.input_schema["properties"]["operation"]["enum"]
    assert "first_last_frame_to_video" in operations
    assert "first_last_frame_to_video" in selector.capabilities
    assert "first_last_frame_to_video" in selector.MOTION_REQUIRED_OPERATIONS


def test_source_has_no_reference_provider_credentials_or_implementation_imports():
    from pathlib import Path

    source = Path("tools/video/siftq_video.py").read_text(encoding="utf-8")
    forbidden = (
        "MINIMAX_API_KEY",
        "MINIMAX_BASE_URL",
        "api.minimax.io",
        "api.minimaxi.com",
        "from tools.video.minimax_video",
        "import tools.video.minimax_video",
    )
    assert not any(value in source for value in forbidden)
    assert "SIFTQ_API_KEY" in source
    assert "https://siftq.com/api/minimax/" in source
