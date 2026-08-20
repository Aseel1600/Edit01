"""OpenMontage Video Compiler — provider-agnostic intermediate representation.

The Video Compiler is the "LLVM of Hermes": every generation backend
(commercial or open source) is just another target that consumes the same
typed intermediate representation (IR). This makes backends swappable,
enables deterministic editing, A/B scene substitution, and incremental
rendering without rewriting the creative pipeline.

Design contract (honest seams):
  * The IR and every lowering transform are *deterministic* (stdlib + pydantic).
  * LLM-driven planning is a documented swap point: ``DefaultPlanner`` is a
    deterministic stand-in so the whole pipeline runs with zero GPU and zero
    API keys. Replace it by subclassing ``Planner``.
  * GPU renderers (Wan, LTX, Hunyuan, CogVideoX, ...) are declared backends
    with capability profiles. ``StubRenderer`` is the honest default that
    materializes a real, inspectable manifest + deterministic placeholder
    footage. Swap in a real backend by implementing ``RendererBackend``.

This module is framework-agnostic and does NOT depend on OpenMontage's agent
stack, so it can be unit-tested in isolation and imported by tools/ runners.
"""

from .ir import (
    AssetRef,
    AttentionCurve,
    AttentionPoint,
    BackendKind,
    ContentHash,
    EmotionBeat,
    EmotionGraph,
    HardwareTier,
    NarrativeGraph,
    NarratorNote,
    QualityTier,
    RenderBackendSpec,
    RenderGraph,
    RenderNode,
    SceneEdge,
    SceneGraph,
    SceneNode,
    ShotEdge,
    ShotGraph,
    ShotNode,
    TimelineDSL,
    TimelineEvent,
    TimelineTrack,
    VideoCompilerIR,
    VideoProgram,
    hash_content,
)
from .planner import DefaultPlanner, Planner
from .transforms import lower_script_to_ir
from .backends import (
    BackendCapability,
    RenderBackend,
    RendererRegistry,
    StubRenderer,
)
from .selector import BackendSelector, select_backend
from .compiler import VideoCompiler

__all__ = [
    "VideoCompiler",
    "VideoCompilerIR",
    "NarrativeGraph",
    "EmotionGraph",
    "AttentionCurve",
    "SceneGraph",
    "ShotGraph",
    "TimelineDSL",
    "RenderGraph",
    "VideoProgram",
    "AssetRef",
    "ContentHash",
    "Planner",
    "DefaultPlanner",
    "lower_script_to_ir",
    "RenderBackend",
    "StubRenderer",
    "RendererRegistry",
    "BackendCapability",
    "BackendSelector",
    "select_backend",
    "HardwareTier",
    "QualityTier",
    "BackendKind",
]
