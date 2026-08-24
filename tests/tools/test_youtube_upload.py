"""Tests for youtube_upload (offline / dry-run paths)."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from schemas.artifacts import validate_artifact
from tools.publishers.youtube_upload import YouTubeUpload
from tools.tool_registry import ToolRegistry


def test_registry_discovers_youtube_upload():
    registry = ToolRegistry()
    registry.discover("tools")
    assert registry.get("youtube_upload") is not None


def test_status_does_not_require_secrets():
    result = YouTubeUpload().execute({"action": "status"})
    assert result.success is True
    assert "configured" in result.data


def test_missing_file_fails():
    result = YouTubeUpload().execute(
        {"action": "upload", "video_path": "/no/such.mp4", "title": "x"}
    )
    assert result.success is False


def test_dry_run_publish_log(tmp_path):
    video = tmp_path / "clip.mp4"
    video.write_bytes(b"fake")
    result = YouTubeUpload().execute(
        {
            "action": "upload",
            "video_path": str(video),
            "title": "Dry run clip",
            "privacy": "unlisted",
            "dry_run": True,
        }
    )
    assert result.success is True
    validate_artifact("publish_log", result.data["publish_log"])
    assert result.data["publish_log"]["entries"][0]["visibility"] == "unlisted"
