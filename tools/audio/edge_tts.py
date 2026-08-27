"""Microsoft Edge neural text-to-speech provider tool.

Zero-key high-quality neural voice synthesis supporting Vietnamese
(vi-VN-HoaiMyNeural, vi-VN-NamMinhNeural) and 100+ multilingual voices.
"""

from __future__ import annotations

import asyncio
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
from tools.audio.vietnamese_text_formatter import format_for_voice


DEFAULT_VOICES = {
    "vi": "vi-VN-HoaiMyNeural",
    "vi-male": "vi-VN-NamMinhNeural",
    "vi-female": "vi-VN-HoaiMyNeural",
    "en": "en-US-JennyNeural",
    "en-male": "en-US-GuyNeural",
    "en-female": "en-US-JennyNeural",
}


class EdgeTTS(BaseTool):
    name = "edge_tts"
    version = "1.0.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "microsoft_edge"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.API

    dependencies = ["python:edge_tts"]
    install_instructions = "Install edge-tts:\n  pip install edge-tts"
    agent_skills = ["text-to-speech"]

    capabilities = [
        "text_to_speech",
        "voice_selection",
        "multilingual",
        "rate_control",
        "pitch_control",
    ]
    supports = {
        "voice_cloning": False,
        "multilingual": True,
        "offline": False,
        "native_audio": True,
        "zero_key": True,
    }
    best_for = [
        "zero-key high quality Vietnamese narration",
        "fast multilingual speech synthesis without paid API keys",
        "natural sounding female and male Vietnamese voices",
    ]
    not_good_for = [
        "custom voice cloning from reference audio (use omnivoice_tts or elevenlabs_tts)",
        "strictly offline setups with zero network access (use piper_tts)",
    ]

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string", "description": "Text to synthesize"},
            "voice": {
                "type": "string",
                "default": "vi-VN-HoaiMyNeural",
                "description": "Voice name (e.g. vi-VN-HoaiMyNeural, vi-VN-NamMinhNeural, en-US-JennyNeural)",
            },
            "language": {
                "type": "string",
                "default": "vi",
                "description": "Language code (e.g. vi, en, ja, fr)",
            },
            "rate": {
                "type": "string",
                "default": "+0%",
                "description": "Speed rate adjustment (e.g. +10%, -5%)",
            },
            "pitch": {
                "type": "string",
                "default": "+0Hz",
                "description": "Pitch adjustment (e.g. +0Hz, +20Hz)",
            },
            "volume": {
                "type": "string",
                "default": "+0%",
                "description": "Volume adjustment",
            },
            "output_path": {
                "type": "string",
                "description": "Path to write the output MP3 audio",
            },
            "format_vietnamese": {
                "type": "boolean",
                "default": True,
                "description": "Whether to apply Vietnamese number/unit normalizer before TTS",
            },
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=50, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=3, retryable_errors=["timeout", "connection"])
    idempotency_key_fields = ["text", "voice", "rate", "pitch", "volume"]
    side_effects = ["writes audio file to output_path"]
    user_visible_verification = ["Play generated audio file to verify voice clarity and pronunciation"]

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        t0 = time.time()
        text = inputs.get("text", "").strip()
        if not text:
            return ToolResult(
                success=False,
                error="Parameter 'text' is required and must not be empty.",
                duration_seconds=time.time() - t0,
            )

        language = inputs.get("language", "vi").lower()
        voice = inputs.get("voice") or inputs.get("voice_id") or DEFAULT_VOICES.get(language, "vi-VN-HoaiMyNeural")
        rate = inputs.get("rate", "+0%")
        pitch = inputs.get("pitch", "+0Hz")
        volume = inputs.get("volume", "+0%")
        format_vietnamese = inputs.get("format_vietnamese", True)

        if format_vietnamese:
            text = format_for_voice(text, language=language)

        output_path_str = inputs.get("output_path")
        if output_path_str:
            out_path = Path(output_path_str)
        else:
            out_path = Path("scratch") / f"edge_tts_{int(time.time() * 1000)}.mp3"

        out_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            import edge_tts

            async def _synthesize():
                communicate = edge_tts.Communicate(
                    text=text,
                    voice=voice,
                    rate=rate,
                    pitch=pitch,
                    volume=volume,
                )
                await communicate.save(str(out_path))

            asyncio.run(_synthesize())

            file_size = out_path.stat().st_size if out_path.exists() else 0
            if file_size == 0:
                return ToolResult(
                    success=False,
                    error="Edge TTS produced empty output file.",
                    duration_seconds=time.time() - t0,
                )

            return ToolResult(
                success=True,
                data={
                    "output_path": str(out_path),
                    "file_size_bytes": file_size,
                    "voice": voice,
                    "language": language,
                    "character_count": len(text),
                    "formatted_text": text,
                },
                artifacts=[str(out_path)],
                cost_usd=0.0,
                duration_seconds=time.time() - t0,
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Edge TTS generation failed: {e}",
                duration_seconds=time.time() - t0,
            )
