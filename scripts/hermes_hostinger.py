#!/usr/bin/env python3
"""CLI for the Hermes Hostinger pipeline: preflight, serve, youtube, status."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SERVICE_DIR = REPO_ROOT / "services" / "hermes-api"


def _dump(result) -> int:
    payload = {
        "success": result.success,
        "error": result.error,
        "data": result.data,
    }
    print(json.dumps(payload, indent=2))
    return 0 if result.success else 1


def cmd_preflight(_: argparse.Namespace) -> int:
    from tools.llm.lmstudio import LMStudio
    from tools.publishers.hostinger_deploy import HostingerDeploy
    from tools.publishers.youtube_upload import YouTubeUpload

    def slim(res):
        return {"success": res.success, "error": res.error, "data": res.data}

    print(
        json.dumps(
            {
                "lmstudio": slim(LMStudio().execute({"action": "health"})),
                "hostinger": slim(HostingerDeploy().execute({"action": "status"})),
                "youtube": slim(YouTubeUpload().execute({"action": "status"})),
            },
            indent=2,
        )
    )
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    port = str(args.port)
    env = os.environ.copy()
    if not env.get("PUBLIC_DOMAIN"):
        env["PUBLIC_DOMAIN"] = "localhost"
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app:app",
        "--app-dir",
        str(SERVICE_DIR),
        "--host",
        args.host,
        "--port",
        port,
    ]
    print(f"Hermes API → http://{args.host}:{port}/health", file=sys.stderr)
    return subprocess.call(cmd, env=env)


def cmd_youtube(args: argparse.Namespace) -> int:
    from tools.publishers.youtube_upload import YouTubeUpload

    tool = YouTubeUpload()
    if args.status or not args.file:
        return _dump(tool.execute({"action": "status"}))
    return _dump(
        tool.execute(
            {
                "action": "upload",
                "video_path": args.file,
                "title": args.title or Path(args.file).stem,
                "description": args.description,
                "privacy": args.privacy,
                "dry_run": args.dry_run,
            }
        )
    )


def cmd_deploy(args: argparse.Namespace) -> int:
    from tools.publishers.hostinger_deploy import HostingerDeploy

    action = "deploy" if args.remote else "scaffold"
    return _dump(HostingerDeploy().execute({"action": action, "domain": args.domain}))


def main() -> int:
    parser = argparse.ArgumentParser(description="Hermes Hostinger operator CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("preflight", help="Probe LM Studio, Hostinger, YouTube")

    serve = sub.add_parser("serve", help="Run the Hermes API locally")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8080)

    yt = sub.add_parser("youtube", help="YouTube uploader")
    yt.add_argument("--file")
    yt.add_argument("--title", default="")
    yt.add_argument("--description", default="")
    yt.add_argument("--privacy", default="unlisted")
    yt.add_argument("--dry-run", action="store_true")
    yt.add_argument("--status", action="store_true")

    dep = sub.add_parser("deploy", help="Validate Hostinger compose / remote gate")
    dep.add_argument("--domain", default="hermestudios.com")
    dep.add_argument("--remote", action="store_true")

    args = parser.parse_args()
    if args.cmd == "preflight":
        return cmd_preflight(args)
    if args.cmd == "serve":
        return cmd_serve(args)
    if args.cmd == "youtube":
        return cmd_youtube(args)
    if args.cmd == "deploy":
        return cmd_deploy(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
