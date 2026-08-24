"""Planner: turns a source (script / brief) into the narrative + emotion
+ attention layers of the IR.

SWAP POINT: ``DefaultPlanner`` is a *deterministic*, rule-based stand-in so the
whole pipeline runs with zero GPU and zero API keys. It infers an emotional arc
and an attention curve from the script's structure (section count, pacing,
enhancement cues). To use a real LLM planner, subclass ``Planner`` and override
``plan()`` — nothing else in the compiler changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .ir import (
    AttentionCurve,
    AttentionPoint,
    EmotionBeat,
    EmotionGraph,
    NarrativeGraph,
    SceneNode,
)


@dataclass
class SourceScript:
    """Minimal structural view of a script the planner consumes.

    Mirrors the canonical ``schemas/artifacts/script.schema.json`` shape
    closely enough to accept real scripts directly.
    """

    title: str
    total_duration_seconds: float
    sections: list[dict[str, Any]]
    logline: str = ""
    thesis: str = ""
    audience: str = ""
    tone: str = ""


class Planner:
    """Abstract planner interface. Subclass to plug in an LLM."""

    def plan(self, source: SourceScript) -> tuple[NarrativeGraph, EmotionGraph, AttentionCurve]:
        raise NotImplementedError


class DefaultPlanner(Planner):
    """Deterministic planner: derives arcs from script structure.

    Honest-seam default. Produces a *plausible* narrative/emotion/attention
    skeleton that downstream stages (scene/shot/timeline) can refine. It never
    invents facts; it propagates structure (section timing, enhancement cues,
    pacing profile) into the creative graphs.
    """

    # Shared emotional vocabulary the planner cycles through for beats.
    _EMOTION_CYCLE = ["curiosity", "tension", "anticipation", "relief", "awe", "resolution"]

    def plan(self, source: SourceScript) -> tuple[NarrativeGraph, EmotionGraph, AttentionCurve]:
        narrative = self._plan_narrative(source)
        emotion = self._plan_emotion(source)
        attention = self._plan_attention(source)
        return narrative, emotion, attention

    def _plan_narrative(self, source: SourceScript) -> NarrativeGraph:
        notes = []
        for s in source.sections:
            sid = s.get("id", "")
            note = s.get("delivery_cues", {}).get("delivery_note") or s.get("speaker_directions", "")
            if note:
                notes.append({"section_id": sid, "note": note})
        ng = NarrativeGraph(
            title=source.title,
            logline=source.logline,
            thesis=source.thesis,
            audience=source.audience,
            tone=source.tone or self._infer_tone(source),
            narrator_notes=notes,
        )
        return ng.finalize()

    def _infer_tone(self, source: SourceScript) -> str:
        pacing = ""
        if source.sections:
            pacing = source.sections[0].get("delivery_cues", {}).get("pace", "")
        if pacing in ("energetic", "fast", "brisk"):
            return "energetic"
        if pacing in ("contemplative", "slow", "measured"):
            return "contemplative"
        return "conversational"

    def _plan_emotion(self, source: SourceScript) -> EmotionGraph:
        total = max(source.total_duration_seconds, 1.0)
        n = max(len(source.sections), 1)
        beats = []
        for i, s in enumerate(source.sections):
            t = s.get("start_seconds", (total / n) * i)
            try:
                t = float(t)
            except (TypeError, ValueError):
                t = (total / n) * i
            emotion = self._EMOTION_CYCLE[i % len(self._EMOTION_CYCLE)]
            beats.append(EmotionBeat(t=t, emotion=emotion, intensity=self._intensity_for(s, i, n)))
        if not beats:
            beats.append(EmotionBeat(t=0.0, emotion="neutral", intensity=0.5))
        eg = EmotionGraph(beats=beats)
        return eg.finalize()

    def _intensity_for(self, section: dict[str, Any], i: int, n: int) -> float:
        cue = section.get("delivery_cues", {})
        energy = (cue.get("energy") or "").lower()
        if energy in ("high", "excited", "intense"):
            base = 0.85
        elif energy in ("low", "calm", "soft"):
            base = 0.4
        else:
            base = 0.6
        # Slight arc: build toward the middle, settle at the end.
        mid = n / 2.0
        arc = 1.0 - abs(i - mid) / max(mid, 1.0)
        return round(min(1.0, max(0.1, base * (0.7 + 0.3 * arc))), 3)

    def _plan_attention(self, source: SourceScript) -> AttentionCurve:
        total = max(source.total_duration_seconds, 1.0)
        n = max(len(source.sections), 1)
        points = []
        for i, s in enumerate(source.sections):
            t = s.get("start_seconds", (total / n) * i)
            try:
                t = float(t)
            except (TypeError, ValueError):
                t = (total / n) * i
            # Enhancement cues (broll, diagram, stat_card) boost predicted attention.
            cues = s.get("enhancement_cues", [])
            boost = 0.12 * len(cues)
            level = round(min(1.0, 0.55 + boost + 0.1 * (i % 2)), 3)
            reason = "enhancement cues" if cues else "narration"
            points.append(AttentionPoint(t=t, level=level, reason=reason))
        # Add the closing point.
        points.append(AttentionPoint(t=total, level=0.5, reason="outro"))
        ac = AttentionCurve(points=points)
        return ac.finalize()
