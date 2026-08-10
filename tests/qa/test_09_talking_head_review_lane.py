from lib.talking_head_review_lane import select_opening_candidate


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
