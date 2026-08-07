"""OpenSpeaker text-to-speech provider tool (api.ai33.pro, v3 unified endpoint).

The v3 TTS endpoint has no `model` field — the prefixed `voice_id` IS the model
selector. Valid prefixes: elevenlabs_, minimax_, clone_, edge_, kokoro_, vbee_,
fishaudio_. Discover IDs via GET /v3/voices (they come back pre-prefixed).
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

VALID_VOICE_PREFIXES = (
    "elevenlabs_",
    "minimax_",
    "clone_",
    "edge_",
    "kokoro_",
    "vbee_",
    "fishaudio_",
)


class OpenSpeakerTTS(BaseTool):
    name = "openspeaker_tts"
    version = "0.1.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "openspeaker"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.ASYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.API

    dependencies = ["requests"]
    install_instructions = (
        "Set the OPENSPEAKER_API_KEY environment variable in .env:\n"
        "  OPENSPEAKER_API_KEY=your_key_here\n"
        "Optionally set OPENSPEAKER_TTS_VOICE_ID to a default prefixed voice id\n"
        "(e.g. elevenlabs_cjVigY5qzO86Huf0OWal). List voices with\n"
        "  GET https://api.ai33.pro/v3/voices?provider=elevenlabs\n"
        "See docs/openspeaker-api.md"
    )
    fallback = "piper_tts"
    fallback_tools = ["piper_tts", "elevenlabs_tts"]
    agent_skills = ["text-to-speech", "elevenlabs"]

    capabilities = [
        "text_to_speech",
        "voice_selection",
        "multi_provider_voices",
        "pronunciation_dictionary",
    ]
    supports = {
        "voice_cloning": True,
        "multilingual": True,
        "offline": False,
        "native_audio": True,
        "word_timestamps": True,
    }
    best_for = [
        "narration with ElevenLabs/Minimax/Edge/Fish Audio voices through one key",
        "multilingual narration including Vietnamese and Arabic-market English",
        "projects that also need cloned voices or a pronunciation dictionary",
    ]
    not_good_for = [
        "fully offline production",
        "sub-second latency streaming",
    ]

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string", "description": "Text to speak (max 1,000,000 chars)."},
            "voice_id": {
                "type": "string",
                "description": (
                    "Prefixed voice id from GET /v3/voices, e.g. "
                    "elevenlabs_cjVigY5qzO86Huf0OWal. Defaults to "
                    "OPENSPEAKER_TTS_VOICE_ID."
                ),
            },
            "voice": {
                "type": "string",
                "description": "Alias for voice_id, for selector compatibility.",
            },
            "speed": {
                "type": "number",
                "minimum": 0.5,
                "maximum": 1.5,
                "default": 1.0,
                "description": "Speaking rate. API default is 1.",
            },
            "with_transcript": {
                "type": "boolean",
                "default": False,
                "description": "Request word-level timing data alongside the audio.",
            },
            "pronunciation_dictionary_id": {
                "type": "string",
                "description": "Optional dictionary id from POST /v3/dictionaries.",
            },
            "output_path": {"type": "string"},
            "timeout_seconds": {"type": "integer", "default": 900},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=100, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=3, retryable_errors=["rate_limit", "timeout", "server_busy"])
    idempotency_key_fields = ["text", "voice_id", "speed", "pronunciation_dictionary_id"]
    side_effects = ["writes audio file to output_path", "calls OpenSpeaker API", "consumes credits"]
    user_visible_verification = [
        "Listen to generated audio for intelligibility, pace, and pronunciation of brand names",
    ]

    def get_status(self) -> ToolStatus:
        if not api_key():
            return ToolStatus.UNAVAILABLE
        # A key without a usable default voice still works when the caller
        # passes voice_id explicitly, so this is DEGRADED rather than a hard no.
        default_voice = (os.environ.get("OPENSPEAKER_TTS_VOICE_ID") or "").strip()
        if default_voice and not default_voice.startswith(VALID_VOICE_PREFIXES):
            return ToolStatus.DEGRADED
        return ToolStatus.AVAILABLE

    def get_info(self) -> dict[str, Any]:
        info = super().get_info() if hasattr(super(), "get_info") else {}
        default_voice = (os.environ.get("OPENSPEAKER_TTS_VOICE_ID") or "").strip()
        info.update(
            {
                "default_voice_id": default_voice or None,
                "valid_voice_prefixes": list(VALID_VOICE_PREFIXES),
                "voice_discovery": "GET /v3/voices?provider=<provider>",
            }
        )
        if default_voice and not default_voice.startswith(VALID_VOICE_PREFIXES):
            info["warning"] = (
                f"OPENSPEAKER_TTS_VOICE_ID={default_voice!r} has no provider prefix. "
                "The v3 API requires one of "
                f"{', '.join(VALID_VOICE_PREFIXES)}. Pass voice_id explicitly or fix .env."
            )
        return info

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        # Billed in account credits, not USD. Cost is reported from the task
        # payload after execution; this is a conservative placeholder.
        return 0.0

    def _resolve_voice_id(self, inputs: dict[str, Any]) -> str:
        voice_id = (
            inputs.get("voice_id")
            or inputs.get("voice")
            or os.environ.get("OPENSPEAKER_TTS_VOICE_ID")
            or ""
        ).strip()
        if not voice_id:
            raise OpenSpeakerError(
                "No voice_id given and OPENSPEAKER_TTS_VOICE_ID is unset. "
                "List voices with GET /v3/voices?provider=elevenlabs"
            )
        if not voice_id.startswith(VALID_VOICE_PREFIXES):
            raise OpenSpeakerError(
                f"voice_id {voice_id!r} is missing a provider prefix. The v3 API "
                f"requires one of: {', '.join(VALID_VOICE_PREFIXES)}. "
                "Note that names like 'eleven_multilingual_v2' are ElevenLabs MODEL "
                "ids, not voice ids — use GET /v3/voices to get a real one."
            )
        return voice_id

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        try:
            result = self._generate(inputs)
        except OpenSpeakerError as exc:
            return ToolResult(success=False, error=f"OpenSpeaker TTS failed: {exc}")
        except Exception as exc:  # noqa: BLE001 - surfaced to the agent as a tool error
            return ToolResult(success=False, error=f"OpenSpeaker TTS failed: {exc}")
        result.duration_seconds = round(time.time() - start, 2)
        return result

    def _generate(self, inputs: dict[str, Any]) -> ToolResult:
        from tools.analysis.audio_probe import probe_duration

        text = inputs["text"]
        voice_id = self._resolve_voice_id(inputs)
        speed = inputs.get("speed")
        if speed is None:
            env_speed = (os.environ.get("OPENSPEAKER_TTS_SPEED") or "").strip()
            speed = float(env_speed) if env_speed else 1.0

        form: dict[str, Any] = {
            "text": text,
            "voice_id": voice_id,
            "speed": str(speed),
            "with_transcript": "true" if inputs.get("with_transcript") else "false",
        }
        dictionary_id = inputs.get("pronunciation_dictionary_id") or os.environ.get(
            "OPENSPEAKER_PRONUNCIATION_DICTIONARY_ID"
        )
        if dictionary_id:
            form["pronunciation_dictionary_id"] = dictionary_id

        created = request("POST", "/v3/text-to-speech", data=form, timeout=60)
        task_id = created.get("task_id")
        if not task_id:
            raise OpenSpeakerError(f"No task_id in create response: {created}")

        task = poll_task(task_id, timeout_seconds=int(inputs.get("timeout_seconds", 900)))
        metadata = task.get("metadata") or {}
        audio_url = metadata.get("audio_url")
        if not audio_url:
            raise OpenSpeakerError(f"Task {task_id} finished without an audio_url: {metadata}")

        output_path = Path(inputs.get("output_path") or f"openspeaker_tts_{task_id}.mp3")
        download(audio_url, output_path)
        audio_duration = probe_duration(output_path)

        return ToolResult(
            success=True,
            data={
                "provider": self.provider,
                "voice_id": voice_id,
                "speed": speed,
                "task_id": task_id,
                "credit_cost": task.get("credit_cost"),
                "text_length": len(text),
                "audio_duration_seconds": round(audio_duration, 2) if audio_duration else None,
                "transcript": metadata.get("transcript") or metadata.get("transcript_url"),
                "output": str(output_path),
            },
            artifacts=[str(output_path)],
            model=voice_id,
        )
