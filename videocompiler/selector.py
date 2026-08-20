"""Backend selector — tag-based, offline-calibrated.

NO live per-request benchmarking (infeasible: each render is minutes of GPU).
Instead each backend carries a static capability/quality/cost profile and the
selector scores candidates against prompt tags + target quality + available
hardware. This is the same multiplicative-scoring pattern used across
OpenMontage's opportunity engine — applied to render routing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .backends import RendererRegistry
from .ir import HardwareContext, HardwareTier, QualityTier, RenderBackendSpec, _hardware_supports


# Hardware precedence for failover when a tier is unavailable.
_HARDWARE_RANK = {
    HardwareTier.CPU: 0,
    HardwareTier.GPU_8GB: 1,
    HardwareTier.GPU_24GB: 2,
    HardwareTier.GPU_48GB: 3,
    HardwareTier.API_KEY: 4,
}

# Axis weights used to combine the profile's ``scores`` into a fit score.
_AXIS_WEIGHTS = {
    "motion": 0.25,
    "realism": 0.2,
    "prompt_adherence": 0.2,
    "temporal_coherence": 0.2,
    "speed": 0.15,
}


@dataclass
class SelectResult:
    backend_id: str
    score: float
    reason: str
    candidates: list[tuple[str, float, str]]


class BackendSelector:
    """Scores backends against prompt tags + quality + hardware."""

    def __init__(self, registry: RendererRegistry, hardware: HardwareContext | None = None) -> None:
        self.registry = registry
        self.hardware = hardware or HardwareContext()

    def score_one(self, spec: RenderBackendSpec, tags: dict[str, float], quality: QualityTier) -> float:
        # Axis fit: weighted sum of profile scores (these are axis scores).
        axis_fit = sum(_AXIS_WEIGHTS.get(k, 0.0) * spec.scores.get(k, 0.0)
                       for k in _AXIS_WEIGHTS)
        # Tag match: weighted alignment of spec.tag_weights with requested tags.
        if tags:
            tag_fit = sum(spec.tag_weights.get(t, 0.0) * w for t, w in tags.items())
            tag_denom = max(sum(w for w in tags.values()), 1e-6)
            tag_fit = tag_fit / tag_denom
        else:
            tag_fit = 0.5  # no preference -> neutral
        # Quality reachability: does the backend support the requested tier?
        quality_ok = 1.0 if quality in spec.quality_tiers else 0.4
        return round(axis_fit * 0.5 + tag_fit * 0.3 + quality_ok * 0.2, 4)

    def select(
        self, tags: dict[str, float] | None = None, quality: QualityTier = QualityTier.STANDARD
    ) -> SelectResult:
        tags = tags or {}
        candidates: list[tuple[str, float, str]] = []
        for spec in self.registry.specs():
            if not self.hardware.supports(spec):
                candidates.append((spec.id, 0.0, f"hardware/key unavailable ({spec.hardware.value})"))
                continue
            sc = self.score_one(spec, tags, quality)
            reason = f"axis+tag+quality fit={sc}"
            candidates.append((spec.id, sc, reason))
        # Highest score wins; ties broken by hardware rank (cheaper first).
        ranked = sorted(
            candidates,
            key=lambda c: (c[1], -_HARDWARE_RANK[self._spec(c[0]).hardware]),
            reverse=True,
        )
        best_id, best_score, best_reason = ranked[0]
        return SelectResult(backend_id=best_id, score=best_score, reason=best_reason, candidates=ranked)

    def _spec(self, backend_id: str) -> RenderBackendSpec:
        for s in self.registry.specs():
            if s.id == backend_id:
                return s
        raise KeyError(backend_id)


def select_backend(
    registry: RendererRegistry,
    tags: dict[str, float] | None = None,
    quality: QualityTier = QualityTier.STANDARD,
    hardware: HardwareContext | None = None,
) -> SelectResult:
    """Convenience wrapper."""
    return BackendSelector(registry, hardware).select(tags=tags, quality=quality)
