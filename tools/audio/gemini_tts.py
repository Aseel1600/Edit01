"""Gemini Text-to-Speech provider tool.

Speech synthesis through the Gemini API (generativelanguage.googleapis.com).

Unlike `google_tts`, which targets Google Cloud Text-to-Speech, this tool works
with a plain AI Studio API key: Cloud TTS rejects API keys outright
("API keys are not supported by this API"), while the Gemini API accepts them.
Reach for this when GOOGLE_API_KEY is all that is configured; prefer
`google_tts` when a service account is available and the wider Cloud voice
catalogue is needed.
"""

from __future__ import annotations

import base64
import os
import struct
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


class GeminiTTS(BaseTool):
    name = "gemini_tts"
    version = "0.1.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "gemini"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.API

    dependencies = []
    install_instructions = (
        "Set GOOGLE_API_KEY (or GEMINI_API_KEY) to an AI Studio API key.\n"
        "  Get one at https://aistudio.google.com/apikey — no Google Cloud project,\n"
        "  billing account or service account needed.\n"
        "  The same key also unlocks google_imagen and gemini_omni_video."
    )
    fallback = "piper_tts"
    fallback_tools = ["google_tts", "openai_tts", "piper_tts"]
    agent_skills = ["text-to-speech"]

    capabilities = ["text_to_speech", "voice_selection", "multilingual"]
    supports = {
        "voice_cloning": False,
        "multilingual": True,
        "offline": False,
        "native_audio": True,
        "ssml": False,
    }
    best_for = [
        "TTS when only an AI Studio API key is configured",
        "quick narration drafts without Google Cloud setup",
        "style direction through plain-language prompts",
    ]
    not_good_for = [
        "SSML markup — the Gemini API has no SSML input",
        "the full 700+ voice Cloud catalogue — use google_tts",
        "fully offline production — use piper_tts",
    ]

    # Prebuilt voice names accepted by the Gemini speech models.
    VOICES = [
        "Zephyr", "Puck", "Charon", "Kore", "Fenrir", "Leda", "Orus", "Aoede",
        "Callirrhoe", "Autonoe", "Enceladus", "Iapetus", "Umbriel", "Algieba",
        "Despina", "Erinome", "Algenib", "Rasalgethi", "Laomedeia", "Achernar",
        "Alnilam", "Schedar", "Gacrux", "Pulcherrima", "Achird", "Zubenelgenubi",
        "Vindemiatrix", "Sadachbia", "Sadaltager", "Sulafat",
    ]

    DEFAULT_MODEL = "gemini-3.1-flash-tts-preview"

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string", "description": "Text to convert to speech"},
            "voice": {
                "type": "string",
                "default": "Kore",
                "enum": VOICES,
                "description": "Prebuilt Gemini voice name.",
            },
            "model": {
                "type": "string",
                "default": DEFAULT_MODEL,
                "description": (
                    "Gemini speech model. The default is resolved against the live "
                    "model list, so a retired preview name falls back automatically."
                ),
            },
            "style": {
                "type": "string",
                "description": (
                    "Optional delivery direction in plain language, e.g. "
                    "'read this slowly and warmly'. Prepended to the text as a prompt."
                ),
            },
            "output_path": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=50, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=2, retryable_errors=["rate_limit", "timeout"])
    idempotency_key_fields = ["text", "voice", "model", "style"]
    side_effects = ["writes a WAV file to output_path", "calls the Gemini API"]
    user_visible_verification = ["Listen to generated audio for natural speech quality"]

    _API_ROOT = "https://generativelanguage.googleapis.com/v1beta"

    # ---- Credentials ----

    @staticmethod
    def _api_key() -> str | None:
        for var in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
            value = os.environ.get(var)
            if value:
                return value
        return None

    def get_status(self) -> ToolStatus:
        return ToolStatus.AVAILABLE if self._api_key() else ToolStatus.UNAVAILABLE

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        return 2.0 + len(inputs.get("text", "")) / 200.0

    # ---- Model resolution ----

    def _resolve_model(self, requested: str, api_key: str) -> str:
        """Return `requested` if the key can see it, else any other speech model.

        Google retires preview model names without notice, and a stale default
        would otherwise surface as a bare 404.
        """
        import requests

        try:
            response = requests.get(
                f"{self._API_ROOT}/models",
                headers={"x-goog-api-key": api_key},
                timeout=30,
            )
            response.raise_for_status()
            names = [m["name"].split("/")[-1] for m in response.json().get("models", [])]
        except Exception:
            return requested

        if requested in names:
            return requested
        speech = [n for n in names if "tts" in n.lower()]
        return speech[0] if speech else requested

    # ---- PCM -> WAV ----

    @staticmethod
    def _pcm_to_wav(pcm: bytes, sample_rate: int, channels: int = 1) -> bytes:
        """Wrap raw little-endian 16-bit PCM in a WAV container.

        The API returns headerless PCM (audio/L16), which most players and
        ffmpeg filters will not open without an explicit format hint.
        """
        bits = 16
        byte_rate = sample_rate * channels * bits // 8
        block_align = channels * bits // 8
        header = b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVEfmt "
        header += struct.pack("<IHHIIHH", 16, 1, channels, sample_rate, byte_rate, block_align, bits)
        header += b"data" + struct.pack("<I", len(pcm))
        return header + pcm

    @staticmethod
    def _sample_rate_from_mime(mime: str, default: int = 24000) -> int:
        for part in mime.split(";"):
            part = part.strip()
            if part.startswith("rate="):
                try:
                    return int(part[5:])
                except ValueError:
                    return default
        return default

    # ---- Execution ----

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        import requests

        api_key = self._api_key()
        if not api_key:
            return ToolResult(
                success=False,
                error="No Gemini API key found. " + self.install_instructions,
            )

        text = inputs["text"]
        voice = inputs.get("voice", "Kore")
        style = inputs.get("style")
        model = self._resolve_model(inputs.get("model", self.DEFAULT_MODEL), api_key)
        prompt = f"{style}: {text}" if style else text

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}
                },
            },
        }

        start = time.time()
        try:
            response = requests.post(
                f"{self._API_ROOT}/models/{model}:generateContent",
                headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
                json=payload,
                timeout=180,
            )
            response.raise_for_status()
            part = response.json()["candidates"][0]["content"]["parts"][0]["inlineData"]
        except Exception as exc:
            safe_error = str(exc).replace(api_key, "[REDACTED]")
            return ToolResult(success=False, error=f"Gemini TTS failed: {safe_error}")

        mime = part.get("mimeType", "audio/L16;rate=24000")
        sample_rate = self._sample_rate_from_mime(mime)
        audio = self._pcm_to_wav(base64.b64decode(part["data"]), sample_rate)

        output_path = Path(inputs.get("output_path", "tts_output.wav"))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(audio)

        return ToolResult(
            success=True,
            data={
                "provider": self.provider,
                "voice": voice,
                "model": model,
                "text_length": len(text),
                "output": str(output_path),
                "format": "WAV",
                "sample_rate": sample_rate,
                "duration_seconds": round(len(audio) / (sample_rate * 2), 2),
            },
            artifacts=[str(output_path)],
            model=f"gemini-tts/{model}/{voice}",
            duration_seconds=round(time.time() - start, 2),
        )
