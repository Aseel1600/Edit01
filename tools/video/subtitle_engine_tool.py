"""Subtitle Engine Tool for OpenMontage.

High-performance subtitle processing, word-level alignment, karaoke animation (.ass),
transcript resolution preserving Vietnamese diacritics, and Remotion caption export.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import time
from typing import Any, Optional

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
from lib.subtitles.processor import SubtitleProcessor
from lib.subtitles.domain import RenderScene


class SubtitleEngineTool(BaseTool):
    name = "subtitle_engine"
    version = "1.0.0"
    tier = ToolTier.CORE
    capability = "subtitles"
    provider = "openmontage_subtitles"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["cmd:ffmpeg"]
    install_instructions = "Ensure ffmpeg is installed and on PATH."
    agent_skills = ["speech-to-text"]

    capabilities = [
        "word_alignment",
        "ass_karaoke_generation",
        "caption_segmentation",
        "vietnamese_transcript_preservation",
        "remotion_captions_export",
        "subtitle_burn_in",
    ]
    supports = {
        "word_timestamps": True,
        "karaoke_animation": True,
        "multi_speaker": True,
        "emoji_enhancement": True,
    }
    best_for = [
        "word-by-word active highlighting (TikTok / Reels / Shorts style)",
        "perfect alignment preserving 100% Vietnamese diacritics and casing",
        "generating .ass karaoke subtitles and Remotion caption props",
    ]
    not_good_for = [
        "plain non-timed text files",
    ]

    input_schema = {
        "type": "object",
        "required": ["audio_path"],
        "properties": {
            "audio_path": {
                "type": "string",
                "description": "Path to the narration audio or video file",
            },
            "transcript": {
                "type": "string",
                "description": "Original text transcript for diacritic-preserving alignment",
            },
            "preset": {
                "type": "string",
                "default": "viral-bold-yellow",
                "description": "Subtitle style preset (e.g. viral-bold-yellow, storytelling-serif, 2d-stick-figure-cartoon)",
            },
            "canvas_width": {
                "type": "integer",
                "default": 1920,
                "description": "Canvas width in pixels (e.g. 1920 for landscape, 1080 for portrait)",
            },
            "canvas_height": {
                "type": "integer",
                "default": 1080,
                "description": "Canvas height in pixels (e.g. 1080 for landscape, 1920 for portrait)",
            },
            "language": {
                "type": "string",
                "default": "vi",
                "description": "Language code (default: vi)",
            },
            "output_ass_path": {
                "type": "string",
                "description": "Optional output path for the rendered .ass subtitle file",
            },
            "enable_emoji": {
                "type": "boolean",
                "default": False,
                "description": "Enable automatic emotion/keyword emoji decoration",
            },
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=2, ram_mb=1024, vram_mb=0, disk_mb=100, network_required=False
    )
    retry_policy = RetryPolicy(max_retries=1, retryable_errors=[])
    idempotency_key_fields = ["audio_path", "transcript", "preset", "canvas_width", "canvas_height"]
    side_effects = ["writes .ass subtitle file"]
    user_visible_verification = ["Inspect generated ASS subtitle file or preview subtitles on video"]

    def get_status(self) -> ToolStatus:
        return ToolStatus.AVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        t0 = time.time()
        audio_path_str = inputs.get("audio_path")
        if not audio_path_str:
            return ToolResult(
                success=False,
                error="Parameter 'audio_path' is required.",
                duration_seconds=time.time() - t0,
            )

        audio_path = pathlib.Path(audio_path_str)
        if not audio_path.exists():
            return ToolResult(
                success=False,
                error=f"Audio file not found: {audio_path}",
                duration_seconds=time.time() - t0,
            )

        transcript = inputs.get("transcript")
        preset = inputs.get("preset", "viral-bold-yellow")
        canvas_width = int(inputs.get("canvas_width", 1920))
        canvas_height = int(inputs.get("canvas_height", 1080))
        fps = int(inputs.get("fps", 30))
        language = inputs.get("language", "vi")
        enable_emoji = inputs.get("enable_emoji", False)

        try:
            processor = SubtitleProcessor(preset_path_or_id=preset, enable_emoji=enable_emoji)
            scene: RenderScene = processor.build_render_scene(
                audio_or_video_path=audio_path,
                transcript=transcript,
                canvas_width=canvas_width,
                canvas_height=canvas_height,
                fps=fps,
                language=language,
            )

            # 1. Output ASS file
            output_ass_path_str = inputs.get("output_ass_path")
            if output_ass_path_str:
                ass_path = pathlib.Path(output_ass_path_str)
            else:
                ass_path = audio_path.parent / f"{audio_path.stem}.ass"

            processor.ass_renderer.render_to_file(scene, ass_path)

            # 2. Export Remotion compatible captions list
            remotion_captions = []
            for cap in scene.captions:
                for idx, w in enumerate(cap.words):
                    remotion_captions.append({
                        "word": w.text,
                        "startMs": int(w.start * 1000),
                        "endMs": int(w.end * 1000),
                        "pageBreakAfter": (idx == len(cap.words) - 1),
                    })

            return ToolResult(
                success=True,
                data={
                    "ass_path": str(ass_path),
                    "caption_count": len(scene.captions),
                    "word_count": len(remotion_captions),
                    "preset": preset,
                    "remotion_captions": remotion_captions,
                },
                artifacts=[str(ass_path)],
                cost_usd=0.0,
                duration_seconds=time.time() - t0,
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Subtitle generation failed: {e}",
                duration_seconds=time.time() - t0,
            )
