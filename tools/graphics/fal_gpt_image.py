"""GPT Image 2 via fal.ai (https://fal.run/openai/gpt-image-2).

Used in this project because the OpenSpeaker Imagen queue stalls under load.
fal.run is a synchronous endpoint — it returns the finished images on the same
request, so there is no task to poll and no queue to get stuck behind.

Cost is driven by the `quality` parameter (fal defaults to `high`). This tool
defaults to `low` deliberately: the caller asked for low quality at ~1K, which
is roughly an order of magnitude cheaper per image than the fal default.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

import requests

from tools.openspeaker_client import safe_media_path
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

ENDPOINT = "https://fal.run/openai/gpt-image-2"

# fal constrains concrete sizes: both dimensions multiples of 16, max edge 3840,
# aspect ratio <= 3:1, and total pixels between 655,360 and 8,294,400.
# 1024x576 (a naive "1K 16:9") is only 589,824 px and is REJECTED — 1280x720 is
# the smallest compliant 16:9 size, so that is what "1K landscape" maps to here.
SIZE_PRESETS: dict[str, dict[str, int]] = {
    "16:9": {"width": 1280, "height": 720},
    "9:16": {"width": 720, "height": 1280},
    "1:1": {"width": 1024, "height": 1024},
    "4:3": {"width": 1024, "height": 768},
    "3:4": {"width": 768, "height": 1024},
}

MIN_PIXELS = 655_360
MAX_PIXELS = 8_294_400
MAX_EDGE = 3840

# A single generated still that exceeds this is a bug, not a big image.
MAX_IMAGE_BYTES = 128 * 1024 * 1024


class FalGPTImage(BaseTool):
    name = "fal_gpt_image"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "image_generation"
    provider = "fal"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.API

    dependencies = ["requests"]
    install_instructions = (
        "Set FAL_KEY to your fal.ai API key.\n"
        "  FAL_KEY=your_key_here\n"
        "Get one at https://fal.ai/dashboard/keys"
    )
    fallback = "openspeaker_image"
    fallback_tools = ["openspeaker_image", "flux_image"]
    agent_skills = ["flux-best-practices", "visual-style"]

    capabilities = ["text_to_image", "typography_rendering"]
    supports = {
        "reference_images": False,
        "aspect_ratio_control": True,
        "resolution_control": True,
        "offline": False,
        "batch": True,
        "synchronous": True,
    }
    best_for = [
        "fast synchronous image generation with no task queue to stall behind",
        "images containing fine typography and legible on-image text",
        "cheap iteration at quality=low",
    ]
    not_good_for = [
        "reference-image conditioning (use openspeaker_image or flux_image)",
        "deterministic reruns",
    ]

    input_schema = {
        "type": "object",
        "required": ["prompt"],
        "properties": {
            "prompt": {"type": "string"},
            "aspect_ratio": {
                "type": "string",
                "description": "Preset key: 16:9, 9:16, 1:1, 4:3, 3:4. Mapped to a fal-compliant size.",
            },
            "width": {"type": "integer", "description": "Explicit width. Must be a multiple of 16."},
            "height": {"type": "integer", "description": "Explicit height. Must be a multiple of 16."},
            "quality": {
                "type": "string",
                "enum": ["auto", "low", "medium", "high"],
                "default": "low",
                "description": "fal defaults to 'high'; this tool defaults to 'low' for cost.",
            },
            "num_images": {"type": "integer", "default": 1, "minimum": 1, "maximum": 4},
            "output_format": {
                "type": "string",
                "enum": ["jpeg", "png", "webp"],
                "default": "png",
            },
            "output_path": {"type": "string"},
            "timeout_seconds": {"type": "integer", "default": 300},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=200, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=2, retryable_errors=["rate_limit", "timeout"])
    idempotency_key_fields = ["prompt", "width", "height", "quality"]
    side_effects = ["writes image file(s) to output_path", "calls fal.ai API", "incurs USD cost"]
    user_visible_verification = [
        "Open the image and check composition, on-image text spelling, and that no invented branding appears",
    ]

    @staticmethod
    def _api_key() -> Optional[str]:
        return os.environ.get("FAL_KEY") or os.environ.get("FAL_AI_API_KEY")

    def get_status(self) -> ToolStatus:
        return ToolStatus.AVAILABLE if self._api_key() else ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        # fal bills image output tokens; quality dominates. These are rough
        # per-image figures for ~1MP output, used for budget reporting only.
        per_image = {"low": 0.011, "medium": 0.042, "high": 0.167, "auto": 0.042}
        quality = inputs.get("quality", "low")
        return round(per_image.get(quality, 0.042) * int(inputs.get("num_images", 1)), 4)

    def _resolve_size(self, inputs: dict[str, Any]) -> tuple[dict[str, int], list[str]]:
        """Return a fal-compliant {width, height} plus any adjustment notes."""
        notes: list[str] = []
        width, height = inputs.get("width"), inputs.get("height")

        if not (width and height):
            aspect = (inputs.get("aspect_ratio") or "16:9").strip()
            preset = SIZE_PRESETS.get(aspect)
            if preset is None:
                notes.append(f"aspect_ratio {aspect!r} unknown; used 16:9")
                preset = SIZE_PRESETS["16:9"]
            width, height = preset["width"], preset["height"]

        # Snap to multiples of 16 rather than letting fal reject the request.
        snapped_w, snapped_h = (max(16, round(v / 16) * 16) for v in (width, height))
        if (snapped_w, snapped_h) != (width, height):
            notes.append(f"size {width}x{height} snapped to {snapped_w}x{snapped_h} (multiples of 16)")
        width, height = snapped_w, snapped_h

        if max(width, height) > MAX_EDGE:
            notes.append(f"edge exceeded {MAX_EDGE}px; falling back to 16:9 preset")
            width, height = SIZE_PRESETS["16:9"].values()

        pixels = width * height
        if not (MIN_PIXELS <= pixels <= MAX_PIXELS):
            preset = SIZE_PRESETS["16:9"]
            notes.append(
                f"{width}x{height} is {pixels:,}px, outside fal's "
                f"{MIN_PIXELS:,}-{MAX_PIXELS:,} range; used "
                f"{preset['width']}x{preset['height']}"
            )
            width, height = preset["width"], preset["height"]

        return {"width": width, "height": height}, notes

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        api_key = self._api_key()
        if not api_key:
            return ToolResult(success=False, error="No fal.ai API key. " + self.install_instructions)

        start = time.time()
        try:
            result = self._generate(inputs, api_key)
        except Exception as exc:  # noqa: BLE001 - surfaced to the agent as a tool error
            return ToolResult(success=False, error=f"fal GPT Image 2 failed: {exc}")
        result.duration_seconds = round(time.time() - start, 2)
        result.cost_usd = self.estimate_cost(inputs)
        return result

    def _generate(self, inputs: dict[str, Any], api_key: str) -> ToolResult:
        image_size, size_notes = self._resolve_size(inputs)
        quality = inputs.get("quality", "low")
        num_images = int(inputs.get("num_images", 1))
        output_format = inputs.get("output_format", "png")

        payload = {
            "prompt": inputs["prompt"],
            "image_size": image_size,
            "quality": quality,
            "num_images": num_images,
            "output_format": output_format,
        }

        # Transient DNS/connection failures to fal.run were observed in practice,
        # so a bare single attempt is not good enough for a batch of scenes.
        timeout = int(inputs.get("timeout_seconds", 300))
        attempts = self.retry_policy.max_retries + 1
        response = None
        for attempt in range(attempts):
            try:
                response = requests.post(
                    ENDPOINT,
                    headers={
                        "Authorization": f"Key {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=timeout,
                )
                break
            except requests.RequestException as exc:
                if attempt >= attempts - 1:
                    raise RuntimeError(f"network error after {attempts} attempts: {exc}") from exc
                time.sleep(2 ** attempt)

        if response.status_code == 429 or response.status_code >= 500:
            raise RuntimeError(
                f"HTTP {response.status_code} (retryable): {response.text[:300]}"
            )
        if response.status_code >= 400:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text[:400]}")

        data = response.json()
        images = data.get("images") or []
        if not images:
            raise RuntimeError(f"No images in response: {str(data)[:300]}")

        suffix = f".{output_format}"
        output_path = safe_media_path(inputs.get("output_path") or f"fal_gpt_image{suffix}")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        written: list[str] = []
        for index, image in enumerate(images):
            url = image.get("url")
            if not url:
                continue
            target = (
                output_path
                if index == 0
                else output_path.with_name(f"{output_path.stem}_{index + 1}{output_path.suffix}")
            )
            # The URL is chosen by the API, not the caller: https only, and the
            # write is capped so a malformed response cannot fill the disk.
            if urlparse(url).scheme != "https":
                raise RuntimeError(f"refusing to download image over non-https url: {url[:40]}…")
            written_bytes = 0
            with requests.get(url, stream=True, timeout=180) as stream:
                stream.raise_for_status()
                with open(target, "wb") as handle:
                    for chunk in stream.iter_content(chunk_size=1 << 16):
                        if not chunk:
                            continue
                        written_bytes += len(chunk)
                        if written_bytes > MAX_IMAGE_BYTES:
                            handle.close()
                            target.unlink(missing_ok=True)
                            raise RuntimeError(
                                f"image download exceeded {MAX_IMAGE_BYTES} bytes, aborted"
                            )
                        handle.write(chunk)
            written.append(str(target))

        if not written:
            raise RuntimeError("Response contained images but none had a url")

        return ToolResult(
            success=True,
            data={
                "provider": self.provider,
                "model_id": "openai/gpt-image-2",
                "image_size": image_size,
                "quality": quality,
                "parameter_adjustments": size_notes,
                "dimensions": [
                    {"width": i.get("width"), "height": i.get("height")} for i in images
                ],
                "generations": len(written),
                "prompt": inputs["prompt"],
                "output": written[0],
                "outputs": written,
            },
            artifacts=written,
            model="openai/gpt-image-2",
        )
