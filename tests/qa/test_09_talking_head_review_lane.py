import json
from pathlib import Path

from lib.talking_head_review_lane import CandidateWindow, run_talking_head_review_lane, select_opening_candidate


def test_select_opening_candidate_prefers_strong_opening_window() -> None:
    segments = [
        {"start": 0.0, "end": 1.0, "text": "Welcome back."},
        {"start": 1.0, "end": 2.2, "text": "Trump was right."},
        {"start": 2.2, "end": 3.2, "text": "Media said he was lying."},
        {"start": 3.2, "end": 4.5, "text": "Media said he was wrong."},
        {"start": 4.5, "end": 8.0, "text": "And now Iran has confirmed what he said about the strait being open."},
        {"start": 8.0, "end": 10.0, "text": "Let me explain why this matters."},
        {"start": 10.0, "end": 16.0, "text": "This is the best shot right now."},
        {"start": 16.0, "end": 20.0, "text": "We finally have proof."},
    ]

    candidate = select_opening_candidate(segments, search_limit_seconds=30.0)

    assert candidate.start_seconds == 0.0
    assert candidate.end_seconds >= 16.0
    assert "Media said he was lying" in candidate.text
    assert candidate.duration_seconds >= 14.0


def test_review_lane_transcribes_selects_and_exports_square_subtitled_summary(monkeypatch, tmp_path: Path) -> None:
    import lib.talking_head_review_lane as lane

    source = tmp_path / "source.mp4"
    source.touch()
    segments = [{"start": 4.0, "end": 22.0, "text": "This is the strong opening proof."}]
    candidate = CandidateWindow("opening_candidate", 4.0, 22.0, segments[0]["text"], 7)
    calls: list[tuple] = []

    monkeypatch.setattr(lane, "load_env", lambda project_repo: None)
    monkeypatch.setattr(lane, "discover_provider_menu", lambda project_repo: {"video_generation": {"configured": 1, "total": 2}})
    monkeypatch.setattr(lane, "transcribe_if_needed", lambda source_path, artifacts_dir: {"success": True, "error": None, "data": {"segments": segments}})
    monkeypatch.setattr(lane, "select_opening_candidate", lambda selected_segments: candidate)
    monkeypatch.setattr(lane, "cut_clip", lambda source_path, out_path, start, end: calls.append(("cut", source_path, out_path, start, end)))
    monkeypatch.setattr(lane, "make_square", lambda source_path, out_path: calls.append(("square", source_path, out_path)))
    monkeypatch.setattr(lane, "write_srt_for_window", lambda selected_segments, start, end, out_path: (calls.append(("srt", selected_segments, start, end, out_path)) or 1))
    monkeypatch.setattr(lane, "burn_subtitles", lambda square_path, srt_path, out_path, subtitle_y_from_top: (calls.append(("burn", square_path, srt_path, out_path, subtitle_y_from_top)) or 259))

    summary = run_talking_head_review_lane(tmp_path, source, project_name="review-proof")

    assert summary["selected_candidate"] == {
        "start_seconds": 4.0,
        "end_seconds": 22.0,
        "duration_seconds": 18.0,
        "text": "This is the strong opening proof.",
        "score": 7,
    }
    assert summary["template"] == {
        "aspect_ratio": "1:1",
        "resolution": "1080x1080",
        "burn_subtitles": True,
        "subtitle_y_from_top": 0.76,
        "margin_v": 259,
        "large_hook_overlay": False,
    }
    assert summary["subtitle_segments"] == 1
    assert summary["provider_menu_summary"] == {"video_generation": {"configured": 1, "total": 2}}
    assert [call[0] for call in calls] == ["cut", "square", "srt", "burn"]
    assert calls[0][3:] == (4.0, 22.0)
    assert calls[2][1:4] == (segments, 4.0, 22.0)
    assert calls[3][-1] == 0.76
    written_summary = tmp_path / "projects" / "review-proof" / "artifacts" / "review-lane-summary.json"
    assert json.loads(written_summary.read_text(encoding="utf-8")) == summary
