#!/usr/bin/env python3
"""CLI driver for running Wan / HunyuanVideo local generation on a rented GPU pod.

Thin wrapper around the existing tools/video/wan_video.py and
tools/video/hunyuan_video.py tool classes -- same code path as local
generation, just invoked directly instead of through the tool registry.

Examples:
    python3 runpod/render.py wan --variant wan2.1-14b --prompt "a lone fishing boat drifting in fog" \\
        --out /workspace/out/boat.mp4

    python3 runpod/render.py hunyuan --variant hunyuan-1.5 --prompt "candle flame in a dark stone room" \\
        --width 1280 --height 720 --steps 40 --out /workspace/out/candle.mp4

    python3 runpod/render.py wan --variant wan2.1-14b --operation image_to_video \\
        --prompt "waves crash against the cliff" --ref /workspace/seed.png --out /workspace/out/clip.mp4

If a job OOMs on Wan-14B, retry with --offload-mode sequential (slower, lower
peak VRAM) before giving up and dropping to wan2.1-1.3b.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.video.hunyuan_video import HunyuanVideo
from tools.video.wan_video import WanVideo

TOOLS = {"wan": WanVideo, "hunyuan": HunyuanVideo}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("model", choices=sorted(TOOLS), help="which local model to run")
    parser.add_argument("--variant", required=True, help="e.g. wan2.1-14b, wan2.1-1.3b, hunyuan-1.5, hunyuan-1.5-distilled")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--operation", default="text_to_video", choices=["text_to_video", "image_to_video"])
    parser.add_argument("--ref", dest="reference_image_path", default=None, help="reference image path for image_to_video")
    parser.add_argument("--width", type=int, default=None)
    parser.add_argument("--height", type=int, default=None)
    parser.add_argument("--frames", type=int, default=None, dest="num_frames")
    parser.add_argument("--steps", type=int, default=None, dest="num_inference_steps")
    parser.add_argument("--offload-mode", default="model", choices=["model", "sequential"],
                         help="'sequential' uses less peak VRAM but is much slower; try this if Wan-14B OOMs")
    parser.add_argument("--no-offload", action="store_true", help="disable CPU offload entirely (needs the most VRAM, fastest)")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--out", required=True, dest="output_path")
    args = parser.parse_args()

    inputs = {
        "prompt": args.prompt,
        "operation": args.operation,
        "model_variant": args.variant,
        "enable_model_offload": not args.no_offload,
        "offload_mode": args.offload_mode,
        "output_path": args.output_path,
        "seed": args.seed,
    }
    if args.reference_image_path:
        inputs["reference_image_path"] = args.reference_image_path
    if args.width:
        inputs["width"] = args.width
    if args.height:
        inputs["height"] = args.height
    if args.num_frames:
        inputs["num_frames"] = args.num_frames
    if args.num_inference_steps:
        inputs["num_inference_steps"] = args.num_inference_steps
    inputs = {k: v for k, v in inputs.items() if v is not None}

    tool = TOOLS[args.model]()
    print(f"Running {args.model} ({args.variant}, {args.operation})...")
    start = time.time()
    result = tool.execute(inputs)
    elapsed = time.time() - start

    if not result.success:
        print(f"FAILED after {elapsed:.1f}s: {result.error}", file=sys.stderr)
        return 1

    print(f"Done in {elapsed:.1f}s -> {result.data['output']}")
    print(f"  {result.data['width']}x{result.data['height']}, {result.data['num_frames']} frames @ {result.data['fps']}fps "
          f"({result.data['duration_seconds']}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
