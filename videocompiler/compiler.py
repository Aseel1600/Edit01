"""VideoCompiler — the entry point that turns a script into a rendered program.

Pipeline (deterministic, provider-agnostic):
    script -> lower_script_to_ir() -> VideoCompilerIR
           -> build_render_graph()  -> RenderGraph (asset-addressed)
           -> select_backend()      -> best available backend (offline profile)
           -> backend.render()       -> VideoProgram (backend-specific)

The compiled IR and render graph are persisted so a later run can do
incremental rendering / A/B scene substitution without re-lowering everything.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .backends import RendererRegistry, default_registry
from .ir import (
    AssetRef,
    BackendKind,
    ContentHash,
    HardwareTier,
    QualityTier,
    RenderGraph,
    RenderNode,
    VideoCompilerIR,
    VideoProgram,
)
from .selector import BackendSelector, HardwareContext, SelectResult
from .transforms import lower_script_to_ir


class VideoCompiler:
    def __init__(
        self,
        registry: RendererRegistry | None = None,
        hardware: HardwareContext | None = None,
        planner=None,
    ) -> None:
        self.registry = registry or default_registry()
        self.hardware = hardware or HardwareContext()
        self._planner = planner

    # -- Stage: lower -----------------------------------------------------

    def compile_ir(self, script: dict[str, Any], *, fps: int = 30, source_id: str = "") -> VideoCompilerIR:
        return lower_script_to_ir(script, planner=self._planner, fps=fps, source_id=source_id)

    # -- Stage: render graph ---------------------------------------------

    def build_render_graph(self, ir: VideoCompilerIR) -> RenderGraph:
        """Map each shot to a content-addressed RenderNode (no media yet)."""
        nodes: list[RenderNode] = []
        if ir.shots is None:
            raise ValueError("IR has no shot graph; lower a script first.")
        for sh in ir.shots.nodes:
            # Asset ref = content hash of the shot's generation contract.
            contract = {
                "prompt": sh.prompt,
                "negative_prompt": sh.negative_prompt,
                "duration_seconds": sh.duration_seconds,
                "shot_type": sh.shot_type,
                "motion": sh.motion,
            }
            asset_ref = ContentHash.from_obj(contract).digest
            nodes.append(
                RenderNode(
                    shot_id=sh.id,
                    asset_ref=asset_ref,
                    backend="",  # resolved at select time
                    params=contract,
                )
            )
        rg = RenderGraph(nodes=nodes)
        return rg.finalize()

    # -- Stage: select ----------------------------------------------------

    def select(
        self, tags: dict[str, float] | None = None, quality: QualityTier = QualityTier.STANDARD
    ) -> SelectResult:
        return BackendSelector(self.registry, self.hardware).select(tags=tags, quality=quality)

    # -- Stage: render ----------------------------------------------------

    def render(
        self,
        ir: VideoCompilerIR,
        render_graph: RenderGraph,
        *,
        backend_id: str | None = None,
        tags: dict[str, float] | None = None,
        quality: QualityTier = QualityTier.STANDARD,
        out_dir: str | Path = "out/video_compiler",
    ) -> VideoProgram:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        if backend_id is None:
            sel = self.select(tags=tags, quality=quality)
            backend_id = sel.backend_id
        backend = self.registry.get(backend_id)
        if not backend.is_available(self.hardware):
            raise RuntimeError(
                f"Backend '{backend_id}' is not available on this hardware/keys. "
                f"Use select() to find a runnable backend."
            )
        # Stamp the chosen backend onto each render node (provenance).
        for n in render_graph.nodes:
            n.backend = backend_id
        return backend.render(ir, render_graph, out_dir, quality)

    # -- Full run ---------------------------------------------------------

    def run(
        self,
        script: dict[str, Any],
        *,
        backend_id: str | None = None,
        tags: dict[str, float] | None = None,
        quality: QualityTier = QualityTier.STANDARD,
        fps: int = 30,
        source_id: str = "",
        out_dir: str | Path = "out/video_compiler",
        persist: bool = True,
    ) -> tuple[VideoCompilerIR, RenderGraph, VideoProgram]:
        ir = self.compile_ir(script, fps=fps, source_id=source_id)
        rg = self.build_render_graph(ir)
        program = self.render(ir, rg, backend_id=backend_id, tags=tags, quality=quality, out_dir=out_dir)
        if persist:
            self._persist(ir, rg, program, Path(out_dir))
        return ir, rg, program

    def _persist(self, ir: VideoCompilerIR, rg: RenderGraph, program: VideoProgram, out_dir: Path) -> None:
        (out_dir / "ir.json").write_text(ir.model_dump_json(indent=2), encoding="utf-8")
        (out_dir / "render_graph.json").write_text(rg.model_dump_json(indent=2), encoding="utf-8")
        (out_dir / "video_program.json").write_text(program.model_dump_json(indent=2), encoding="utf-8")
