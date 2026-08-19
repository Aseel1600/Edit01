#!/usr/bin/env python3
"""Before context compaction: require HANDOFF and capture mechanical Git state."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone


def git(*args: str) -> str:
    try:
        proc = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return ""
    return (proc.stdout or "").strip()


def main() -> None:
    handoff = os.path.join("docs", "continuity", "HANDOFF.md")
    missing = not os.path.isfile(handoff)
    status = git("status", "--short")
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    head = git("rev-parse", "--short", "HEAD")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    os.makedirs(os.path.join("docs", "continuity"), exist_ok=True)
    state_path = os.path.join("docs", "continuity", ".last-git-state.txt")
    try:
        with open(state_path, "w", encoding="utf-8") as handle:
            handle.write(f"captured_at: {stamp}\n")
            handle.write(f"branch: {branch or 'unknown'}\n")
            handle.write(f"head: {head or 'unknown'}\n")
            handle.write("status:\n")
            handle.write((status or "(clean)") + "\n")
    except OSError:
        pass

    notes = [
        f"preCompact git: branch={branch or 'unknown'} head={head or 'unknown'}",
        f"status: {status or 'clean'}",
    ]
    if missing:
        notes.append(
            "HANDOFF.md is missing. Update docs/continuity/HANDOFF.md before this session continues."
        )

    print(json.dumps({"additional_context": "\n".join(notes)}))


if __name__ == "__main__":
    main()
