"""ima2-gen image generation tool for OpenMontage.

Supports high-quality 2D Stick Figure Cartoon illustrations, minimalist infographic art,
and general image generation via the local `ima2` CLI.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import time
import urllib.request
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


class Ima2Image(BaseTool):
    name = "ima2_image"
    version = "1.0.0"
    tier = ToolTier.GENERATE
    capability = "image_generation"
    provider = "ima2"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["cmd:ima2"]
    install_instructions = (
        "Install ima2-gen CLI:\n"
        "  npm install -g ima2-gen\n"
        "  ima2 serve\n"
    )
    agent_skills = ["flux-best-practices"]

    capabilities = [
        "generate_image",
        "generate_illustration",
        "text_to_image",
        "stick_figure_cartoon",
    ]
    supports = {
        "stick_figure_preset": True,
        "custom_prompt": True,
        "aspect_ratios": ["9:16", "16:9", "1:1"],
        "character_actions": True,
        "character_expressions": True,
    }
    best_for = [
        "minimalist 2D flat vector stickman educational illustrations (Taka style)",
        "offline and local fast image generation via ima2 proxy",
        "high-contrast character explainer diagrams on cream backgrounds",
    ]
    not_good_for = [
        "complex 3D CGI photorealism (use ComfyUI / Kling / Flux)",
    ]

    input_schema = {
        "type": "object",
        "required": ["prompt"],
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Text description of the scene or action",
            },
            "preset": {
                "type": "string",
                "enum": ["2d-stick-figure-cartoon", "minimalist-vector", "none"],
                "default": "2d-stick-figure-cartoon",
                "description": "Style preset applying design system rules and color palettes",
            },
            "aspect_ratio": {
                "type": "string",
                "enum": ["9:16", "16:9", "1:1", "auto"],
                "default": "9:16",
                "description": "Target aspect ratio (9:16 for portrait reels, 16:9 for landscape)",
            },
            "size": {
                "type": "string",
                "description": "Explicit size override (e.g. 1152x2048, 1824x1024, 1024x1024)",
            },
            "character_action": {
                "type": "string",
                "description": "Specific action performed by the character (e.g. holding a lightbulb, climbing stairs, pointing)",
            },
            "character_expression": {
                "type": "string",
                "description": "Expression state (e.g. happy, thinking, surprised, confident, shocked)",
            },
            "prop": {
                "type": "string",
                "description": "Key prop or icon in scene (e.g. lightbulb, money bag, target arrow, question mark)",
            },
            "output_path": {
                "type": "string",
                "description": "Path where the generated image should be saved",
            },
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=512, vram_mb=0, disk_mb=100, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=2, retryable_errors=["timeout", "server_error"])
    idempotency_key_fields = ["prompt", "preset", "aspect_ratio", "size"]
    side_effects = ["writes image file to output_path", "calls local ima2 server"]
    user_visible_verification = ["Inspect generated stickman illustration for design consistency"]

    def _ensure_server_running(self) -> bool:
        """Checks if ima2 server is responding; if not, attempts to ping."""
        server_url = os.environ.get("IMA2_SERVER", "http://127.0.0.1:3333")
        try:
            req = urllib.request.Request(f"{server_url}/api/status", headers={"User-Agent": "OpenMontage"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status in (200, 204):
                    return True
        except Exception:
            pass

        # Try `ima2 ping` command
        try:
            res = subprocess.run(["ima2", "ping"], capture_output=True, text=True, timeout=3)
            return res.returncode == 0
        except Exception:
            return False

    def _resolve_size(self, aspect_ratio: str, explicit_size: Optional[str] = None) -> str:
        if explicit_size:
            return explicit_size
        ar = (aspect_ratio or "9:16").lower()
        if ar in ("9:16", "portrait", "vertical"):
            return "1152x2048"
        elif ar in ("16:9", "landscape", "horizontal"):
            return "1824x1024"
        elif ar in ("1:1", "square"):
            return "1024x1024"
        return "1152x2048"

    def _build_stickman_prompt(self, base_prompt: str, action: Optional[str] = None, expression: Optional[str] = None, prop: Optional[str] = None) -> str:
        prefix = (
            "minimalist 2D flat vector explainer illustration, educational infographic animation style, "
            "cream background #ECE7D8, stickman character with white circular head, thick 8px black outline, "
            "orange shirt #F4A621, black necktie #181818, simple black limbs"
        )
        suffix = (
            "clean geometric shapes, flat color fills, no gradients, no photorealism, no 3D render, "
            "high contrast vector art, Adobe Illustrator style presentation"
        )
        
        details = []
        if action:
            details.append(f"character action: {action}")
        if expression:
            details.append(f"character expression: {expression}")
        if prop:
            details.append(f"featuring prop: {prop}")

        details_str = ", ".join(details)
        if details_str:
            return f"{prefix}, {base_prompt}, {details_str}, {suffix}"
        return f"{prefix}, {base_prompt}, {suffix}"

    def get_status(self) -> ToolStatus:
        if not shutil.which("ima2"):
            return ToolStatus.UNAVAILABLE
        return ToolStatus.AVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        t0 = time.time()
        prompt = inputs.get("prompt", "").strip()
        if not prompt:
            return ToolResult(
                success=False,
                error="Parameter 'prompt' is required and cannot be empty.",
                duration_seconds=time.time() - t0,
            )

        if not shutil.which("ima2"):
            return ToolResult(
                success=False,
                error="Executable 'ima2' not found on PATH. Please run 'npm install -g ima2-gen'.",
                duration_seconds=time.time() - t0,
            )

        preset = inputs.get("preset", "2d-stick-figure-cartoon")
        aspect_ratio = inputs.get("aspect_ratio", "9:16")
        size = self._resolve_size(aspect_ratio, inputs.get("size"))
        action = inputs.get("character_action")
        expression = inputs.get("character_expression")
        prop = inputs.get("prop")

        if preset == "2d-stick-figure-cartoon":
            final_prompt = self._build_stickman_prompt(prompt, action=action, expression=expression, prop=prop)
        elif preset == "minimalist-vector":
            final_prompt = f"minimalist 2D flat vector illustration, clean lines, solid background, {prompt}"
        else:
            final_prompt = prompt

        output_path_str = inputs.get("output_path")
        if output_path_str:
            out_path = pathlib.Path(output_path_str).resolve()
        else:
            out_path = (pathlib.Path("scratch") / f"ima2_{int(time.time() * 1000)}.png").resolve()

        out_path.parent.mkdir(parents=True, exist_ok=True)

        # Check server readiness
        if not self._ensure_server_running():
            # Attempt to spawn background server if not active
            try:
                subprocess.Popen(["ima2", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(2.0)
            except Exception as e:
                return ToolResult(
                    success=False,
                    error=f"Could not connect to ima2 server: {e}",
                    duration_seconds=time.time() - t0,
                )

        cmd = [
            "ima2",
            "gen",
            final_prompt,
            "-s",
            size,
            "-o",
            str(out_path),
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if res.returncode != 0:
                return ToolResult(
                    success=False,
                    error=f"ima2 gen failed (code {res.returncode}): {res.stderr.strip() or res.stdout.strip()}",
                    duration_seconds=time.time() - t0,
                )
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                error="ima2 gen timed out after 120s.",
                duration_seconds=time.time() - t0,
            )
        except Exception as err:
            return ToolResult(
                success=False,
                error=f"Failed to execute ima2 CLI: {err}",
                duration_seconds=time.time() - t0,
            )

        if not out_path.exists() or out_path.stat().st_size == 0:
            return ToolResult(
                success=False,
                error="ima2 reported success but output image file was not created.",
                duration_seconds=time.time() - t0,
            )

        return ToolResult(
            success=True,
            data={
                "image_path": str(out_path),
                "prompt": final_prompt,
                "preset": preset,
                "aspect_ratio": aspect_ratio,
                "size": size,
                "file_size_bytes": out_path.stat().st_size,
            },
            duration_seconds=round(time.time() - t0, 3),
        )
