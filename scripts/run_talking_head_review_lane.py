#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from lib.talking_head_review_lane import run_talking_head_review_lane


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the talking-head review baseline lane")
    parser.add_argument("input", help="Path to local source video")
    parser.add_argument("--project-name", help="Project folder name under projects/")
    parser.add_argument("--clip-start", type=float, help="Optional manual clip start in seconds")
    parser.add_argument("--clip-end", type=float, help="Optional manual clip end in seconds")
    parser.add_argument("--subtitle-y-from-top", type=float, default=0.76, help="Subtitle anchor as fraction from top (default: 0.76)")
    args = parser.parse_args()

    project_repo = Path(__file__).resolve().parent.parent
    source = Path(args.input)
    if not source.exists():
        raise SystemExit(f"Input file not found: {source}")
    if (args.clip_start is None) ^ (args.clip_end is None):
        raise SystemExit("Provide both --clip-start and --clip-end together, or neither")

    summary = run_talking_head_review_lane(
        project_repo=project_repo,
        source_path=source,
        project_name=args.project_name,
        clip_start=args.clip_start,
        clip_end=args.clip_end,
        subtitle_y_from_top=args.subtitle_y_from_top,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
