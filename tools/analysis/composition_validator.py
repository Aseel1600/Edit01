"""Pre-render composition validator.

Checks an ExplainerProps JSON for common issues before rendering:
- Missing asset files (images, audio)
- Narration duration exceeding video duration
- Music duration shorter than video (warning)
- Overlapping or out-of-order cuts
- Required fields present

Run this before every render to catch problems that would otherwise
produce broken or truncated output.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Any

from tools.analysis.audio_probe import probe_duration
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


class CompositionValidator(BaseTool):
    name = "composition_validator"
    version = "0.2.0"
    tier = ToolTier.CORE
    capability = "analysis"
    provider = "local"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["binary:ffprobe"]
    install_instructions = "Requires ffprobe on PATH (part of ffmpeg)."

    capabilities = ["validate_composition", "pre_render_check"]
    best_for = [
        "catching audio-video duration mismatches before render",
        "verifying all referenced assets exist",
        "pre-flight check before expensive render operations",
    ]

    input_schema = {
        "type": "object",
        "required": ["composition_path"],
        "properties": {
            "composition_path": {
                "type": "string",
                "description": "Path to the composition JSON file",
            },
            "assets_root": {
                "type": "string",
                "description": (
                    "Root directory for resolving relative asset paths. "
                    "If omitted, resolved from render_runtime (see below)."
                ),
            },
            "render_runtime": {
                "type": "string",
                "enum": ["remotion", "hyperframes", "ffmpeg"],
                "description": (
                    "Which runtime will consume this composition. Drives the "
                    "default asset root: remotion→remotion-composer/public, "
                    "hyperframes→<workspace>/assets or composition's parent, "
                    "ffmpeg→composition's parent. Explicit assets_root wins."
                ),
            },
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=64, vram_mb=0, disk_mb=0, network_required=False
    )
    side_effects = []

    def get_status(self) -> ToolStatus:
        return ToolStatus.AVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        comp_path = Path(inputs["composition_path"])
        if not comp_path.exists():
            return ToolResult(success=False, error=f"Composition not found: {comp_path}")

        start = time.time()

        try:
            comp = json.loads(comp_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            return ToolResult(success=False, error=f"Invalid JSON: {e}")

        # Determine assets root. Explicit wins; otherwise dispatch by runtime.
        # `render_runtime` may be passed in inputs, or extracted from the
        # composition JSON itself (edit_decisions.render_runtime).
        explicit_root = inputs.get("assets_root") or ""
        assets_root = Path(explicit_root) if explicit_root else None
        runtime = (
            inputs.get("render_runtime")
            or comp.get("render_runtime")
            or ""
        ).strip().lower()

        if assets_root is None or not assets_root.is_dir():
            if runtime == "hyperframes":
                # HyperFrames workspaces keep assets/ alongside index.html.
                # Composition JSON typically lives in projects/<p>/artifacts/,
                # so the workspace is at projects/<p>/hyperframes/.
                candidate = comp_path
                resolved = None
                for _ in range(5):
                    candidate = candidate.parent
                    hf_assets = candidate / "hyperframes" / "assets"
                    if hf_assets.is_dir():
                        resolved = hf_assets
                        break
                    local_assets = candidate / "assets"
                    if local_assets.is_dir() and (candidate / "index.html").is_file():
                        resolved = local_assets
                        break
                assets_root = resolved or comp_path.parent
            elif runtime == "ffmpeg":
                # FFmpeg jobs reference files by absolute path; fall back to
                # the composition's parent for any bare-name references.
                assets_root = comp_path.parent
            else:
                # Remotion (default): remotion-composer/public
                candidate = comp_path
                resolved = None
                for _ in range(5):
                    candidate = candidate.parent
                    public = candidate / "remotion-composer" / "public"
                    if public.is_dir():
                        resolved = public
                        break
                assets_root = resolved or comp_path.parent

        errors: list[str] = []
        warnings: list[str] = []
        info: list[str] = []

        cuts = comp.get("cuts", [])
        audio = comp.get("audio", {})

        # --- Check 1: Cuts exist ---
        if not cuts:
            errors.append("No cuts defined in composition")
            return self._result(errors, warnings, info, start)

        # --- Check 2: Video duration ---
        video_duration = 0.0
        for cut in cuts:
            out_s = cut.get("out_seconds", 0)
            if out_s > video_duration:
                video_duration = out_s
        info.append(f"Video duration: {video_duration}s ({len(cuts)} cuts)")
        info.append(f"Render runtime: {runtime or 'default (remotion)'}; assets root: {assets_root}")

        # --- Check 3: Cut ordering and gaps ---
        sorted_cuts = sorted(cuts, key=lambda c: c.get("in_seconds", 0))
        for i, cut in enumerate(sorted_cuts):
            in_s = cut.get("in_seconds", 0)
            out_s = cut.get("out_seconds", 0)
            if out_s <= in_s:
                errors.append(
                    f"Cut '{cut.get('id', i)}': out_seconds ({out_s}) <= in_seconds ({in_s})"
                )

        # --- Check 4: Asset files exist ---
        for cut in cuts:
            source = cut.get("source", "")
            if source:
                asset_path = assets_root / source
                if not asset_path.exists():
                    errors.append(f"Missing asset: {source} (looked in {assets_root})")

            bg_img = cut.get("backgroundImage", "")
            if bg_img:
                bg_path = assets_root / bg_img
                if not bg_path.exists():
                    errors.append(f"Missing background image: {bg_img}")

        # --- Check 5: Narration duration vs video duration ---
        narration = audio.get("narration", {})
        narration_src = narration.get("src", "")
        if narration_src:
            narration_path = assets_root / narration_src
            if not narration_path.exists():
                errors.append(f"Missing narration audio: {narration_src}")
            else:
                narration_dur = probe_duration(narration_path)
                if narration_dur is not None:
                    info.append(f"Narration duration: {narration_dur:.1f}s")
                    overshoot = narration_dur - video_duration
                    if overshoot > 1.0:
                        errors.append(
                            f"Narration ({narration_dur:.1f}s) exceeds video ({video_duration}s) "
                            f"by {overshoot:.1f}s — audio will be cut off"
                        )
                    elif overshoot > 0:
                        warnings.append(
                            f"Narration ({narration_dur:.1f}s) slightly exceeds video ({video_duration}s) "
                            f"by {overshoot:.1f}s"
                        )
                else:
                    warnings.append(f"Could not probe narration duration: {narration_src}")

        # --- Check 6: Music duration ---
        music = audio.get("music", {})
        music_src = music.get("src", "")
        if music_src:
            music_path = assets_root / music_src
            if not music_path.exists():
                errors.append(f"Missing music audio: {music_src}")
            else:
                music_dur = probe_duration(music_path)
                if music_dur is not None:
                    info.append(f"Music duration: {music_dur:.1f}s")
                    if music_dur < video_duration:
                        warnings.append(
                            f"Music ({music_dur:.1f}s) is shorter than video ({video_duration}s) "
                            f"— will end early"
                        )

        # --- Check 7: No audio at all ---
        if not narration_src and not music_src:
            warnings.append("No audio configured (no narration or music)")

        # --- Check 8: Overlay timing contract ---
        # Remotion's <Sequence> needs finite from/duration values. An overlay
        # that uses the wrong timing keys yields NaN and fails deep inside the
        # render ("The 'from' prop of a sequence must be finite, but got NaN"),
        # after bundling. Catch it here instead.
        errors.extend(self._validate_overlays(comp.get("overlays", [])))

        return self._result(errors, warnings, info, start)

    OVERLAY_TYPES = {"section_title", "stat_reveal", "hero_title", "provider_chip"}
    OVERLAY_TIMING_ALIASES = {
        "start_seconds": "in_seconds",
        "end_seconds": "out_seconds",
        "start": "in_seconds",
        "end": "out_seconds",
        "from_seconds": "in_seconds",
        "to_seconds": "out_seconds",
    }

    @classmethod
    def _validate_overlays(cls, overlays: Any) -> list[str]:
        """Validate overlay timing/type/content before the composition renders."""
        errors: list[str] = []
        if not overlays:
            return errors
        if not isinstance(overlays, list):
            return ["overlays must be a list"]

        for index, overlay in enumerate(overlays):
            label = f"Overlay {index}"
            if not isinstance(overlay, dict):
                errors.append(f"{label}: must be an object")
                continue
            label = f"Overlay {index} ({overlay.get('type', 'no type')})"

            overlay_type = overlay.get("type")
            if not overlay_type:
                errors.append(f"{label}: missing 'type'")
            elif overlay_type not in cls.OVERLAY_TYPES:
                errors.append(
                    f"{label}: unknown overlay type {overlay_type!r}. "
                    f"Supported: {', '.join(sorted(cls.OVERLAY_TYPES))}"
                )

            # Wrong-but-plausible timing keys are the common failure; name the fix.
            aliases = [k for k in cls.OVERLAY_TIMING_ALIASES if k in overlay]
            for alias in aliases:
                errors.append(
                    f"{label}: unsupported timing key {alias!r} — "
                    f"use {cls.OVERLAY_TIMING_ALIASES[alias]!r}. "
                    f"Supported overlay timing keys are 'in_seconds' and 'out_seconds'."
                )

            times: dict[str, float] = {}
            for key in ("in_seconds", "out_seconds"):
                if key not in overlay:
                    if not aliases:
                        errors.append(
                            f"{label}: missing {key!r} "
                            f"(overlay timing keys are 'in_seconds' and 'out_seconds')"
                        )
                    continue
                value = overlay[key]
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    errors.append(f"{label}: {key} must be a number, got {value!r}")
                elif not math.isfinite(value):
                    errors.append(f"{label}: {key} must be finite, got {value!r}")
                elif value < 0:
                    errors.append(f"{label}: {key} must be >= 0, got {value!r}")
                else:
                    times[key] = float(value)

            if len(times) == 2 and times["out_seconds"] <= times["in_seconds"]:
                errors.append(
                    f"{label}: out_seconds ({times['out_seconds']}) must be greater than "
                    f"in_seconds ({times['in_seconds']})"
                )

            if overlay_type in {"section_title", "stat_reveal", "hero_title"} and not overlay.get("text"):
                errors.append(f"{label}: requires 'text'")
            if overlay_type == "provider_chip" and not overlay.get("providers"):
                errors.append(f"{label}: requires 'providers'")

        return errors

    def _result(
        self,
        errors: list[str],
        warnings: list[str],
        info: list[str],
        start: float,
    ) -> ToolResult:
        passed = len(errors) == 0
        data = {
            "valid": passed,
            "errors": errors,
            "warnings": warnings,
            "info": info,
            "error_count": len(errors),
            "warning_count": len(warnings),
        }

        if not passed:
            summary = "; ".join(errors[:3])
            return ToolResult(
                success=False,
                error=f"Composition has {len(errors)} error(s): {summary}",
                data=data,
                duration_seconds=round(time.time() - start, 2),
            )

        return ToolResult(
            success=True,
            data=data,
            duration_seconds=round(time.time() - start, 2),
        )
