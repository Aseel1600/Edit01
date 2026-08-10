#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 /path/to/video.mp4 [project-name]"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$SCRIPT_DIR"
INPUT_PATH="$1"
PROJECT_NAME="${2:-}"
PYTHON_BIN="$REPO_DIR/.venv/bin/python"

if [ ! -x "$PYTHON_BIN" ]; then
  echo "Missing OpenMontage venv python: $PYTHON_BIN"
  exit 1
fi

cd "$REPO_DIR"
if [ -n "$PROJECT_NAME" ]; then
  "$PYTHON_BIN" scripts/run_talking_head_review_lane.py "$INPUT_PATH" --project-name "$PROJECT_NAME"
else
  "$PYTHON_BIN" scripts/run_talking_head_review_lane.py "$INPUT_PATH"
fi
