"""Run the loopback-only OpenMontage runner service."""

from __future__ import annotations

import argparse
import os


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="openmontage-runner")
    parser.add_argument("--port", type=int, default=int(os.environ.get("OPENMONTAGE_RUNNER_PORT", "4751")))
    args = parser.parse_args(argv)
    import uvicorn
    uvicorn.run("runner.server:app", host="127.0.0.1", port=args.port, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
