"""YouTube Data API uploader (optional google-api-python-client)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)

TOKEN_PATH = Path(".youtube-token.json")
DEFAULT_PRIVACY = "unlisted"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def _secrets_path() -> Path | None:
    raw = os.environ.get("YOUTUBE_CLIENT_SECRETS_FILE") or os.environ.get(
        "GOOGLE_CLIENT_SECRETS"
    )
    if raw:
        return Path(raw).expanduser()
    for candidate in (
        Path("client_secrets.json"),
        Path.home() / ".config/openmontage/youtube-client-secrets.json",
    ):
        if candidate.is_file():
            return candidate
    return None


class YouTubeUpload(BaseTool):
    name = "youtube_upload"
    version = "1.0.0"
    tier = ToolTier.PUBLISH
    capability = "publish"
    provider = "youtube"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.API

    dependencies = []
    install_instructions = (
        "Create a Google Cloud OAuth desktop client with YouTube Data API v3.\n"
        "Set YOUTUBE_CLIENT_SECRETS_FILE to the client JSON.\n"
        "Optional: pip install google-api-python-client google-auth-oauthlib google-auth-httplib2\n"
        "First run opens a browser; the token is stored in .youtube-token.json (gitignored)."
    )
    agent_skills = ["creative/hermes-hostinger"]

    capabilities = ["youtube_upload", "status"]
    supports = {"uploads": True, "resumable": True, "free": True}
    best_for = ["uploading an OpenMontage render to the user's channel"]
    not_good_for = ["unattended upload without OAuth client secrets"]

    input_schema = {
        "type": "object",
        "required": ["action"],
        "properties": {
            "action": {"type": "string", "enum": ["status", "upload"]},
            "video_path": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "tags": {"type": "array", "items": {"type": "string"}},
            "privacy": {"type": "string", "enum": ["public", "private", "unlisted"]},
            "dry_run": {"type": "boolean"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=0, network_required=True
    )
    side_effects = ["uploads a video to YouTube when action=upload and dry_run is false"]
    user_visible_verification = [
        "Studio > Content shows the new unlisted video",
    ]

    def get_status(self) -> ToolStatus:
        if _secrets_path() and _secrets_path().is_file():
            return ToolStatus.AVAILABLE
        return ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        started = time.monotonic()
        action = (inputs.get("action") or "status").strip().lower()
        secrets = _secrets_path()
        configured = bool(secrets and secrets.is_file())
        privacy = inputs.get("privacy") or os.environ.get("YOUTUBE_PRIVACY") or DEFAULT_PRIVACY

        if action == "status":
            return ToolResult(
                success=True,
                data={
                    "configured": configured,
                    "secrets_path": str(secrets) if secrets else None,
                    "token_path": str(TOKEN_PATH),
                    "token_present": TOKEN_PATH.is_file(),
                    "privacy_default": privacy,
                    "library": self._library_ok(),
                },
                duration_seconds=time.monotonic() - started,
            )

        if action != "upload":
            return ToolResult(success=False, error=f"Unknown action: {action}")

        video_path = Path(inputs.get("video_path") or "").expanduser()
        title = inputs.get("title")
        if not video_path.is_file():
            return ToolResult(success=False, error=f"Video not found: {video_path}")
        if not title:
            return ToolResult(success=False, error="title is required")

        timestamp = datetime.now(timezone.utc).isoformat()
        entry = {
            "platform": "youtube",
            "status": "draft",
            "timestamp": timestamp,
            "visibility": privacy,
            "metadata_used": {
                "title": title,
                "description": inputs.get("description") or "",
                "hashtags": inputs.get("tags") or [],
            },
        }

        if inputs.get("dry_run"):
            entry["status"] = "exported"
            entry["error"] = "dry_run"
            return ToolResult(
                success=True,
                data={"publish_log": {"version": "1.0", "entries": [entry]}, "dry_run": True},
                duration_seconds=time.monotonic() - started,
            )

        if not configured:
            entry["status"] = "failed"
            entry["error"] = "YOUTUBE_CLIENT_SECRETS_FILE missing"
            return ToolResult(
                success=False,
                error=entry["error"],
                data={"publish_log": {"version": "1.0", "entries": [entry]}},
            )

        if not self._library_ok():
            entry["status"] = "failed"
            entry["error"] = (
                "Install google-api-python-client google-auth-oauthlib google-auth-httplib2"
            )
            return ToolResult(
                success=False,
                error=entry["error"],
                data={"publish_log": {"version": "1.0", "entries": [entry]}},
            )

        try:
            video_id, url = self._upload(
                video_path,
                title=title,
                description=inputs.get("description") or "",
                tags=list(inputs.get("tags") or []),
                privacy=privacy,
                secrets_file=secrets,
            )
        except Exception as exc:  # noqa: BLE001
            entry["status"] = "failed"
            entry["error"] = str(exc)
            return ToolResult(
                success=False,
                error=str(exc),
                data={"publish_log": {"version": "1.0", "entries": [entry]}},
                duration_seconds=time.monotonic() - started,
            )

        entry["status"] = "published"
        entry["video_id"] = video_id
        entry["url"] = url
        return ToolResult(
            success=True,
            data={"publish_log": {"version": "1.0", "entries": [entry]}, "video_id": video_id, "url": url},
            duration_seconds=time.monotonic() - started,
        )

    @staticmethod
    def _library_ok() -> bool:
        try:
            import googleapiclient.discovery  # noqa: F401
            import google_auth_oauthlib.flow  # noqa: F401
            return True
        except ImportError:
            return False

    def _upload(
        self,
        video_path: Path,
        *,
        title: str,
        description: str,
        tags: list[str],
        privacy: str,
        secrets_file: Path,
    ) -> tuple[str, str]:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        creds = None
        if TOKEN_PATH.is_file():
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        if creds is None or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(str(secrets_file), SCOPES)
                creds = flow.run_local_server(port=0)
            TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")

        youtube = build("youtube", "v3", credentials=creds)
        body = {
            "snippet": {"title": title, "description": description, "tags": tags, "categoryId": "22"},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
        }
        media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            _, response = request.next_chunk()
        video_id = response["id"]
        return video_id, f"https://youtu.be/{video_id}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Upload a video to YouTube (unlisted by default).")
    parser.add_argument("--file", dest="video_path", help="Path to mp4")
    parser.add_argument("--title", default="")
    parser.add_argument("--description", default="")
    parser.add_argument("--privacy", default=DEFAULT_PRIVACY, choices=["public", "private", "unlisted"])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args(argv)
    tool = YouTubeUpload()
    if args.status or not args.video_path:
        result = tool.execute({"action": "status"})
    else:
        result = tool.execute(
            {
                "action": "upload",
                "video_path": args.video_path,
                "title": args.title or Path(args.video_path).stem,
                "description": args.description,
                "privacy": args.privacy,
                "dry_run": args.dry_run,
            }
        )
    print(json.dumps({"success": result.success, "error": result.error, "data": result.data}, indent=2))
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
