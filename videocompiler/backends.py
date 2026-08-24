"""Backend adapter layer — the heart of provider-agnostic rendering.

Every generation engine (commercial or open source) implements
``RenderBackend`` and registers a ``BackendCapability`` profile. The compiler
and selector only ever talk to this interface, so swapping Wan for LTX for
Runway is a one-line change at the edge.

Honest default: ``StubRenderer`` materializes a *real, inspectable* manifest
and deterministic placeholder footage with zero GPU and zero API keys. Real
backends (Wan/LTX/Hunyuan/CogVideoX/...) are declared below with hardware
tiers and capability scores — implement ``RenderBackend.render()`` to activate.
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from .ir import (
    AssetRef,
    BackendKind,
    HardwareContext,
    HardwareTier,
    QualityTier,
    RenderBackendSpec,
    RenderGraph,
    VideoCompilerIR,
    VideoProgram,
)


class BackendCapability:
    """Builder helper for declarative backend profiles (see ``BUILTIN_BACKENDS``)."""

    def __init__(
        self,
        id: str,
        kind: BackendKind,
        label: str,
        hardware: HardwareTier,
        quality_tiers: list[QualityTier],
        scores: dict[str, float],
        tag_weights: dict[str, float],
        requires_api_key: str | None = None,
    ) -> None:
        self.spec = RenderBackendSpec(
            id=id,
            kind=kind,
            label=label,
            hardware=hardware,
            quality_tiers=quality_tiers,
            scores=scores,
            tag_weights=tag_weights,
            requires_api_key=requires_api_key,
        )

    def with_installed(self, installed: bool) -> "BackendCapability":
        self.spec.installed = installed
        return self


# Declared backend catalog. Profiles are calibrated offline (not per-request).
# ``scores`` axes: motion, realism, prompt_adherence, temporal_coherence, speed.
# ``tag_weights``: how well the backend matches prompt tags (motion, realism,
# text_in_video, cheap, local).
BUILTIN_BACKEND_SPECS: list[RenderBackendSpec] = [
    BackendCapability(
        id="stub",
        kind=BackendKind.STUB,
        label="Stub (deterministic placeholder)",
        hardware=HardwareTier.CPU,
        quality_tiers=[QualityTier.DRAFT, QualityTier.STANDARD],
        scores={"motion": 0.1, "realism": 0.1, "prompt_adherence": 0.2,
                "temporal_coherence": 0.2, "speed": 1.0},
        tag_weights={"cheap": 1.0, "local": 1.0},
    ).spec,
    BackendCapability(
        id="wan",
        kind=BackendKind.WAN,
        label="Wan (Alibaba, local)",
        hardware=HardwareTier.GPU_24GB,
        quality_tiers=[QualityTier.STANDARD, QualityTier.HIGH, QualityTier.REFERENCE],
        scores={"motion": 0.85, "realism": 0.8, "prompt_adherence": 0.8,
                "temporal_coherence": 0.82, "speed": 0.4},
        tag_weights={"motion": 0.9, "realism": 0.8, "local": 1.0},
    ).spec,
    BackendCapability(
        id="ltx_local",
        kind=BackendKind.LTX,
        label="LTX-Video (local)",
        hardware=HardwareTier.GPU_8GB,
        quality_tiers=[QualityTier.STANDARD, QualityTier.HIGH],
        scores={"motion": 0.7, "realism": 0.65, "prompt_adherence": 0.7,
                "temporal_coherence": 0.68, "speed": 0.6},
        tag_weights={"motion": 0.7, "cheap": 0.6, "local": 1.0},
    ).spec,
    BackendCapability(
        id="hunyuan",
        kind=BackendKind.HUNYUAN,
        label="Hunyuan Video (local)",
        hardware=HardwareTier.GPU_48GB,
        quality_tiers=[QualityTier.HIGH, QualityTier.REFERENCE],
        scores={"motion": 0.9, "realism": 0.88, "prompt_adherence": 0.85,
                "temporal_coherence": 0.86, "speed": 0.3},
        tag_weights={"realism": 0.9, "motion": 0.85, "local": 1.0},
    ).spec,
    BackendCapability(
        id="cogvideo",
        kind=BackendKind.COGVIDEOX,
        label="CogVideoX (local)",
        hardware=HardwareTier.GPU_24GB,
        quality_tiers=[QualityTier.STANDARD, QualityTier.HIGH],
        scores={"motion": 0.75, "realism": 0.72, "prompt_adherence": 0.78,
                "temporal_coherence": 0.74, "speed": 0.45},
        tag_weights={"prompt_adherence": 0.8, "local": 1.0},
    ).spec,
    BackendCapability(
        id="runway",
        kind=BackendKind.COMMERCIAL,
        label="Runway (commercial API)",
        hardware=HardwareTier.API_KEY,
        quality_tiers=[QualityTier.HIGH, QualityTier.REFERENCE],
        scores={"motion": 0.88, "realism": 0.9, "prompt_adherence": 0.9,
                "temporal_coherence": 0.9, "speed": 0.7},
        tag_weights={"realism": 0.9, "quality": 0.9},
        requires_api_key="RUNWAY_API_KEY",
    ).spec,
    BackendCapability(
        id="veo",
        kind=BackendKind.COMMERCIAL,
        label="Veo (commercial API)",
        hardware=HardwareTier.API_KEY,
        quality_tiers=[QualityTier.HIGH, QualityTier.REFERENCE],
        scores={"motion": 0.92, "realism": 0.95, "prompt_adherence": 0.92,
                "temporal_coherence": 0.93, "speed": 0.6},
        tag_weights={"realism": 0.95, "quality": 0.95},
        requires_api_key="GEMINI_API_KEY",
    ).spec,
]


class RenderBackend(ABC):
    """Interface every generation engine implements."""

    #: Declared capability profile (hardware tier, scores, tags).
    spec: RenderBackendSpec

    def __init__(self, spec: RenderBackendSpec) -> None:
        self.spec = spec

    @abstractmethod
    def render(
        self, ir: VideoCompilerIR, render_graph: RenderGraph, out_dir: Path, quality: QualityTier
    ) -> VideoProgram:
        """Render the IR into a backend-specific ``VideoProgram``.

        Real backends write actual media into ``out_dir`` and populate
        ``assets`` + ``manifest``. Must return a finalized ``VideoProgram``.
        """
        ...

    def is_available(self, hardware: "HardwareContext | None" = None) -> bool:
        """Honest availability check.

        Installed AND (no API key required OR key present) AND, when a
        hardware context is supplied, the machine can actually run it.
        """
        if not self.spec.installed:
            return False
        if self.spec.requires_api_key:
            import os

            return bool(os.environ.get(self.spec.requires_api_key))
        if hardware is not None and not hardware.supports(self.spec):
            return False
        return True


class StubRenderer(RenderBackend):
    """Deterministic, zero-dependency renderer.

    Writes a real, inspectable manifest (JSON) and one placeholder media file
    per shot. This is the honest default: the entire pipeline runs end-to-end
    on a laptop with no GPU and no API keys. Replace by registering a real
    backend (Wan/LTX/Hunyuan/CogVideoX) that implements ``render()``.
    """

    def render(
        self, ir: VideoCompilerIR, render_graph: RenderGraph, out_dir: Path, quality: QualityTier
    ) -> VideoProgram:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        assets: list[AssetRef] = []
        nodes = render_graph.nodes
        for i, rn in enumerate(nodes):
            shot = next((s for s in (ir.shots.nodes if ir.shots else []) if s.id == rn.shot_id), None)
            dur = shot.duration_seconds if shot else 3.0
            # Deterministic placeholder asset: name + duration recorded, not fabricated pixels.
            asset_ref = AssetRef(
                kind="video_clip",
                ref=rn.shot_id,
                content_hash=rn.asset_ref,
                uri=str(out_dir / f"{rn.shot_id}.stub.mp4"),
                metadata={"duration_seconds": dur, "backend": self.spec.id, "quality": quality.value},
            )
            assets.append(asset_ref)
            # Materialize a tiny, real artifact so the output is inspectable.
            marker = {
                "shot_id": rn.shot_id,
                "backend": self.spec.id,
                "quality": quality.value,
                "duration_seconds": dur,
                "prompt": shot.prompt if shot else "",
                "placeholder": True,
            }
            (out_dir / f"{rn.shot_id}.stub.mp4").write_text(
                json.dumps(marker, indent=2), encoding="utf-8"
            )
        manifest = {
            "backend": self.spec.id,
            "backend_kind": self.spec.kind.value,
            "quality": quality.value,
            "shot_count": len(nodes),
            "duration_seconds": (ir.timeline.duration_seconds if ir.timeline else 0.0),
            "note": "Deterministic placeholder render. Swap in a real backend to produce media.",
        }
        program = VideoProgram(
            backend_id=self.spec.id,
            backend_kind=self.spec.kind,
            quality=quality,
            fps=ir.timeline.fps if ir.timeline else 30,
            duration_seconds=ir.timeline.duration_seconds if ir.timeline else 0.0,
            assets=assets,
            render_nodes=nodes,
            manifest=manifest,
        )
        return program.finalize()


class RendererRegistry:
    """Holds backend implementations keyed by id."""

    def __init__(self) -> None:
        self._backends: dict[str, RenderBackend] = {}

    def register(self, backend: RenderBackend) -> None:
        self._backends[backend.spec.id] = backend

    def get(self, backend_id: str) -> RenderBackend:
        if backend_id not in self._backends:
            raise KeyError(f"Unknown backend: {backend_id}")
        return self._backends[backend_id]

    def available(self, hardware: "HardwareContext | None" = None) -> list[str]:
        return [bid for bid, b in self._backends.items() if b.is_available(hardware)]

    def specs(self) -> list[RenderBackendSpec]:
        return [b.spec for b in self._backends.values()]


def default_registry() -> RendererRegistry:
    """Registry pre-populated with the StubRenderer + declared OSS/commercial specs.

    The OSS/commercial backends are registered as *unavailable* capability
    stubs (installed=False) so the selector can see them and fail over
    honestly until you implement ``render()`` and flip ``installed``.
    """
    reg = RendererRegistry()
    for spec in BUILTIN_BACKEND_SPECS:
        if spec.kind == BackendKind.STUB:
            reg.register(StubRenderer(spec))
        else:
            # Declared but not yet implemented -> registered as unavailable.
            reg.register(_DeclaredBackend(spec))
    return reg


class _DeclaredBackend(RenderBackend):
    """Capability-only backend. Raises if used before implementation."""

    def render(self, ir, render_graph, out_dir, quality) -> VideoProgram:
        raise NotImplementedError(
            f"Backend '{self.spec.id}' is declared but not implemented. "
            f"Implement RenderBackend.render() and register it to activate."
        )
