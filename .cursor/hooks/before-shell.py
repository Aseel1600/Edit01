#!/usr/bin/env python3
"""Gate destructive shell commands without a naive string blacklist."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

DENY_MSG = {
    "permission": "deny",
    "user_message": "A Cursor hook blocked this command.",
    "agent_message": "",
}
ASK_MSG = {
    "permission": "ask",
    "user_message": "Review this command before continuing.",
    "agent_message": "",
}


def allow() -> None:
    print(json.dumps({"permission": "allow"}))
    sys.exit(0)


def ask(agent: str, user: str | None = None) -> None:
    payload = dict(ASK_MSG)
    payload["agent_message"] = agent
    if user:
        payload["user_message"] = user
    print(json.dumps(payload))
    sys.exit(0)


def deny(agent: str, user: str | None = None) -> None:
    payload = dict(DENY_MSG)
    payload["agent_message"] = agent
    if user:
        payload["user_message"] = user
    print(json.dumps(payload))
    sys.exit(0)


def read_command() -> str:
    raw = sys.stdin.read()
    if not raw.strip():
        return ""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return raw.strip()
    for key in ("command", "cmd", "shell_command"):
        value = data.get(key)
        if isinstance(value, str):
            return value
    return ""


def normalize(command: str) -> str:
    return " ".join(command.strip().split())


def is_force_push(command: str) -> bool:
    if not re.search(r"\bgit\b", command):
        return False
    if re.search(r"\bpush\b", command) and re.search(
        r"(--force-with-lease|--force|-f\b)", command
    ):
        return True
    return False


def is_hard_reset(command: str) -> bool:
    return bool(re.search(r"\bgit\b.*\breset\b.*--hard\b", command)) or bool(
        re.search(r"\bgit\b.*\bcheckout\b.*--force\b", command)
    )


def is_history_rewrite(command: str) -> bool:
    return bool(
        re.search(r"\bgit\b.*\bfilter-(branch|repo)\b", command)
        or re.search(r"\bgit\b.*\brebase\b.*\b-i\b", command)
        or re.search(r"\bgit\b.*\bpush\b.*\b--mirror\b", command)
    )


def is_sql_destructive(command: str) -> bool:
    upper = command.upper()
    return bool(
        re.search(r"\bDROP\s+(DATABASE|SCHEMA|TABLE)\b", upper)
        or re.search(r"\bTRUNCATE\b", upper)
    )


def rm_rf_targets(command: str) -> list[str]:
    if not re.search(r"\brm\b", command) or not re.search(r"-[^\s]*r[^\s]*f|-[^\s]*f[^\s]*r", command):
        return []
    tokens = command.split()
    out: list[str] = []
    started = False
    for token in tokens:
        if token in {"sudo", "command"}:
            continue
        if token == "rm" or token.startswith("rm"):
            started = True
            continue
        if not started:
            continue
        if token.startswith("-"):
            continue
        out.append(token)
    return out


def dangerous_rm_target(path: str) -> bool:
    expanded = os.path.expanduser(path)
    stripped = expanded.rstrip("/")
    if stripped in {"", ".", ".."}:
        return True
    if stripped in {"/", "/Users", "/home", "/System", "/Library", "/opt", "/usr", "/bin", "/sbin", "/etc", "/var", "/private"}:
        return True
    home = os.path.expanduser("~").rstrip("/")
    if stripped == home:
        return True
    if stripped.startswith("/volume1") and stripped.count("/") <= 2:
        return True
    return False


def git_diff_check_cached() -> str | None:
    try:
        proc = subprocess.run(
            ["git", "diff", "--cached", "--check"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if proc.returncode == 0:
        return None
    return (proc.stdout or proc.stderr or "git diff --check failed").strip()


def main() -> None:
    command = normalize(read_command())
    if not command:
        allow()

    if is_force_push(command) or is_history_rewrite(command):
        deny(
            "Force-push or shared-history rewrite requires Level 3 human approval.",
            "This Git command can rewrite shared history. It was blocked.",
        )

    if is_hard_reset(command):
        ask(
            "git reset --hard / force checkout discards work. Confirm before running.",
        )

    if is_sql_destructive(command):
        ask("DROP/TRUNCATE can destroy data. Confirm before running.")

    for target in rm_rf_targets(command):
        if dangerous_rm_target(target):
            deny(
                f"Refusing rm -rf of high-risk path: {target}",
                f"Blocked rm -rf targeting {target}.",
            )

    if re.search(r"\bgit\b", command) and re.search(r"\bcommit\b", command):
        problem = git_diff_check_cached()
        if problem:
            ask(
                "git diff --cached --check failed. Fix whitespace/conflict markers before commit.\n"
                + problem[:2000]
            )

    allow()


if __name__ == "__main__":
    main()
