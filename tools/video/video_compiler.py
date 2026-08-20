"""OpenMontage BaseTool wrapper for the Video Compiler.

Exposes the framework-agnostic compiler to the agent/registry as a tool, using
the project's selector+provider convention. The tool is the single integration
point; the real engine lives in ``videocompiler/`` and has no agent dependency.

Tool contract:
  * name: video_compiler
  * capability: video_compile
  * deterministic, local, free (uses the StubRenderer by default — honest seam)
  * accepts a canonical script artifact (schemas/artifacts/script.schema.json)
  * writes ir.json / render_graph.json / video_program.json to out_dir
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolTier,
)

from videocompiler import QualityTier, VideoCompiler
from videocompiler.selector import HardwareContext


class VideoCompilerTool(BaseTool):
    name = "video_compiler"
    version = "0.1.0"
    tier = ToolTier.CORE
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    capability = "video_compile"
    provider = "openmontage"
    capabilities = ["compile_script_to_timeline", "select_render_backend", "render_video_program"]
    description = (
        "Compile a canonical script into the provider-agnostic Video Compiler IR "
        "(Narrative -> Emotion -> Attention -> Scene -> Shot -> Timeline -> Render) "
        "and render it through a selected backend. Defaults to the deterministic "
        "StubRenderer so the full pipeline runs with no GPU and no API keys; real "
        "OSS backends (Wan/LTX/Hunyuan/CogVideoX) are swap-in adapters."
    )
    best_for = [
        "deterministic script -> timeline compilation",
        "backend-agnostic video planning",
        "incremental / A/B scene substitution",
    ]
    not_good_for = [
        "producing final pixels without a registered GPU backend",
    ]
    input_schema = {
        "type": "object",
        "properties": {
            "script": {"type": "object", "description": "Canonical script artifact."},
            "script_path": {"type": "string", "description": "Path to a script JSON file (alt to script)."},
            "backend_id": {"type": "string", "description": "Force a backend (e.g. 'stub','wan'). Omit to auto-select."},
            "tags": {"type": "object", "description": "Prompt tags -> weight, e.g. {'motion':0.9,'local':1.0}."},
            "quality": {"type": "string", "enum": ["draft", "standard", "high", "reference"]},
            "fps": {"type": "integer"},
            "out_dir": {"type": "string"},
        },
    }
    output_schema = {
        "type": "object",
        "properties": {
            "backend_id": {"type": "string"},
            "shot_count": {"type": "integer"},
            "duration_seconds": {"type": "number"},
            "ir_hash": {"type": "string"},
            "program_hash": {"type": "string"},
            "artifacts": {"type": "array", "items": {"type": "string"}},
        },
    }
    resource_profile = ResourceProfile(cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=10)
    side_effects = ["writes ir.json / render_graph.json / video_program.json to out_dir"]
    fallback_tools = ["video_compose"]

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        script = inputs.get("script")
        if script is None and inputs.get("script_path"):
            script = json.loads(Path(inputs["script_path"]).read_text(encoding="utf-8"))
        if script is None:
            return ToolResult(success=False, error="Provide 'script' or 'script_path'.")
        backend_id = inputs.get("backend_id")
        tags = inputs.get("tags") or None
        quality = QualityTier(inputs.get("quality", "standard"))
        fps = int(inputs.get("fps", 30))
        out_dir = inputs.get("out_dir", "out/video_compiler")

        # Honest hardware probe: read VRAM hint from env if present, else CPU.
        gpu_vram = int(__import__("os").environ.get("OM_GPU_VRAM_MB", "0"))
        hw = HardwareContext(gpu_vram_mb=gpu_vram)

        compiler = VideoCompiler(hardware=hw)
        try:
            ir, rg, program = compiler.run(
                script, backend_id=backend_id, tags=tags, quality=quality,
                fps=fps, out_dir=out_dir,
            )
        except Exception as exc:  # surface honest errors, never fabricate success
            return ToolResult(success=False, error=f"{type(exc).__name__}: {exc}")

        artifacts = [
            str(Path(out_dir) / "ir.json"),
            str(Path(out_dir) / "render_graph.json"),
            str(Path(out_dir) / "video_program.json"),
        ]
        return ToolResult(
            success=True,
            data={
                "backend_id": program.backend_id,
                "shot_count": len(rg.nodes),
                "duration_seconds": program.duration_seconds,
                "ir_hash": ir.content_hash,
                "program_hash": program.content_hash,
            },
            artifacts=artifacts,
        )


if __name__ == "__main__":
    # Allow `python -m tools.video.video_compiler` smoke run with a sample script.
    import sys

    sample = {
        "version": "1.0",
        "title": "Why the Video Compiler Matters",
        "total_duration_seconds": 30.0,
        "sections": [
            {"id": "s1", "text": "Most pipelines hardcode one video API.", "start_seconds": 0.0, "end_seconds": 10.0,
             "delivery_cues": {"pace": "conversational", "energy": "high"},
             "enhancement_cues": [{"type": "diagram", "description": "pipeline vs compiler"}]},
            {"id": "s2", "text": "A compiler IR makes every backend swappable.", "start_seconds": 10.0, "end_seconds": 20.0,
             "delivery_cues": {"pace": "brisk", "energy": "high"},
             "enhancement_cues": [{"type": "stat_card", "description": "8 backends"}]},
            {"id": "s3", "text": "Now the model is just a backend target.", "start_seconds": 20.0, "end_seconds": 30.0,
             "delivery_cues": {"pace": "measured", "energy": "calm"}},
        ],
    }
    tool = VideoCompilerTool()
    res = tool.execute({"script": sample, "out_dir": "out/video_compiler"})
    print(json.dumps(res.__dict__, indent=2, default=str))
