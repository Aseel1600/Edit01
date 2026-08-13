#!/usr/bin/env bash
# PostToolUse (Write|Edit) backstop for the no-ai-slop standing rule.
# If Claude just saved a file whose PATH looks like outgoing copy, inject a
# reminder to run it through the no-ai-slop skill before presenting it.
# Matches on the file_path only (not file contents), so a code file that merely
# mentions "email"/"draft" does NOT trigger. Silent for everything else.
set -euo pipefail

payload="$(cat)"
path="$(printf '%s' "$payload" | grep -oE '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1)"

if printf '%s' "$path" | grep -iqE '(email|draft|outreach|pitch|cold|listing|/copy/|_copy|ad[-_]copy)'; then
  printf '%s' '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"This file looks like outgoing copy. Per the no-ai-slop standing rule, edit it with the no-ai-slop skill before presenting it to the user."}}'
fi
exit 0
