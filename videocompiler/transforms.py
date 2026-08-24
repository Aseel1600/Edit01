"""Lowering transforms: pure functions ``Graph -> Graph`` over the IR.

Each stage is a *pure transform* of the staged IR. This is what makes the
pipeline composable, parallelizable, and revisitable (a stage can re-run
without re-running earlier ones). The transforms are deterministic.

    lower_script_to_ir(source) -> VideoCompilerIR
        Narrative -> Emotion -> Attention -> Scene -> Shot -> Timeline
"""

from __future__ import annotations

from typing import Any

from .ir import (
    AttentionCurve,
    EmotionGraph,
    NarrativeGraph,
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
)
from .planner import DefaultPlanner, Planner, SourceScript


def _to_source_script(script: dict[str, Any]) -> SourceScript:
    """Coerce a canonical script dict into the planner's SourceScript view."""
    return SourceScript(
        title=script.get("title", "Untitled"),
        total_duration_seconds=float(script.get("total_duration_seconds", 0.0)),
        sections=script.get("sections", []),
        logline=script.get("logline", ""),
        thesis=script.get("thesis", ""),
        audience=script.get("audience", ""),
        tone=(script.get("voice_performance", {}) or {}).get("pacing_profile", ""),
    )


def _lower_to_scenes(source: SourceScript) -> SceneGraph:
    nodes: list[SceneNode] = []
    edges: list[SceneEdge] = []
    prev: str | None = None
    for i, s in enumerate(source.sections):
        sid = s.get("id") or f"scene_{i:03d}"
        start = s.get("start_seconds")
        end = s.get("end_seconds")
        cues = [c.get("description", "") for c in s.get("enhancement_cues", [])]
        node = SceneNode(
            id=sid,
            title=s.get("label", f"Scene {i + 1}"),
            summary=s.get("text", "")[:240],
            emotion="",
            start_seconds=float(start) if start is not None else None,
            end_seconds=float(end) if end is not None else None,
            enhancement_cues=[c for c in cues if c],
            source_refs=[s.get("source_ref", "")] if s.get("source_ref") else [],
        )
        nodes.append(node)
        if prev is not None:
            edges.append(SceneEdge(from_id=prev, to_id=sid))
        prev = sid
    sg = SceneGraph(nodes=nodes, edges=edges)
    return sg.finalize()


def _lower_to_shots(scenes: SceneGraph, source: SourceScript) -> ShotGraph:
    shot_nodes: list[ShotNode] = []
    shot_edges: list[ShotEdge] = []
    prev_shot: str | None = None
    shot_idx = 0
    for sc in scenes.nodes:
        # One shot per scene by default; divide scene duration into ~3s shots.
        dur = 3.0
        if sc.start_seconds is not None and sc.end_seconds is not None:
            dur = max(1.0, sc.end_seconds - sc.start_seconds)
        n_shots = max(1, int(round(dur / 3.0)))
        seg = dur / n_shots
        for j in range(n_shots):
            shot_id = f"{sc.id}__shot_{j:02d}"
            section = next(
                (s for s in source.sections if (s.get("id") or "") == sc.id), {}
            )
            cue = (section.get("delivery_cues", {}) or {}).get("delivery_note", "")
            shot_nodes.append(
                ShotNode(
                    id=shot_id,
                    scene_id=sc.id,
                    index=j,
                    description=sc.summary,
                    shot_type="wide" if j == 0 else "insert",
                    motion="static" if j == 0 else "cutaway",
                    duration_seconds=round(seg, 3),
                    prompt=_build_prompt(sc, section, j),
                    negative_prompt="blurry, low quality, watermark",
                    enhancement_cues=sc.enhancement_cues,
                )
            )
            if prev_shot is not None:
                shot_edges.append(ShotEdge(from_id=prev_shot, to_id=shot_id))
            prev_shot = shot_id
            shot_idx += 1
    sg = ShotGraph(nodes=shot_nodes, edges=shot_edges)
    return sg.finalize()


def _build_prompt(scene: SceneNode, section: dict[str, Any], shot_idx: int) -> str:
    base = (scene.summary or scene.title).strip()
    cues = " ".join(scene.enhancement_cues[:3])
    extra = f" Visual cues: {cues}." if cues else ""
    if shot_idx == 0:
        return f"Cinematic establishing shot. {base}{extra}".strip()
    return f"Detailed cutaway illustrating: {base}{extra}".strip()


def _lower_to_timeline(shots: ShotGraph, scenes: SceneGraph, fps: int = 30) -> TimelineDSL:
    # Align shots sequentially on the video track using their durations.
    tracks: dict[str, list[TimelineEvent]] = {"video": []}
    # Map scene -> voiceover section text for a parallel voiceover track.
    cursor = 0.0
    scene_start: dict[str, float] = {}
    scene_end: dict[str, float] = {}
    for sh in shots.nodes:
        scene_start.setdefault(sh.scene_id, cursor)
        scene_end[sh.scene_id] = cursor + sh.duration_seconds
        tracks["video"].append(
            TimelineEvent(
                id=sh.id,
                track="video",
                asset_ref=sh.id,
                start_seconds=round(cursor, 3),
                end_seconds=round(cursor + sh.duration_seconds, 3),
                label=sh.description[:80],
            )
        )
        cursor += sh.duration_seconds
    # Voiceover track from scene summaries (placeholder asset refs).
    for sc in scenes.nodes:
        s = scene_start.get(sc.id, 0.0)
        e = scene_end.get(sc.id, s + 3.0)
        tracks.setdefault("voiceover", []).append(
            TimelineEvent(
                id=f"vo_{sc.id}",
                track="voiceover",
                asset_ref=f"vo_{sc.id}",
                start_seconds=s,
                end_seconds=e,
                label=sc.title,
            )
        )
    timeline = TimelineDSL(
        fps=fps,
        # Snap the authoritative duration to the frame grid to avoid
        # float accumulation drift from per-shot 3-decimal rounding.
        duration_seconds=round(cursor * fps) / fps,
        tracks=[TimelineTrack(name=name, events=evs) for name, evs in tracks.items()],
    )
    return timeline.finalize()


def lower_script_to_ir(
    script: dict[str, Any],
    *,
    planner: Planner | None = None,
    fps: int = 30,
    source_id: str = "",
) -> VideoCompilerIR:
    """Compile a canonical script dict into the full staged IR.

    This is the deterministic, honest-seam entry point: no GPU, no API keys.
    Pass ``planner=MyLLMPlanner()`` to use a real LLM-driven narrative planner.
    """
    source = _to_source_script(script)
    planner = planner or DefaultPlanner()
    narrative, emotion, attention = planner.plan(source)
    scenes = _lower_to_scenes(source)
    shots = _lower_to_shots(scenes, source)
    timeline = _lower_to_timeline(shots, scenes, fps=fps)
    ir = VideoCompilerIR(
        source_id=source_id or source.title,
        narrative=narrative,
        emotion=emotion,
        attention=attention,
        scenes=scenes,
        shots=shots,
        timeline=timeline,
    )
    return ir.finalize()
