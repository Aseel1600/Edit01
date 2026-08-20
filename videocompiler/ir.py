"""Typed intermediate representation (IR) for the OpenMontage Video Compiler.

Stages (each is versioned and validated):
    NarrativeGraph  -> high-level story / message / audience
    EmotionGraph    -> desired emotional arc beat-by-beat
    AttentionCurve  -> predicted viewer-attention curve over time
    SceneGraph      -> story beats grouped into scenes (nodes + edges)
    ShotGraph       -> scenes expanded into shots (nodes + edges)
    TimelineDSL     -> time-aligned tracks of events (the editorial timeline)
    RenderGraph     -> backend-agnostic render plan (assets + ops per shot)
    VideoProgram    -> fully resolved, backend-specific render program

Asset addressing: every asset carries a content hash (sha256 of its canonical
JSON) so re-renders and scene substitutions are cheap and deterministic.
"""

from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class HardwareTier(str, Enum):
    """Hardware envelope a backend requires. Drives failover, not benchmarks."""

    CPU = "cpu"
    GPU_8GB = "gpu_8gb"
    GPU_24GB = "gpu_24gb"
    GPU_48GB = "gpu_48gb"
    API_KEY = "api_key"


class QualityTier(str, Enum):
    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    REFERENCE = "reference"


from dataclasses import dataclass, field


@dataclass
class HardwareContext:
    """What this machine can actually offer right now.

    Shared by the selector and backend availability checks so there is a
    single source of truth for "can this backend run here?".
    """

    gpu_vram_mb: int = 0
    api_keys: set[str] = field(default_factory=set)  # env var names present

    def supports(self, spec: "RenderBackendSpec") -> bool:  # type: ignore[name-defined]
        return _hardware_supports(self, spec)


def _hardware_supports(hw: "HardwareContext", spec: "RenderBackendSpec") -> bool:  # type: ignore[name-defined]
    if spec.requires_api_key:
        return spec.requires_api_key in hw.api_keys
    rank = {
        HardwareTier.CPU: 0,
        HardwareTier.GPU_8GB: 1,
        HardwareTier.GPU_24GB: 2,
        HardwareTier.GPU_48GB: 3,
        HardwareTier.API_KEY: 4,
    }
    max_hw = HardwareTier.CPU
    if hw.gpu_vram_mb >= 48 * 1024:
        max_hw = HardwareTier.GPU_48GB
    elif hw.gpu_vram_mb >= 24 * 1024:
        max_hw = HardwareTier.GPU_24GB
    elif hw.gpu_vram_mb >= 8 * 1024:
        max_hw = HardwareTier.GPU_8GB
    return rank[spec.hardware] <= rank[max_hw]


class BackendKind(str, Enum):
    """Family of generation engine. Used by the selector for tag matching."""

    STUB = "stub"            # deterministic placeholder (honest default)
    DIFFUSION = "diffusion"  # image diffusion (FLUX/SDXL) per-frame
    WAN = "wan"
    LTX = "ltx"
    HUNYUAN = "hunyuan"
    COGVIDEOX = "cogvideo"
    OPEN_SORA = "open_sora"
    MOCHI = "mochi"
    PYRAMID = "pyramid"
    SKYREELS = "skyreels"
    FRAMEPACK = "framepack"
    COMMERCIAL = "commercial"  # Runway / Veo / proprietary


class ContentHash(BaseModel):
    """Content-addressable reference. `alg` is always 'sha256'."""

    alg: str = "sha256"
    digest: str

    @classmethod
    def from_obj(cls, obj: Any) -> "ContentHash":
        canonical = json.dumps(obj, sort_keys=True, ensure_ascii=False)
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return cls(digest=digest)


def hash_content(obj: Any) -> str:
    """Return the sha256 hex digest of a canonical-JSON encoding of ``obj``."""
    return ContentHash.from_obj(obj).digest


class AssetRef(BaseModel):
    """Content-addressed asset handle.

    ``kind`` is the media role (video_clip, image, audio, music, voiceover,
    subtitle, ...). ``ref`` is a logical id; ``content_hash`` makes the asset
    immutable and cacheable across renders (enables incremental rendering).
    """

    kind: str
    ref: str
    content_hash: str
    uri: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# --------------------------------------------------------------------------
# Narrative layer
# --------------------------------------------------------------------------


class NarratorNote(BaseModel):
    section_id: str
    note: str


class NarrativeGraph(BaseModel):
    ir_version: str = "1.0"
    title: str
    logline: str = ""
    thesis: str = ""
    audience: str = ""
    tone: str = ""
    narrator_notes: list[NarratorNote] = Field(default_factory=list)
    content_hash: Optional[str] = None

    def finalize(self) -> "NarrativeGraph":
        payload = self.model_dump(exclude={"content_hash"})
        return self.model_copy(update={"content_hash": hash_content(payload)})


# --------------------------------------------------------------------------
# Emotion / attention layer
# --------------------------------------------------------------------------


class EmotionBeat(BaseModel):
    """A point on the emotional arc. ``t`` is seconds from start."""

    t: float
    emotion: str  # e.g. curiosity, tension, relief, awe
    intensity: float = Field(ge=0.0, le=1.0)


class EmotionGraph(BaseModel):
    ir_version: str = "1.0"
    beats: list[EmotionBeat] = Field(default_factory=list)
    content_hash: Optional[str] = None

    def finalize(self) -> "EmotionGraph":
        payload = self.model_dump(exclude={"content_hash"})
        return self.model_copy(update={"content_hash": hash_content(payload)})


class AttentionPoint(BaseModel):
    """Predicted viewer-attention level at time ``t`` (0..1)."""

    t: float
    level: float = Field(ge=0.0, le=1.0)
    reason: str = ""


class AttentionCurve(BaseModel):
    ir_version: str = "1.0"
    points: list[AttentionPoint] = Field(default_factory=list)
    content_hash: Optional[str] = None

    def finalize(self) -> "AttentionCurve":
        payload = self.model_dump(exclude={"content_hash"})
        return self.model_copy(update={"content_hash": hash_content(payload)})


# --------------------------------------------------------------------------
# Scene layer
# --------------------------------------------------------------------------


class SceneNode(BaseModel):
    id: str
    title: str = ""
    summary: str = ""
    emotion: str = ""
    # Logical duration bounds (seconds). Resolved later by the planner.
    start_seconds: Optional[float] = None
    end_seconds: Optional[float] = None
    enhancement_cues: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)


class SceneEdge(BaseModel):
    from_id: str
    to_id: str
    relation: str = "sequential"  # sequential | flashback | parallel


class SceneGraph(BaseModel):
    ir_version: str = "1.0"
    nodes: list[SceneNode] = Field(default_factory=list)
    edges: list[SceneEdge] = Field(default_factory=list)
    content_hash: Optional[str] = None

    def finalize(self) -> "SceneGraph":
        payload = self.model_dump(exclude={"content_hash"})
        return self.model_copy(update={"content_hash": hash_content(payload)})


# --------------------------------------------------------------------------
# Shot layer
# --------------------------------------------------------------------------


class ShotNode(BaseModel):
    id: str
    scene_id: str
    index: int = 0
    description: str = ""
    shot_type: str = ""  # e.g. wide, close_up, insert
    motion: str = ""     # e.g. static, pan, zoom_in, handheld
    duration_seconds: float = Field(default=3.0, ge=0.0)
    prompt: str = ""     # generation prompt for the render backend
    negative_prompt: str = ""
    enhancement_cues: list[str] = Field(default_factory=list)


class ShotEdge(BaseModel):
    from_id: str
    to_id: str
    transition: str = "cut"  # cut | dissolve | wipe | smash


class ShotGraph(BaseModel):
    ir_version: str = "1.0"
    nodes: list[ShotNode] = Field(default_factory=list)
    edges: list[ShotEdge] = Field(default_factory=list)
    content_hash: Optional[str] = None

    def finalize(self) -> "ShotGraph":
        payload = self.model_dump(exclude={"content_hash"})
        return self.model_copy(update={"content_hash": hash_content(payload)})


# --------------------------------------------------------------------------
# Timeline layer (editorial DSL)
# --------------------------------------------------------------------------


class TimelineEvent(BaseModel):
    id: str
    track: str          # video | broll | voiceover | music | sfx | subtitle
    asset_ref: Optional[str] = None
    start_seconds: float
    end_seconds: float
    label: str = ""


class TimelineTrack(BaseModel):
    name: str
    events: list[TimelineEvent] = Field(default_factory=list)


class TimelineDSL(BaseModel):
    ir_version: str = "1.0"
    fps: int = 30
    duration_seconds: float = 0.0
    tracks: list[TimelineTrack] = Field(default_factory=list)
    content_hash: Optional[str] = None

    def finalize(self) -> "TimelineDSL":
        payload = self.model_dump(exclude={"content_hash"})
        return self.model_copy(update={"content_hash": hash_content(payload)})


# --------------------------------------------------------------------------
# Render layer (backend-agnostic)
# --------------------------------------------------------------------------


class RenderNode(BaseModel):
    shot_id: str
    asset_ref: str
    backend: str        # backend id, e.g. "stub", "wan", "ltx_local"
    params: dict[str, Any] = Field(default_factory=dict)
    estimated_seconds: Optional[float] = None


class RenderGraph(BaseModel):
    ir_version: str = "1.0"
    nodes: list[RenderNode] = Field(default_factory=list)
    content_hash: Optional[str] = None

    def finalize(self) -> "RenderGraph":
        payload = self.model_dump(exclude={"content_hash"})
        return self.model_copy(update={"content_hash": hash_content(payload)})


class RenderBackendSpec(BaseModel):
    """Declarative capability profile of a render backend.

    This is the single source of truth the selector uses. No benchmarking at
    request time — profiles are calibrated offline and shipped with the backend.
    """

    id: str
    kind: BackendKind
    label: str
    hardware: HardwareTier
    quality_tiers: list[QualityTier] = Field(default_factory=list)
    # 0..1 axis scores used by the tag-based selector.
    scores: dict[str, float] = Field(default_factory=dict)
    # Prompt-tag match weights (e.g. {"motion": 0.9, "realism": 0.6}).
    tag_weights: dict[str, float] = Field(default_factory=dict)
    requires_api_key: Optional[str] = None  # env var name if API_KEY tier
    installed: bool = True  # honest seam: false means declared but not present


# --------------------------------------------------------------------------
# Final program (backend-specific, fully resolved)
# --------------------------------------------------------------------------


class VideoProgram(BaseModel):
    ir_version: str = "1.0"
    backend_id: str
    backend_kind: BackendKind
    quality: QualityTier
    fps: int = 30
    duration_seconds: float = 0.0
    assets: list[AssetRef] = Field(default_factory=list)
    render_nodes: list[RenderNode] = Field(default_factory=list)
    manifest: dict[str, Any] = Field(default_factory=dict)
    content_hash: Optional[str] = None

    def finalize(self) -> "VideoProgram":
        payload = self.model_dump(exclude={"content_hash"})
        return self.model_copy(update={"content_hash": hash_content(payload)})


# --------------------------------------------------------------------------
# Top-level IR bundle
# --------------------------------------------------------------------------


class VideoCompilerIR(BaseModel):
    """The full staged IR produced by lowering a script (or any source)."""

    ir_version: str = "1.0"
    source_id: str = ""
    narrative: Optional[NarrativeGraph] = None
    emotion: Optional[EmotionGraph] = None
    attention: Optional[AttentionCurve] = None
    scenes: Optional[SceneGraph] = None
    shots: Optional[ShotGraph] = None
    timeline: Optional[TimelineDSL] = None
    render: Optional[RenderGraph] = None
    content_hash: Optional[str] = None

    def finalize(self) -> "VideoCompilerIR":
        # Finalize sub-graphs first (idempotent), then the bundle.
        updated: dict[str, Any] = {}
        for fname in ("narrative", "emotion", "attention", "scenes", "shots", "timeline", "render"):
            g = getattr(self, fname)
            if g is not None and hasattr(g, "finalize"):
                updated[fname] = g.finalize()
        payload = self.model_dump(exclude={"content_hash"})
        for k, v in updated.items():
            payload[k] = v.model_dump()
        return self.model_copy(update={**updated, "content_hash": hash_content(payload)})
