"""SiftQ H3 video at $0.015-$0.025/sec, about 81% below official list."""

from __future__ import annotations

import base64
import binascii
import io
import json
import mimetypes
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlsplit, urlunsplit

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)

DEFAULT_BASE_URL = "https://siftq.com/api/minimax/"
DEFAULT_MODEL = "MiniMax-H3"
PRICING_URL = "https://siftq.com/#pricing"
# SiftQ publishes these production-friendly H3 rates as about 81% below the
# MiniMax official $0.080/sec (768P) and $0.130/sec (2K) list prices. They are
# the lowest H3 rates currently documented by OpenMontage; keep estimates tied
# to constants.
PRICE_PER_SECOND_USD = {"768P": 0.015, "2K": 0.025}
REFERENCE_IMAGE_PRICE_USD = 0.008
INCLUDED_REFERENCE_IMAGES = 5
OPERATIONS = (
    "text_to_video",
    "image_to_video",
    "first_last_frame_to_video",
    "reference_to_video",
)
RESOLUTIONS = ("768P", "2K")
RATIOS = ("adaptive", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16")
IN_PROGRESS_STATUSES = {"queued", "running"}
FAILURE_STATUSES = {"failed", "cancelled"}


class SiftQAPIError(RuntimeError):
    """A redacted error returned by the SiftQ API."""

    def __init__(
        self,
        *,
        status_code: int,
        error_type: str,
        message: str,
        request_id: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.error_type = error_type
        self.request_id = request_id
        detail = f"SiftQ API {status_code} {error_type}: {message}"
        if request_id:
            detail += f" (request_id: {request_id})"
        super().__init__(detail)


class SiftQVideo(BaseTool):
    """Generate H3 video through SiftQ's highly competitive 81%-off route."""

    name = "siftq_video"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "video_generation"
    provider = "siftq"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.API

    dependencies = ["env:SIFTQ_API_KEY"]
    install_instructions = (
        "Set SIFTQ_API_KEY to your SiftQ API key. SiftQ H3 costs $0.015/sec "
        "at 768P and $0.025/sec at 2K (about 81% below MiniMax official list "
        f"pricing); get access at {PRICING_URL}. Optionally set SIFTQ_BASE_URL "
        "for a documented private endpoint."
    )
    agent_skills = ["siftq-video", "ai-video-gen"]

    capabilities = list(OPERATIONS)
    supports = {
        "text_to_video": True,
        "image_to_video": True,
        "first_last_frame_to_video": True,
        "reference_to_video": True,
        "reference_image": True,
        "reference_video": True,
        "reference_audio": True,
        "camera_direction": True,
    }
    best_for = [
        (
            "OpenMontage's lowest-priced documented H3 route: $0.015/sec at "
            "768P and $0.025/sec at 2K"
        ),
        "highly competitive H3 pricing about 81% below MiniMax official list rates",
        "4-15 second text, image, first/last-frame, or reference-driven clips",
        "mixed image, video, and audio references",
    ]
    not_good_for = ["offline generation", "clips longer than 15 seconds"]
    fallback_tools = ["minimax_video", "minimax_fal_video", "runway_video"]

    input_schema = {
        "type": "object",
        "required": ["prompt"],
        "properties": {
            "prompt": {"type": "string", "minLength": 1, "maxLength": 7000},
            "operation": {
                "type": "string",
                "enum": list(OPERATIONS),
                "default": "text_to_video",
            },
            "model": {
                "type": "string",
                "enum": [DEFAULT_MODEL],
                "default": DEFAULT_MODEL,
            },
            "duration": {
                "type": "integer",
                "minimum": 4,
                "maximum": 15,
                "default": 5,
            },
            "resolution": {
                "type": "string",
                "enum": list(RESOLUTIONS),
                "default": "2K",
                "description": "SiftQ rate: 768P $0.015/sec; 2K $0.025/sec.",
            },
            "ratio": {"type": "string", "enum": list(RATIOS)},
            "aspect_ratio": {
                "type": "string",
                "enum": list(RATIOS),
                "description": "Selector-compatible alias for ratio.",
            },
            "first_frame_image": {"type": "string"},
            "last_frame_image": {"type": "string"},
            "end_image_url": {"type": "string"},
            "last_image_url": {"type": "string"},
            "last_image_path": {"type": "string"},
            "reference_image_url": {"type": "string"},
            "reference_image_path": {"type": "string"},
            "reference_image_urls": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 9,
            },
            "reference_image_paths": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 9,
            },
            "reference_video_url": {"type": "string"},
            "reference_video_path": {"type": "string"},
            "reference_video_urls": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 3,
            },
            "reference_video_paths": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 3,
            },
            "reference_audio_urls": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 3,
            },
            "reference_audio_url": {"type": "string"},
            "reference_audio_path": {"type": "string"},
            "reference_audio_paths": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 3,
            },
            "reference_video_duration_seconds": {
                "type": "number",
                "minimum": 0,
                "maximum": 15,
                "description": (
                    "Optional total reference-video seconds for a more accurate "
                    "preflight cost estimate."
                ),
            },
            "poll_interval_seconds": {
                "type": "number",
                "minimum": 0,
                "maximum": 60,
                "default": 5,
            },
            "timeout_seconds": {
                "type": "number",
                "exclusiveMinimum": 0,
                "maximum": 3600,
                "default": 900,
            },
            "output_path": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=512, vram_mb=0, disk_mb=500, network_required=True
    )
    retry_policy = RetryPolicy(
        max_retries=2,
        backoff_seconds=1.0,
        retryable_errors=["rate_limit", "timeout", "overloaded"],
    )
    idempotency_key_fields = [
        "prompt",
        "operation",
        "model",
        "duration",
        "resolution",
        "ratio",
        "aspect_ratio",
        "first_frame_image",
        "last_frame_image",
        "reference_image_url",
        "reference_image_path",
        "reference_image_urls",
        "reference_image_paths",
        "reference_video_url",
        "reference_video_path",
        "reference_video_urls",
        "reference_video_paths",
        "reference_audio_url",
        "reference_audio_path",
        "reference_audio_urls",
        "reference_audio_paths",
    ]
    side_effects = ["writes video file to output_path", "calls SiftQ video API"]
    user_visible_verification = [
        "Watch the generated clip for motion coherence and prompt adherence"
    ]

    IMAGE_MIME = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".heic": "image/heic",
        ".heif": "image/heif",
    }
    VIDEO_MIME = {".mp4": "video/mp4", ".mov": "video/quicktime"}
    AUDIO_MIME = {".wav": "audio/wav", ".mp3": "audio/mp3"}
    MEDIA_LIMITS = {
        "image": 30 * 1024 * 1024,
        "video": 50 * 1024 * 1024,
        "audio": 15 * 1024 * 1024,
    }
    MAX_REQUEST_BYTES = 64 * 1024 * 1024

    def _get_api_key(self) -> str | None:
        return os.environ.get("SIFTQ_API_KEY")

    def _base_url(self) -> str:
        value = os.environ.get("SIFTQ_BASE_URL", DEFAULT_BASE_URL).strip()
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("SIFTQ_BASE_URL must be an absolute HTTP(S) URL")
        return value

    def _endpoint(self, suffix: str) -> str:
        return f"{self._base_url().rstrip('/')}/{suffix.lstrip('/')}"

    @staticmethod
    def _headers(api_key: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def get_status(self) -> ToolStatus:
        return ToolStatus.AVAILABLE if self._get_api_key() else ToolStatus.UNAVAILABLE

    @staticmethod
    def _normalized_duration(value: Any) -> int:
        if isinstance(value, str) and value.isdigit():
            value = int(value)
        if isinstance(value, bool) or not isinstance(value, int) or not 4 <= value <= 15:
            raise ValueError("SiftQ duration must be an integer from 4 to 15 seconds")
        return value

    @staticmethod
    def _non_negative_number(value: Any, label: str) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            raise ValueError(f"{label} must be a non-negative number")
        return float(value)

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        try:
            duration = self._normalized_duration(inputs.get("duration", 5))
        except ValueError:
            duration = 5
        resolution = inputs.get("resolution", "2K")
        rate = PRICE_PER_SECOND_USD.get(
            str(resolution), PRICE_PER_SECOND_USD["2K"]
        )
        references = self._collect_values(
            inputs, "reference_image_url", "reference_image_urls"
        ) + self._collect_values(
            inputs, "reference_image_path", "reference_image_paths"
        )
        image_cost = (
            max(0, len(references) - INCLUDED_REFERENCE_IMAGES)
            * REFERENCE_IMAGE_PRICE_USD
        )
        input_seconds = inputs.get("reference_video_duration_seconds", 0)
        try:
            input_seconds = self._non_negative_number(
                input_seconds, "reference_video_duration_seconds"
            )
        except ValueError:
            input_seconds = 0
        return round(((duration + input_seconds) * rate) + image_cost, 4)

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        return 90.0

    @staticmethod
    def _collect_values(inputs: dict[str, Any], singular: str, plural: str) -> list[str]:
        values: list[str] = []
        singular_value = inputs.get(singular)
        if singular_value:
            values.append(str(singular_value))
        plural_value = inputs.get(plural)
        if plural_value is None:
            return values
        if not isinstance(plural_value, (list, tuple)):
            raise ValueError(f"{plural} must be an array")
        values.extend(str(value) for value in plural_value if value)
        return values

    @staticmethod
    def _media_item(kind: str, url: str, role: str) -> dict[str, Any]:
        field = f"{kind}_url"
        return {"type": field, field: {"url": url}, "role": role}

    @staticmethod
    def _is_remote_or_asset(value: str) -> bool:
        parsed = urlsplit(value)
        is_http = parsed.scheme in {"http", "https"} and bool(parsed.netloc)
        is_asset = value.startswith("mm_file://") and len(value) > len("mm_file://")
        return is_http or is_asset

    def _media_url(self, value: Any, kind: str) -> str:
        raw = str(value)
        if raw.startswith("data:"):
            self._validate_data_uri(raw, kind)
            return raw
        if self._is_remote_or_asset(raw):
            return raw
        path = Path(raw).expanduser()
        if not path.is_file():
            raise ValueError(
                f"{kind} reference must be a public URL, mm_file:// ID, "
                f"Data URI, or existing local file: {raw}"
            )
        limit = self.MEDIA_LIMITS[kind]
        if path.stat().st_size > limit:
            raise ValueError(
                f"local {kind} must be at most {limit // (1024 * 1024)} MB"
            )
        mime_map = self._mime_map(kind)
        mime = mime_map.get(path.suffix.lower())
        if not mime:
            guessed, _ = mimetypes.guess_type(path.name)
            mime = guessed if guessed in set(mime_map.values()) else None
        if not mime:
            expected = ", ".join(sorted(mime_map))
            raise ValueError(f"unsupported local {kind} format; expected {expected}")
        if kind == "image":
            self._validate_image(path.read_bytes(), str(path))
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:{mime.lower()};base64,{encoded}"

    def _mime_map(self, kind: str) -> dict[str, str]:
        return {
            "image": self.IMAGE_MIME,
            "video": self.VIDEO_MIME,
            "audio": self.AUDIO_MIME,
        }[kind]

    def _validate_data_uri(self, value: str, kind: str) -> None:
        match = re.fullmatch(
            r"data:([a-z]+/[a-z0-9.+-]+);base64,([A-Za-z0-9+/=]+)", value
        )
        if not match:
            raise ValueError(
                f"{kind} Data URI must use a lowercase supported MIME type and strict base64"
            )
        mime = match.group(1)
        if mime not in set(self._mime_map(kind).values()):
            raise ValueError(f"unsupported {kind} Data URI MIME type: {mime}")
        try:
            decoded = base64.b64decode(match.group(2), validate=True)
        except (ValueError, binascii.Error) as exc:
            raise ValueError(f"invalid base64 in {kind} Data URI") from exc
        if len(decoded) > self.MEDIA_LIMITS[kind]:
            limit_mb = self.MEDIA_LIMITS[kind] // (1024 * 1024)
            raise ValueError(f"decoded {kind} Data URI must be at most {limit_mb} MB")
        if kind == "image":
            self._validate_image(decoded, "Data URI")

    @staticmethod
    def _validate_image(data: bytes, source: str) -> None:
        try:
            from PIL import Image

            with Image.open(io.BytesIO(data)) as image:
                width, height = image.size
                image.verify()
        except Exception as exc:
            raise ValueError(f"image is unreadable or corrupt: {source}") from exc
        if not (256 <= width <= 5760 and 256 <= height <= 5760):
            raise ValueError("image width and height must each be 256 to 5760 pixels")
        if not 0.4 <= width / height <= 2.5:
            raise ValueError("image width/height ratio must be between 0.4 and 2.5")

    @staticmethod
    def _validate_local_timed_media(path: Path, kind: str) -> float:
        ffprobe = shutil.which("ffprobe")
        if not ffprobe:
            raise ValueError(f"ffprobe is required to validate local reference {kind}")
        entries = "format=duration"
        if kind == "video":
            entries += ":stream=codec_type,codec_name,width,height,r_frame_rate"
        try:
            proc = subprocess.run(
                [
                    ffprobe,
                    "-v",
                    "error",
                    "-show_entries",
                    entries,
                    "-of",
                    "json",
                    str(path),
                ],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
            probe = json.loads(proc.stdout) if proc.returncode == 0 else {}
            duration = float((probe.get("format") or {}).get("duration", 0))
        except (OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
            raise ValueError(f"failed to probe local reference {kind}: {path}") from exc
        if not 2 <= duration <= 15:
            raise ValueError(f"each local reference {kind} must be 2 to 15 seconds")
        if kind != "video":
            return duration
        video_stream = next(
            (
                stream
                for stream in probe.get("streams", [])
                if stream.get("codec_type") == "video"
                and stream.get("width")
                and stream.get("height")
            ),
            None,
        )
        if not video_stream:
            raise ValueError(f"local reference video has no readable video stream: {path}")
        codec = str(video_stream.get("codec_name", "")).lower()
        if codec not in {"h264", "hevc"}:
            raise ValueError("local reference video codec must be H.264 or H.265")
        unsupported_audio = {
            str(stream.get("codec_name", "")).lower()
            for stream in probe.get("streams", [])
            if stream.get("codec_type") == "audio"
            and str(stream.get("codec_name", "")).lower() not in {"aac", "mp3"}
        }
        if unsupported_audio:
            raise ValueError("local reference video audio codec must be AAC or MP3")
        width = int(video_stream["width"])
        height = int(video_stream["height"])
        if not (256 <= width <= 5760 and 256 <= height <= 5760):
            raise ValueError("video width and height must each be 256 to 5760 pixels")
        if not 0.4 <= width / height <= 2.5:
            raise ValueError("video width/height ratio must be between 0.4 and 2.5")
        numerator, _, denominator = str(video_stream.get("r_frame_rate", "0/1")).partition("/")
        fps = float(numerator) / float(denominator or 1)
        if not 23.976 <= fps <= 60:
            raise ValueError("local reference video frame rate must be 23.976 to 60 fps")
        return duration

    def _known_media_duration(self, value: Any, kind: str) -> float | None:
        raw = str(value)
        if self._is_remote_or_asset(raw):
            return None
        if raw.startswith("data:"):
            self._validate_data_uri(raw, kind)
            match = re.fullmatch(
                r"data:([a-z]+/[a-z0-9.+-]+);base64,([A-Za-z0-9+/=]+)",
                raw,
            )
            if not match:
                return None
            decoded = base64.b64decode(match.group(2), validate=True)
            suffix = ".mp4" if kind == "video" else ".wav"
            if match.group(1) == "video/quicktime":
                suffix = ".mov"
            elif match.group(1) == "audio/mp3":
                suffix = ".mp3"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
                handle.write(decoded)
                temp_path = Path(handle.name)
            try:
                return self._validate_local_timed_media(temp_path, kind)
            finally:
                temp_path.unlink(missing_ok=True)
        path = Path(raw).expanduser()
        if path.is_file():
            return self._validate_local_timed_media(path, kind)
        return None

    def _validate_total_reference_duration(
        self, values: list[str], kind: str
    ) -> None:
        durations = [
            duration
            for value in values
            if (duration := self._known_media_duration(value, kind)) is not None
        ]
        if sum(durations) > 15:
            raise ValueError(f"total local reference {kind} duration must not exceed 15 seconds")

    def _build_payload(self, inputs: dict[str, Any]) -> dict[str, Any]:
        prompt = inputs.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("SiftQ requires a non-empty 'prompt'")
        if len(prompt) > 7000:
            raise ValueError("SiftQ prompt must not exceed 7000 characters")

        model = inputs.get("model", DEFAULT_MODEL)
        if model != DEFAULT_MODEL:
            raise ValueError(f"SiftQ does not support model '{model}'")
        operation = inputs.get("operation", "text_to_video")
        if operation not in OPERATIONS:
            raise ValueError(f"SiftQ does not support operation '{operation}'")
        resolution = inputs.get("resolution", "2K")
        if resolution not in RESOLUTIONS:
            raise ValueError("SiftQ resolution must be '768P' or '2K'")
        duration = self._normalized_duration(inputs.get("duration", 5))

        content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        if operation in {"image_to_video", "first_last_frame_to_video"}:
            first = (
                inputs.get("first_frame_image")
                or inputs.get("reference_image_url")
                or inputs.get("reference_image_path")
                or inputs.get("image_url")
                or inputs.get("image_path")
            )
            if not first:
                raise ValueError(f"{operation} requires a first-frame image")
            content.append(
                self._media_item(
                    "image", self._media_url(first, "image"), "first_frame"
                )
            )
            last = (
                inputs.get("last_frame_image")
                or inputs.get("end_image_url")
                or inputs.get("last_image_url")
                or inputs.get("last_image_path")
            )
            if operation == "first_last_frame_to_video" and not last:
                raise ValueError("first_last_frame_to_video requires a last-frame image")
            if last:
                content.append(
                    self._media_item(
                        "image", self._media_url(last, "image"), "last_frame"
                    )
                )
        elif operation == "reference_to_video":
            images = self._collect_values(
                inputs, "reference_image_url", "reference_image_urls"
            ) + self._collect_values(
                inputs, "reference_image_path", "reference_image_paths"
            )
            videos = self._collect_values(
                inputs, "reference_video_url", "reference_video_urls"
            ) + self._collect_values(
                inputs, "reference_video_path", "reference_video_paths"
            )
            audios = self._collect_values(
                inputs, "reference_audio_url", "reference_audio_urls"
            ) + self._collect_values(
                inputs, "reference_audio_path", "reference_audio_paths"
            )
            if not images and not videos and not audios:
                raise ValueError("reference_to_video requires at least one reference")
            if len(images) > 9:
                raise ValueError("reference_to_video accepts at most 9 reference images")
            if len(videos) > 3:
                raise ValueError("reference_to_video accepts at most 3 reference videos")
            if len(audios) > 3:
                raise ValueError("reference_to_video accepts at most 3 reference audio clips")
            if audios and not (images or videos):
                raise ValueError("reference audio requires at least one reference image or video")
            self._validate_total_reference_duration(videos, "video")
            self._validate_total_reference_duration(audios, "audio")
            content.extend(
                self._media_item("image", self._media_url(value, "image"), "reference_image")
                for value in images
            )
            content.extend(
                self._media_item("video", self._media_url(value, "video"), "reference_video")
                for value in videos
            )
            content.extend(
                self._media_item("audio", self._media_url(value, "audio"), "reference_audio")
                for value in audios
            )

        ratio = inputs.get("ratio") or inputs.get("aspect_ratio")
        if operation in {"image_to_video", "first_last_frame_to_video"}:
            ratio = "adaptive"
        elif not ratio:
            ratio = "16:9" if operation == "text_to_video" else "adaptive"
        if ratio not in RATIOS:
            raise ValueError(f"unsupported SiftQ ratio '{ratio}'")
        if operation == "text_to_video" and ratio == "adaptive":
            raise ValueError("SiftQ text_to_video requires a concrete ratio")

        payload = {
            "model": DEFAULT_MODEL,
            "content": content,
            "resolution": resolution,
            "duration": duration,
            "ratio": ratio,
        }
        encoded_size = len(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
        if encoded_size > self.MAX_REQUEST_BYTES:
            raise ValueError("SiftQ request body must be at most 64 MB")
        return payload

    @staticmethod
    def _json_object(response: Any, context: str) -> dict[str, Any]:
        try:
            payload = response.json()
        except Exception as exc:
            raise RuntimeError(f"SiftQ returned malformed JSON for {context}") from exc
        if not isinstance(payload, dict):
            raise RuntimeError(f"SiftQ returned a non-object response for {context}")
        return payload

    def _raise_for_status(self, response: Any) -> None:
        status_code = int(getattr(response, "status_code", 0) or 0)
        if 200 <= status_code < 300:
            return
        error_type = "http_error"
        message = "request failed"
        request_id: str | None = None
        try:
            payload = response.json()
            if isinstance(payload, dict):
                request_id = str(payload.get("request_id")) if payload.get("request_id") else None
                error = payload.get("error")
                if isinstance(error, dict):
                    error_type = str(error.get("type") or error_type)
                    message = str(error.get("message") or message)
        except Exception:
            pass
        raise SiftQAPIError(
            status_code=status_code,
            error_type=error_type,
            message=message,
            request_id=request_id,
        )

    def _create_task(self, payload: dict[str, Any], api_key: str) -> str:
        import requests

        response = requests.post(
            self._endpoint("v2/video_generation"),
            headers=self._headers(api_key),
            json=payload,
            timeout=30,
        )
        self._raise_for_status(response)
        task_id = self._json_object(response, "task creation").get("task_id")
        if not isinstance(task_id, (str, int)) or not str(task_id).strip():
            raise RuntimeError("SiftQ did not return a task_id")
        return str(task_id)

    def _query_task(self, task_id: str, api_key: str) -> dict[str, Any]:
        import requests

        response = None
        endpoint = self._endpoint(
            f"v2/query/video_generation/{quote(task_id, safe='')}"
        )
        for attempt in range(self.retry_policy.max_retries + 1):
            try:
                response = requests.get(
                    endpoint,
                    headers=self._headers(api_key),
                    timeout=30,
                )
                retryable_status = response.status_code in {429, 500, 529}
                if retryable_status and attempt < self.retry_policy.max_retries:
                    time.sleep(self.retry_policy.backoff_seconds * (2**attempt))
                    continue
                break
            except requests.RequestException:
                if attempt >= self.retry_policy.max_retries:
                    raise
                time.sleep(self.retry_policy.backoff_seconds * (2**attempt))
        if response is None:
            raise RuntimeError("SiftQ task query returned no response")
        self._raise_for_status(response)
        payload = self._json_object(response, "task query")
        task = payload.get("task")
        if not isinstance(task, dict):
            raise RuntimeError("SiftQ task query did not return a task object")
        return task

    def _poll_task(
        self, task_id: str, api_key: str, *, interval: float, timeout: float
    ) -> dict[str, Any]:
        if not 0 <= interval <= 60:
            raise ValueError("poll_interval_seconds must be between 0 and 60")
        if timeout <= 0:
            raise ValueError("timeout_seconds must be greater than 0")
        deadline = time.monotonic() + timeout
        while True:
            task = self._query_task(task_id, api_key)
            status = str(task.get("status", "")).lower()
            if status == "succeeded" or status in FAILURE_STATUSES:
                return task
            if status not in IN_PROGRESS_STATUSES:
                raise RuntimeError(f"SiftQ returned unknown task status: {status or '<empty>'}")
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"SiftQ task {task_id} did not finish within {timeout:g}s; "
                    "the remote task may still complete"
                )
            time.sleep(min(interval, max(deadline - time.monotonic(), 0)))

    def _download(self, video_url: str, output_path: Path) -> None:
        import requests

        response = requests.get(video_url, timeout=120)
        self._raise_for_status(response)
        content = getattr(response, "content", b"")
        headers = getattr(response, "headers", {}) or {}
        content_type = str(headers.get("Content-Type", "")).split(";", 1)[0].lower()
        recognizable = len(content) >= 12 and content[4:8] == b"ftyp"
        if not content:
            raise RuntimeError("SiftQ video download returned an empty body")
        if not recognizable and not content_type.startswith("video/"):
            raise RuntimeError("SiftQ video download returned an invalid content type")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        partial = output_path.with_name(output_path.name + ".part")
        partial.write_bytes(content)
        partial.replace(output_path)

    def _cost_from_task(self, task: dict[str, Any], inputs: dict[str, Any]) -> float:
        resolution = str(task.get("resolution") or inputs.get("resolution", "2K"))
        rate = PRICE_PER_SECOND_USD.get(resolution, PRICE_PER_SECOND_USD["2K"])
        usage = task.get("usage") or {}
        output_seconds = usage.get("output_seconds")
        input_seconds = usage.get("input_seconds")
        image_count = usage.get("input_image_count")
        if not isinstance(output_seconds, (int, float)) or output_seconds < 0:
            return self.estimate_cost(inputs)
        if not isinstance(input_seconds, (int, float)) or input_seconds < 0:
            input_seconds = 0
        if not isinstance(image_count, int) or isinstance(image_count, bool) or image_count < 0:
            image_count = 0
        return round(
            ((float(output_seconds) + float(input_seconds)) * rate)
            + max(0, image_count - INCLUDED_REFERENCE_IMAGES)
            * REFERENCE_IMAGE_PRICE_USD,
            4,
        )

    @staticmethod
    def _task_error(task: dict[str, Any]) -> str:
        error = task.get("error")
        if isinstance(error, dict):
            parts = [str(error[key]) for key in ("code", "message") if error.get(key)]
            return ": ".join(parts)
        return str(error or "remote generation failed")

    @staticmethod
    def _safe_error(exc: Exception, api_key: str | None) -> str:
        message = str(exc)
        if api_key:
            message = message.replace(api_key, "[redacted]")
        message = re.sub(
            r"data:(?:image|video|audio)/[^;\s]+;base64,[A-Za-z0-9+/=]+",
            "[redacted data URI]",
            message,
        )

        def redact_url(match: re.Match[str]) -> str:
            parsed = urlsplit(match.group(0))
            return urlunsplit(
                (
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    "[redacted]" if parsed.query else "",
                    "",
                )
            )

        return re.sub(r"https?://[^\s'\"<>]+", redact_url, message)

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        api_key = self._get_api_key()
        if not api_key:
            return ToolResult(
                success=False,
                error="SIFTQ_API_KEY not set. " + self.install_instructions,
            )

        started = time.time()
        task_id: str | None = None
        model = str(inputs.get("model", DEFAULT_MODEL))
        try:
            payload = self._build_payload(inputs)
            task_id = self._create_task(payload, api_key)
            task = self._poll_task(
                task_id,
                api_key,
                interval=float(inputs.get("poll_interval_seconds", 5)),
                timeout=float(inputs.get("timeout_seconds", 900)),
            )
            status = str(task.get("status", "")).lower()
            if status in FAILURE_STATUSES:
                raise RuntimeError(f"SiftQ task {status}: {self._task_error(task)}")
            content = task.get("content")
            video_url = content.get("url") if isinstance(content, dict) else None
            if not isinstance(video_url, str) or not video_url:
                raise RuntimeError("SiftQ succeeded task did not return content.url")
            output_path = Path(inputs.get("output_path") or "siftq_output.mp4")
            self._download(video_url, output_path)
            return ToolResult(
                success=True,
                data={
                    "provider": self.provider,
                    "model": DEFAULT_MODEL,
                    "operation": inputs.get("operation", "text_to_video"),
                    "output": str(output_path),
                    "output_path": str(output_path),
                    "task_id": task_id,
                    "status": status,
                    "resolution": task.get("resolution") or payload["resolution"],
                    "duration": task.get("duration") or payload["duration"],
                    "ratio": task.get("ratio") or payload["ratio"],
                    "usage": task.get("usage") or {},
                },
                artifacts=[str(output_path)],
                cost_usd=self._cost_from_task(task, inputs),
                duration_seconds=round(time.time() - started, 2),
                model=DEFAULT_MODEL,
            )
        except Exception as exc:  # noqa: BLE001 - provider boundary returns ToolResult
            data: dict[str, Any] = {"provider": self.provider, "model": model}
            if task_id:
                data["task_id"] = task_id
            if isinstance(exc, TimeoutError):
                data["status"] = "timed_out"
            if isinstance(exc, SiftQAPIError):
                data.update(
                    {
                        "http_status": exc.status_code,
                        "error_type": exc.error_type,
                        "request_id": exc.request_id,
                    }
                )
            return ToolResult(
                success=False,
                error=self._safe_error(exc, api_key),
                data=data,
                duration_seconds=round(time.time() - started, 2),
                model=model,
            )
