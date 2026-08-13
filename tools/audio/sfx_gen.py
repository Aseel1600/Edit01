"""Sound-effect generation tool via ElevenLabs Sound Generation API.

Generates short one-shot SFX (whooshes, pops, impacts, UI sounds) for video
production. Distinct from music_gen: uses the /v1/sound-generation endpoint,
which is optimized for effects rather than musical compositions.
Reports unavailable when no API key is configured.
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


class SfxGen(BaseTool):
    name = "sfx_gen"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "music_generation"
    provider = "elevenlabs"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.API

    dependencies = []  # checked dynamically via API key
    install_instructions = (
        "Set the ELEVENLABS_API_KEY environment variable:\n"
        "  export ELEVENLABS_API_KEY=your_key_here\n"
        "Get a key at https://elevenlabs.io"
    )

    agent_skills = ["sound-effects", "elevenlabs"]

    capabilities = [
        "generate_sfx",
    ]

    input_schema = {
        "type": "object",
        "required": ["prompt"],
        "properties": {
            "prompt": {
                "type": "string",
                "description": (
                    "Sound effect description (e.g. 'short soft whoosh, "
                    "smooth air movement, no tail'). Be concrete about "
                    "texture, length, and decay."
                ),
            },
            "duration_seconds": {
                "type": "number",
                "minimum": 0.5,
                "maximum": 22,
                "description": (
                    "Target duration in seconds (API supports 0.5-22s). "
                    "Keep one-shot UI/transition cues under 2s."
                ),
            },
            "prompt_influence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": (
                    "How literally to follow the prompt (0-1, API default 0.3). "
                    "Higher = more literal, lower = more creative."
                ),
            },
            "output_path": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=10, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=2, retryable_errors=["rate_limit", "timeout"])
    idempotency_key_fields = ["prompt", "duration_seconds", "prompt_influence"]
    side_effects = ["writes audio file to output_path", "calls ElevenLabs API"]
    user_visible_verification = [
        "Listen to generated SFX for texture and decay",
    ]

    def get_status(self) -> ToolStatus:
        if os.environ.get("ELEVENLABS_API_KEY"):
            return ToolStatus.AVAILABLE
        return ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        # ElevenLabs sound generation: ~80 credits/generation, roughly $0.01-0.02
        return 0.02

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            return ToolResult(
                success=False,
                error="No ElevenLabs API key. " + self.install_instructions,
            )

        start = time.time()

        try:
            result = self._generate(inputs, api_key)
        except Exception as e:
            return ToolResult(success=False, error=f"SFX generation failed: {e}")

        result.duration_seconds = round(time.time() - start, 2)
        result.cost_usd = self.estimate_cost(inputs)
        return result

    def _generate(self, inputs: dict[str, Any], api_key: str) -> ToolResult:
        import requests

        prompt = inputs["prompt"]

        url = "https://api.elevenlabs.io/v1/sound-generation"

        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json",
        }

        payload: dict[str, Any] = {"text": prompt}
        if inputs.get("duration_seconds") is not None:
            payload["duration_seconds"] = inputs["duration_seconds"]
        if inputs.get("prompt_influence") is not None:
            payload["prompt_influence"] = inputs["prompt_influence"]

        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()

        output_path = Path(inputs.get("output_path", "sfx_output.mp3"))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(response.content)

        return ToolResult(
            success=True,
            data={
                "provider": "elevenlabs",
                "prompt": prompt,
                "output": str(output_path),
                "format": "mp3",
            },
            artifacts=[str(output_path)],
        )
