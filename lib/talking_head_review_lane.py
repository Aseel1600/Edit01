from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lib.env_loader import load_env
from tools.analysis.transcriber import Transcriber


@dataclass
class CandidateWindow:
    name: str
    start_seconds: float
    end_seconds: float
    text: str
    score: int

    @property
    def duration_seconds(self) -> float:
        return round(self.end_seconds - self.start_seconds, 2)


HOOK_PATTERNS = [
    re.compile(r"\b(scandal|lifetime|uncovered|happening|proof|truth|massive|huge|arrests?|lying|wrong)\b", re.I),
    re.compile(r"\b(trump|biden|obama|iran|russia|judge|media|fbi|investigation|grand jury|maga)\b", re.I),
    re.compile(r"\b(here'?s why|what happened|this means|because|let me explain|best shot right now)\b", re.I),
]


def slugify(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    return cleaned or "talking-head-review"


def ensure_project_dirs(project_root: Path) -> None:
    for rel in [
        "artifacts",
        "assets",
        "assets/video",
        "assets/audio",
        "assets/images",
        "renders",
    ]:
        (project_root / rel).mkdir(parents=True, exist_ok=True)


def discover_provider_menu(project_repo: Path) -> dict[str, Any]:
    from tools.tool_registry import registry

    load_env(project_repo)
    registry.discover()
    return registry.provider_menu()


def transcribe_if_needed(source_path: Path, artifacts_dir: Path) -> dict[str, Any]:
    out = artifacts_dir / "transcriber-output.json"
    if out.exists():
        return json.loads(out.read_text())
    result = Transcriber().execute({"input_path": str(source_path)})
    payload = {"success": result.success, "error": result.error, "data": result.data}
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def _segment_score(text: str) -> int:
    score = 0
    for rx in HOOK_PATTERNS:
        score += len(rx.findall(text))
    words = len(text.split())
    if 10 <= words <= 55:
        score += 2
    elif 6 <= words <= 65:
        score += 1
    if text.endswith(("?", "!", ".")):
        score += 1
    return score


def select_opening_candidate(segments: list[dict[str, Any]], search_limit_seconds: float = 120.0) -> CandidateWindow:
    opening = [s for s in segments if s.get("start", 0) <= search_limit_seconds and s.get("text", "").strip()]
    if not opening:
        raise ValueError("No transcript segments available for candidate selection")

    best: CandidateWindow | None = None
    for start_idx in range(len(opening)):
        start_time = opening[start_idx]["start"]
        texts: list[str] = []
        total_score = 0
        end_time = start_time
        for end_idx in range(start_idx, len(opening)):
            seg = opening[end_idx]
            if seg["start"] - end_time > 3.0 and texts:
                break
            texts.append(seg["text"].strip())
            end_time = seg["end"]
            duration = end_time - start_time
            total_score += _segment_score(seg["text"].strip())
            if duration < 14:
                continue
            coherence = 2 if 18 <= duration <= 35 else (1 if duration <= 50 else 0)
            candidate = CandidateWindow(
                name="opening_candidate",
                start_seconds=round(start_time, 2),
                end_seconds=round(end_time, 2),
                text=" ".join(texts),
                score=total_score + coherence,
            )
            if best is None or candidate.score > best.score:
                best = candidate
            if duration >= 35:
                break

    if best is None:
        first = opening[0]
        return CandidateWindow(
            name="opening_candidate",
            start_seconds=round(first["start"], 2),
            end_seconds=round(min(first["end"] + 20.0, opening[-1]["end"]), 2),
            text=first["text"].strip(),
            score=0,
        )
    return best


def write_srt_for_window(segments: list[dict[str, Any]], clip_start: float, clip_end: float, out_path: Path) -> int:
    selected: list[tuple[float, float, str]] = []
    for seg in segments:
        if seg["end"] <= clip_start or seg["start"] >= clip_end:
            continue
        start = max(seg["start"], clip_start) - clip_start
        end = min(seg["end"], clip_end) - clip_start
        text = seg["text"].strip()
        if text:
            selected.append((start, end, text))

    def fmt(ts: float) -> str:
        ms = round(ts * 1000)
        h = ms // 3600000
        ms %= 3600000
        m = ms // 60000
        ms %= 60000
        s = ms // 1000
        ms %= 1000
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    lines: list[str] = []
    for i, (start, end, text) in enumerate(selected, 1):
        lines += [str(i), f"{fmt(start)} --> {fmt(end)}", text, ""]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return len(selected)


def ffmpeg_run(args: list[str]) -> None:
    subprocess.run(args, check=True)


def cut_clip(source_path: Path, out_path: Path, start: float, end: float) -> None:
    ffmpeg_run([
        "ffmpeg", "-y", "-ss", str(start), "-to", str(end), "-i", str(source_path),
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k", str(out_path),
    ])


def make_square(source_path: Path, out_path: Path, crop_x: int = 420) -> None:
    ffmpeg_run([
        "ffmpeg", "-y", "-i", str(source_path),
        "-vf", f"crop=1080:1080:{crop_x}:0",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "copy", str(out_path),
    ])


def burn_subtitles(square_path: Path, srt_path: Path, out_path: Path, subtitle_y_from_top: float = 0.76) -> int:
    margin_v = round(1080 * (1.0 - subtitle_y_from_top))
    vf = (
        f"subtitles='{srt_path.as_posix()}':"
        "force_style='FontName=Arial,FontSize=22,PrimaryColour=&H00FFFFFF,"
        f"OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,MarginV={margin_v},Alignment=2'"
    )
    ffmpeg_run([
        "ffmpeg", "-y", "-i", str(square_path),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "copy", str(out_path),
    ])
    return margin_v


def run_talking_head_review_lane(project_repo: Path, source_path: Path, project_name: str | None = None,
                                 clip_start: float | None = None, clip_end: float | None = None,
                                 subtitle_y_from_top: float = 0.76) -> dict[str, Any]:
    load_env(project_repo)
    if project_name is None:
        project_name = slugify(source_path.stem)
    project_root = project_repo / "projects" / project_name
    ensure_project_dirs(project_root)

    provider_menu = discover_provider_menu(project_repo)
    transcribed = transcribe_if_needed(source_path, project_root / "artifacts")
    if not transcribed.get("success"):
        raise RuntimeError(transcribed.get("error") or "Transcription failed")
    segments = transcribed["data"]["segments"]

    candidate = (
        CandidateWindow("manual", clip_start, clip_end, "manual window", 0)
        if clip_start is not None and clip_end is not None
        else select_opening_candidate(segments)
    )

    raw_path = project_root / "assets" / "video" / "opening-proof.mp4"
    square_path = project_root / "assets" / "video" / "opening-proof-square.mp4"
    srt_path = project_root / "assets" / "opening-proof.srt"
    baseline_path = project_root / "assets" / "video" / "opening-proof-square-subtitled-baseline.mp4"

    cut_clip(source_path, raw_path, candidate.start_seconds, candidate.end_seconds)
    make_square(raw_path, square_path)
    subtitle_segments = write_srt_for_window(segments, candidate.start_seconds, candidate.end_seconds, srt_path)
    margin_v = burn_subtitles(square_path, srt_path, baseline_path, subtitle_y_from_top=subtitle_y_from_top)

    summary = {
        "project": project_name,
        "source_path": str(source_path),
        "selected_candidate": {
            "start_seconds": candidate.start_seconds,
            "end_seconds": candidate.end_seconds,
            "duration_seconds": candidate.duration_seconds,
            "text": candidate.text,
            "score": candidate.score,
        },
        "template": {
            "aspect_ratio": "1:1",
            "resolution": "1080x1080",
            "burn_subtitles": True,
            "subtitle_y_from_top": subtitle_y_from_top,
            "margin_v": margin_v,
            "large_hook_overlay": False,
        },
        "outputs": {
            "raw": str(raw_path),
            "square": str(square_path),
            "srt": str(srt_path),
            "baseline": str(baseline_path),
        },
        "subtitle_segments": subtitle_segments,
        "provider_menu_summary": {
            key: {
                "configured": value.get("configured"),
                "total": value.get("total"),
            }
            for key, value in provider_menu.items()
        },
    }
    (project_root / "artifacts" / "review-lane-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
