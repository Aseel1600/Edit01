#!/usr/bin/env python3
"""Comfy Cloud adapter E2E demo.

Exercises every bundled ComfyUI workflow against the Comfy Cloud backend and
assembles the results into one finished video, so the whole adapter surface is
proven end to end rather than tool by tool:

    flux2-txt2img    -> comfyui_image   (FLUX 2)
    wan22-t2v-4step  -> comfyui_video   (WAN 2.2 text-to-video)
    wan22-i2v-4step  -> comfyui_video   (WAN 2.2 image-to-video, fed the
                                         FLUX still — also covers upload_image)
    ace-step-1-t2a   -> comfyui_music   (ACE-Step)

Default mode is a no-cost dry run that verifies discovery, backend resolution,
model availability, and cost estimates without submitting anything. ``--live``
runs the four real generations, which consume Comfy Cloud GPU credits.

    python scripts/comfy_cloud_e2e.py            # dry run, free
    python scripts/comfy_cloud_e2e.py --live     # real generations, costs money

Requires COMFY_CLOUD_API_KEY in .env. See docs/PROVIDERS.md.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.env_loader import load_env  # noqa: E402

load_env(ROOT)

from lib.checkpoint import init_project  # noqa: E402
from tools._comfyui.client import resolve_backend  # noqa: E402
from tools.tool_registry import registry  # noqa: E402


DEFAULT_PROJECT = "comfy-cloud-demo"

SUBJECT = "a lone lighthouse on a black basalt cliff at dusk, fog over the water"

STEPS: list[dict[str, Any]] = [
    {
        "key": "image",
        "tool": "comfyui_image",
        "workflow": "flux2-txt2img",
        "label": "FLUX 2 still",
        "rel": "assets/images/lighthouse.png",
        "inputs": {
            "prompt": (
                "A lone lighthouse on a black basalt cliff at dusk, low fog "
                "rolling over the water, single warm beam cutting the blue "
                "haze, cinematic wide shot, photographic"
            ),
            "width": 1280,
            "height": 720,
            "steps": 20,
            "seed": 7,
        },
    },
    {
        "key": "t2v",
        "tool": "comfyui_video",
        "workflow": "wan22-t2v-4step",
        "label": "WAN 2.2 text-to-video",
        "rel": "assets/video/t2v_lighthouse.mp4",
        "inputs": {
            "operation": "text_to_video",
            "prompt": (
                "Slow aerial push toward a lighthouse on a black cliff at "
                "dusk, fog drifting across the water, beam sweeping through "
                "haze, cinematic"
            ),
            "width": 832,
            "height": 480,
            "num_frames": 81,
            "seed": 11,
            "timeout_seconds": 2400,
        },
    },
    {
        "key": "i2v",
        "tool": "comfyui_video",
        "workflow": "wan22-i2v-4step",
        "label": "WAN 2.2 image-to-video",
        "rel": "assets/video/i2v_lighthouse.mp4",
        # Consumes the FLUX still produced by the first step.
        "reference_from": "image",
        "inputs": {
            "operation": "image_to_video",
            "prompt": (
                "The fog drifts slowly across the water and the lighthouse "
                "beam sweeps through the haze, gentle camera drift"
            ),
            "width": 640,
            "height": 640,
            "num_frames": 81,
            "seed": 13,
            "timeout_seconds": 2400,
        },
    },
    {
        "key": "music",
        "tool": "comfyui_music",
        "workflow": "ace-step-1-t2a",
        "label": "ACE-Step score",
        "rel": "assets/music/fog_theme.mp3",
        "inputs": {
            "prompt": (
                "slow cinematic ambient, low strings, distant foghorn, sparse "
                "piano, melancholy maritime atmosphere, instrumental"
            ),
            "duration_seconds": 20,
            "steps": 50,
            "seed": 23,
            "timeout_seconds": 1800,
        },
    },
]


def preflight(backend: str) -> int:
    """Report discovery, backend resolution, and readiness. Spends nothing."""
    print(f"\nBackend resolved: {backend}")
    if backend != "cloud":
        print(
            "  note: no Comfy Cloud backend selected. Set COMFY_CLOUD_API_KEY "
            "and COMFYUI_BACKEND=cloud, or pass --backend cloud."
        )

    failures = 0
    print("\nTool readiness")
    for tool_name in ("comfyui_image", "comfyui_video", "comfyui_music"):
        tool = registry._tools.get(tool_name)
        if tool is None:
            print(f"  {tool_name:15} NOT DISCOVERED")
            failures += 1
            continue
        # Report readiness for the backend this run will actually use.
        # tool.get_status() answers for the tool's ambient default, which
        # can differ when COMFYUI_BACKEND is set — printing both side by
        # side would read as a contradiction.
        client = tool._client_for(backend)
        cost = tool.estimate_cost({"backend": backend})
        ok = client.is_available()
        print(
            f"  {tool_name:15} backend={client.backend:5} "
            f"reachable={ok!s:5} est=${cost:.2f}"
        )
        if not ok:
            print(f"    {client.unavailable_reason().splitlines()[0]}")
            failures += 1
    return failures


def run_step(step: dict[str, Any], project_dir: Path, backend: str) -> dict[str, Any]:
    """Execute one generation step and return a manifest entry."""
    tool = registry._tools[step["tool"]]
    out = project_dir / step["rel"]
    out.parent.mkdir(parents=True, exist_ok=True)

    inputs = dict(step["inputs"])
    inputs["backend"] = backend
    inputs["output_path"] = str(out)
    if step.get("reference_from"):
        ref = project_dir / next(
            s["rel"] for s in STEPS if s["key"] == step["reference_from"]
        )
        if not ref.exists():
            raise RuntimeError(
                f"{step['key']} needs {ref}, which the earlier step did not produce."
            )
        inputs["reference_image_path"] = str(ref)

    print(f"\n=== {step['label']}  ({step['workflow']})")
    started = datetime.now(timezone.utc)
    result = tool.execute(inputs)
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()

    if not result.success:
        print(f"  FAILED: {result.error}")
        return {
            "step": step["key"],
            "workflow": step["workflow"],
            "tool": step["tool"],
            "success": False,
            "error": result.error,
            "elapsed_seconds": round(elapsed, 1),
        }

    size = out.stat().st_size if out.exists() else 0
    print(f"  ok  {out}  ({size:,} bytes, {elapsed:.0f}s)")
    return {
        "step": step["key"],
        "workflow": step["workflow"],
        "tool": step["tool"],
        "success": True,
        "output": str(out.relative_to(project_dir)),
        "bytes": size,
        "elapsed_seconds": round(elapsed, 1),
        "model": result.data.get("model"),
        "backend": result.data.get("backend", backend),
    }


def compose(project_dir: Path) -> dict[str, Any]:
    """Concatenate both clips and lay the generated score underneath.

    Uses FFmpeg directly: the point of this script is the ComfyUI Cloud
    adapter, not the composition runtimes, and FFmpeg is always available.
    """
    t2v = project_dir / "assets/video/t2v_lighthouse.mp4"
    i2v = project_dir / "assets/video/i2v_lighthouse.mp4"
    music = project_dir / "assets/music/fog_theme.mp3"
    final = project_dir / "renders/final.mp4"
    final.parent.mkdir(parents=True, exist_ok=True)

    missing = [p.name for p in (t2v, i2v, music) if not p.exists()]
    if missing:
        return {"success": False, "error": f"missing inputs: {', '.join(missing)}"}

    # Normalize both clips to a common size/fps, concat, then mix the score
    # in and fade it out over the tail.
    cmd = [
        "ffmpeg", "-v", "error", "-y",
        "-i", str(t2v),
        "-i", str(i2v),
        "-i", str(music),
        "-filter_complex",
        (
            "[0:v]scale=832:480:force_original_aspect_ratio=decrease,"
            "pad=832:480:(ow-iw)/2:(oh-ih)/2,fps=16,setsar=1[v0];"
            "[1:v]scale=832:480:force_original_aspect_ratio=decrease,"
            "pad=832:480:(ow-iw)/2:(oh-ih)/2,fps=16,setsar=1[v1];"
            "[v0][v1]concat=n=2:v=1:a=0[v];"
            "[2:a]atrim=0:10.125,afade=t=out:st=8.1:d=2[a]"
        ),
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
        "-c:a", "aac", "-shortest",
        str(final),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return {"success": False, "error": proc.stderr.strip()[:500]}
    return {
        "success": True,
        "output": str(final.relative_to(project_dir)),
        "bytes": final.stat().st_size,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument(
        "--backend", default="cloud", choices=["cloud", "local", "auto"]
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run the real generations. Consumes Comfy Cloud credits.",
    )
    args = parser.parse_args()

    registry.discover()
    backend = resolve_backend(args.backend)

    failures = preflight(backend)
    if not args.live:
        print(
            "\nDry run complete — nothing was submitted and no credits were "
            "spent.\nRe-run with --live to generate."
        )
        return 1 if failures else 0
    if failures:
        print("\nPreflight failed; not spending credits. Fix the above first.")
        return 1

    project_dir = Path(
        init_project(
            args.project,
            title="Comfy Cloud Adapter Demo",
            pipeline_type="animated-explainer",
        )
    )

    manifest = [run_step(step, project_dir, backend) for step in STEPS]

    print("\n=== Compose")
    render = compose(project_dir)
    print(f"  {'ok  ' + render['output'] if render['success'] else render['error']}")

    summary = {
        "project": args.project,
        "backend": backend,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "steps": manifest,
        "render": render,
    }
    report = project_dir / "artifacts" / "comfy_cloud_e2e.json"
    report.write_text(json.dumps(summary, indent=2))
    print(f"\nReport: {report}")

    failed = [m for m in manifest if not m["success"]]
    print(
        f"\n{len(manifest) - len(failed)}/{len(manifest)} workflows succeeded"
        + (f" — failed: {', '.join(m['step'] for m in failed)}" if failed else "")
    )
    return 1 if failed or not render["success"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
