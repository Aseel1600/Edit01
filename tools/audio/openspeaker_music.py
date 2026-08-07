"""OpenSpeaker music generation tool (Suno via api.ai33.pro).

Two creation modes:
  simple  — one short description drives the whole song (`gpt_description_prompt`)
  custom  — explicit title + lyrics + style tags, with optional vocal gender

Suno returns multiple clips per task; the first is written to `output_path` and
the rest alongside it so the agent can pick the best take.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

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
from tools.openspeaker_client import OpenSpeakerError, api_key, download, poll_task, request


class OpenSpeakerMusic(BaseTool):
    name = "openspeaker_music"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "music_generation"
    provider = "openspeaker"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.ASYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.API

    dependencies = ["requests"]
    install_instructions = (
        "Set the OPENSPEAKER_API_KEY environment variable in .env:\n"
        "  OPENSPEAKER_API_KEY=your_key_here\n"
        "Music routes through Suno on POST /v1s/task/music-generation.\n"
        "See docs/openspeaker-api.md"
    )
    fallback = None
    fallback_tools = ["music_gen", "music_library"]
    agent_skills = ["music"]

    capabilities = ["music_generation", "instrumental_generation", "lyric_song_generation"]
    supports = {
        "instrumental": True,
        "lyrics": True,
        "style_tags": True,
        "vocal_gender": True,
        "offline": False,
    }
    best_for = [
        "background beds for ads and explainers",
        "instrumental scoring matched to a specific mood and tempo",
        "full songs with lyrics when the brief calls for one",
    ]
    not_good_for = [
        "exact-length beds (Suno picks its own duration; trim in post)",
        "licensed/cleared music where provenance must be contractual",
        "offline generation",
    ]

    input_schema = {
        "type": "object",
        "required": ["prompt"],
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Simple mode: song description (1-500 chars).",
            },
            "create_mode": {
                "type": "string",
                "enum": ["simple", "custom"],
                "default": "simple",
            },
            "instrumental": {
                "type": "boolean",
                "default": True,
                "description": "Simple mode only. Background beds should almost always be instrumental.",
            },
            "title": {"type": "string", "description": "Custom mode. Max 80 chars."},
            "lyrics": {"type": "string", "description": "Custom mode. Max 5000 chars."},
            "tags": {"type": "string", "description": "Custom mode style tags. Max 1000 chars."},
            "vocal_gender": {"type": "string", "enum": ["f", "m"]},
            "output_path": {"type": "string"},
            "timeout_seconds": {"type": "integer", "default": 900},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=200, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=3, retryable_errors=["rate_limit", "timeout", "server_busy"])
    idempotency_key_fields = ["prompt", "create_mode", "tags", "lyrics", "instrumental"]
    side_effects = ["writes audio file(s) to output_path", "calls OpenSpeaker API", "consumes credits"]
    user_visible_verification = [
        "Listen to each returned take and confirm mood, tempo, and that it sits under narration without competing",
    ]

    def get_status(self) -> ToolStatus:
        if not api_key():
            return ToolStatus.UNAVAILABLE
        enabled = (os.environ.get("OPENSPEAKER_MUSIC_ENABLED") or "").strip().lower()
        if enabled in ("false", "0", "no"):
            return ToolStatus.UNAVAILABLE
        return ToolStatus.AVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        # Billed in credits; the real figure comes back on the task payload.
        return 0.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        try:
            result = self._generate(inputs)
        except OpenSpeakerError as exc:
            return ToolResult(success=False, error=f"OpenSpeaker music generation failed: {exc}")
        except Exception as exc:  # noqa: BLE001 - surfaced to the agent as a tool error
            return ToolResult(success=False, error=f"OpenSpeaker music generation failed: {exc}")
        result.duration_seconds = round(time.time() - start, 2)
        return result

    def _generate(self, inputs: dict[str, Any]) -> ToolResult:
        mode = inputs.get("create_mode", "simple")
        body: dict[str, Any] = {"create_mode": mode}

        if mode == "custom":
            if not (inputs.get("lyrics") or inputs.get("tags")):
                raise OpenSpeakerError("custom mode requires `lyrics` or `tags`.")
            body["title"] = (inputs.get("title") or "")[:80]
            body["lyrics"] = (inputs.get("lyrics") or "")[:5000]
            body["tags"] = (inputs.get("tags") or inputs.get("prompt") or "")[:1000]
            if inputs.get("vocal_gender"):
                body["vocal_gender"] = inputs["vocal_gender"]
        else:
            prompt = (inputs.get("prompt") or "").strip()
            if not prompt:
                raise OpenSpeakerError("simple mode requires `prompt`.")
            if len(prompt) > 500:
                raise OpenSpeakerError(
                    f"gpt_description_prompt is limited to 500 chars (got {len(prompt)})."
                )
            body["gpt_description_prompt"] = prompt
            body["make_instrumental"] = bool(inputs.get("instrumental", True))

        created = request("POST", "/v1s/task/music-generation", json_body=body, timeout=60)
        task_id = created.get("task_id")
        if not task_id:
            raise OpenSpeakerError(f"No task_id in create response: {created}")

        task = poll_task(task_id, timeout_seconds=int(inputs.get("timeout_seconds", 900)))
        metadata = task.get("metadata") or {}
        urls = self._extract_audio_urls(metadata)
        if not urls:
            raise OpenSpeakerError(f"Task {task_id} finished without audio urls: {list(metadata)}")

        output_path = Path(inputs.get("output_path") or f"openspeaker_music_{task_id}.mp3")
        written: list[str] = []
        for index, url in enumerate(urls):
            target = (
                output_path
                if index == 0
                else output_path.with_name(f"{output_path.stem}_take{index + 1}{output_path.suffix}")
            )
            download(url, target)
            written.append(str(target))

        clips = ((metadata.get("suno_result") or {}).get("clips")) or []
        durations = [c.get("duration") for c in clips if isinstance(c, dict)]

        return ToolResult(
            success=True,
            data={
                "provider": self.provider,
                "engine": "suno",
                "create_mode": mode,
                "task_id": task_id,
                "credit_cost": task.get("credit_cost"),
                "model_version": metadata.get("major_model_version"),
                "title": metadata.get("title"),
                "tags": metadata.get("tags") or body.get("tags"),
                "takes": len(written),
                "durations_seconds": durations,
                "output": written[0],
                "outputs": written,
            },
            artifacts=written,
            model=f"suno:{metadata.get('major_model_version') or 'unknown'}",
        )

    @staticmethod
    def _extract_audio_urls(metadata: dict[str, Any]) -> list[str]:
        """Collect final (non-stream) audio urls, preserving order and de-duping."""
        candidates: list[str] = []

        primary = metadata.get("audio_url")
        if isinstance(primary, str):
            candidates.append(primary)

        for url in metadata.get("all_audio_urls") or []:
            if isinstance(url, str):
                candidates.append(url)

        for clip in ((metadata.get("suno_result") or {}).get("clips")) or []:
            if isinstance(clip, dict) and isinstance(clip.get("audio_url"), str):
                candidates.append(clip["audio_url"])

        seen: set[str] = set()
        ordered: list[str] = []
        for url in candidates:
            if url and url not in seen:
                seen.add(url)
                ordered.append(url)
        return ordered
