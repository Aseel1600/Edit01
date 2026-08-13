#!/usr/bin/env python3
"""Qwen-Image (text-to-image) on a RunPod GPU. Apache 2.0, ungated.

Qwen-Image is the strongest open model at LEGIBLE TEXT inside the image, which is
why it's worth the pod over the local FLUX.2-klein for text-heavy graphics.

VRAM:
  * A40 48GB  -> full bf16 fits; run as-is (no --offload). SIMPLEST + best quality.
  * 4090 24GB -> the bf16 transformer alone (~40GB) exceeds 24GB even with model
                 cpu-offload, so full bf16 will NOT fit. Use --offload only as a
                 first try; if it OOMs, switch to an fp8 build (see FP8 note below).

Usage:
    python qwen_gen.py "<prompt>" out.png [--w 1328 --h 1328 --steps 30 --cfg 4.0 --seed 0 --offload]

Native-ish sizes (Qwen-Image aspect presets): 1328x1328 (1:1), 1664x928 (16:9),
928x1664 (9:16), 1472x1140 (4:3). Pass --w/--h to match your card.

FP8 note (24GB path): install `optimum-quanto`, then before the pipe call:
    from optimum.quanto import quantize, qfloat8, freeze
    quantize(pipe.transformer, weights=qfloat8); freeze(pipe.transformer)
  keeps the transformer ~= 20GB and fits a 4090 with model cpu-offload.
"""
from __future__ import annotations

import argparse
import os
import time

os.environ.setdefault("HF_HOME", "/workspace/hf_cache")
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

import torch  # noqa: E402
from diffusers import DiffusionPipeline  # noqa: E402

MODEL_ID = "Qwen/Qwen-Image"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt")
    ap.add_argument("out")
    ap.add_argument("--w", type=int, default=1328)
    ap.add_argument("--h", type=int, default=1328)
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--cfg", type=float, default=4.0, help="true_cfg_scale (Qwen-Image)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--offload", action="store_true", help="enable_model_cpu_offload (24GB cards)")
    a = ap.parse_args()

    t = time.time()
    print(f"loading {MODEL_ID} ...")
    pipe = DiffusionPipeline.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16)
    if a.offload:
        pipe.enable_model_cpu_offload()
    else:
        pipe.to("cuda")
    print(f"loaded in {time.time() - t:.1f}s")

    t = time.time()
    print(f"generating {a.w}x{a.h} ({a.steps} steps, cfg {a.cfg}): {a.prompt!r}")
    image = pipe(
        prompt=a.prompt,
        negative_prompt=" ",
        width=a.w,
        height=a.h,
        num_inference_steps=a.steps,
        true_cfg_scale=a.cfg,
        generator=torch.Generator("cuda").manual_seed(a.seed),
    ).images[0]
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    image.save(a.out)
    print(f"generated in {time.time() - t:.1f}s -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
