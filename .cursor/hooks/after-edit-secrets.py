#!/usr/bin/env python3
"""Warn on obvious secrets in files just edited."""
from __future__ import annotations

import json
import os
import re
import sys

PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]{12,}['\"]"),
]

SKIP_NAMES = {
    "after-edit-secrets.py",
    "before-shell.py",
    "pre-compact.py",
    "hooks.sh",
}


def load_input() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def file_path(data: dict) -> str:
    for key in ("file_path", "path", "file", "uri"):
        value = data.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def main() -> None:
    data = load_input()
    path = file_path(data)
    if not path or not os.path.isfile(path):
        print(json.dumps({}))
        return
    if os.path.basename(path) in SKIP_NAMES:
        print(json.dumps({}))
        return
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            text = handle.read(200_000)
    except OSError:
        print(json.dumps({}))
        return
    hits = [pattern.pattern for pattern in PATTERNS if pattern.search(text)]
    if not hits:
        print(json.dumps({}))
        return
    print(
        json.dumps(
            {
                "additional_context": (
                    f"Secret-hygiene hook flagged {path}. "
                    "Do not commit secrets. Move credentials to an untracked secret file."
                )
            }
        )
    )


if __name__ == "__main__":
    main()
