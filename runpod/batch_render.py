#!/usr/bin/env python3
"""Model-persistent batch renderer for Wan 2.2-5B i2v.

Loads the pipeline ONCE, then renders every clip in a JSON manifest, so the
~5-min model load is amortised across the whole chunk instead of paid per clip
(the per-clip render.py path reloaded the 5B model every time). Same locked
recipe (camera-driven prompt + anti-hallucination negative + guidance 4.5) --
prompt/negative are imported from dispatch_i2v so there is one source of truth.

Manifest: [{"ref": "in.png", "out": "out.mp4", "width": W, "height": H}, ...]
Usage:
  python3 runpod/batch_render.py <manifest.json> --no-offload           # 48GB pod
  python3 runpod/batch_render.py <manifest.json> --offload-mode sequential  # 12GB local
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.video._shared import load_diffusers_pipeline, load_reference_image, WAN_VARIANTS, ToolResult
from runpod.dispatch_i2v import PROMPTS, NEGATIVE

VARIANT = "wan2.2-ti2v-5b"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--offload-mode", default="model", choices=["model", "sequential"])
    ap.add_argument("--no-offload", action="store_true")
    args = ap.parse_args()

    from diffusers.utils import export_to_video

    meta = WAN_VARIANTS[VARIANT]
    enable_offload = not args.no_offload
    guid = meta.get("guidance_scale")
    frames = meta["default_num_frames"]
    fps = meta["fps"]

    t0 = time.time()
    pipe = load_diffusers_pipeline(
        meta["i2v_pipeline_class"], meta["hf_i2v_id"],
        enable_offload, args.offload_mode, meta.get("vae_dtype"),
    )
    print(f"MODEL_LOADED {time.time() - t0:.1f}s", flush=True)

    items = json.load(open(args.manifest))
    ok = 0
    for it in items:
        w, h = it["width"], it["height"]
        out = it["out"]
        img = load_reference_image({"reference_image_path": it["ref"]}, w, h)
        if isinstance(img, ToolResult):
            print(f"CLIP_FAIL {out} bad-ref", flush=True)
            continue
        prompt = it.get("prompt") or PROMPTS["static"]  # per-category prompt from the manifest
        ts = time.time()
        try:
            result = pipe(
                prompt=prompt, negative_prompt=NEGATIVE, image=img,
                width=w, height=h, num_frames=frames,
                num_inference_steps=50, guidance_scale=guid,
            )
            Path(out).parent.mkdir(parents=True, exist_ok=True)
            export_to_video(result.frames[0], out, fps=fps)
            ok += 1
            print(f"CLIP_DONE {out} {time.time() - ts:.1f}s", flush=True)
        except Exception as e:  # keep the batch going if one clip fails
            print(f"CLIP_FAIL {out} {e}", flush=True)

    print(f"BATCH_DONE {ok}/{len(items)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
