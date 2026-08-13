#!/usr/bin/env python3
"""Second NEW mixed batch of Stoic b-roll SEEDS with FLUX.2-klein (local, free).

10 horizontal (2752x1536) -> library/seeds/lf/hb00NN.png
10 vertical   (1536x2752) -> library/seeds/vert/vb0NNN.png

Fresh concepts, no candles/statues (pool saturated + candle->fire i2v trap). No people/modern/text.
Auto-numbers, resumable (skips existing). i2v afterwards with dispatch_i2v.py (pod+local).
"""
from __future__ import annotations
import sys, time, re, glob, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.base_tool import _load_dotenv
_load_dotenv()
import torch
from diffusers import Flux2KleinPipeline

VERT = Path(r"C:\OpenMontage\projects\the-quiet-stoic\library\seeds\vert")
HORIZ = Path(r"C:\OpenMontage\projects\the-quiet-stoic\library\seeds\lf")

TAIL = ("cinematic, moody, atmospheric, 35mm film grain, soft natural light, "
        "full frame edge-to-edge composition, no black bars, no letterbox, no border, "
        "no people, no text, no watermark")

HORIZ_PROMPTS = [
    f"A vast pine forest blanketed in morning fog seen from above, rolling misty treetops, {TAIL}",
    f"Weathered marble steps of an ancient temple descending to a still reflecting pool, {TAIL}",
    f"A lone stone watchtower on a grassy sea cliff under fast racing clouds, {TAIL}",
    f"Sunrise over a calm archipelago of misty islands, layered blue silhouettes, {TAIL}",
    f"An ancient paved Roman road cutting straight through an empty golden plain, {TAIL}",
    f"A dramatic mountain pass with a switchback trail under heavy low cloud, {TAIL}",
    f"Moonlight over a calm dark sea with a faint shimmering path of light, minimal, {TAIL}",
    f"A field of ancient standing megalith stones on a misty moor at dawn, {TAIL}",
    f"Rain clouds sweeping across a patchwork of green farmland hills, wide vista, {TAIL}",
    f"Empty snow-covered stone rooftops of an old deserted hamlet under soft grey winter sky, {TAIL}",
]

VERT_PROMPTS = [
    f"A towering sea stack rising from crashing surf under a pale sky, vertical, {TAIL}",
    f"A tall narrow waterfall in a lush green fern gorge, vertical framing, {TAIL}",
    f"A single shaft of light falling through a tall forest canopy to the mossy floor, {TAIL}",
    f"A tall ancient stone tower wrapped in ivy against a moody grey sky, {TAIL}",
    f"A vertical view up a spiral of worn stone stairs toward a bright opening, {TAIL}",
    f"A tall frozen cliff face streaked with pale blue ice, deep winter, {TAIL}",
    f"A lone tall pine on a rocky outcrop against drifting mist, vertical, {TAIL}",
    f"A tall fluted ancient temple column, cracked and weathered, low upward angle, {TAIL}",
    f"A vertical curtain of distant rain sweeping over dark layered mountains, {TAIL}",
    f"A tall wind-sculpted desert dune ridge at golden hour, steep vertical crop, {TAIL}",
]


def _next(dirp: Path, prefix: str) -> int:
    nums = [int(m.group(1)) for f in glob.glob(str(dirp / f"{prefix}*.png"))
            for m in [re.match(rf"{prefix}0*(\d+)\.png", os.path.basename(f))] if m]
    return (max(nums) + 1) if nums else 1


def main() -> int:
    VERT.mkdir(parents=True, exist_ok=True)
    HORIZ.mkdir(parents=True, exist_ok=True)
    print("Loading FLUX.2-klein-4B...", flush=True)
    t0 = time.time()
    pipe = Flux2KleinPipeline.from_pretrained("black-forest-labs/FLUX.2-klein-4B", torch_dtype=torch.bfloat16)
    pipe.enable_model_cpu_offload()
    print(f"MODEL_LOADED {time.time()-t0:.0f}s", flush=True)

    jobs = []
    hb = _next(HORIZ, "hb")
    for i, p in enumerate(HORIZ_PROMPTS):
        jobs.append((HORIZ / f"hb{hb+i:04d}.png", p, 2752, 1536))
    vb = _next(VERT, "vb")
    for i, p in enumerate(VERT_PROMPTS):
        jobs.append((VERT / f"vb{vb+i:04d}.png", p, 1536, 2752))

    print(f"PLAN horiz hb{hb:04d}..hb{hb+len(HORIZ_PROMPTS)-1:04d} | vert vb{vb:04d}..vb{vb+len(VERT_PROMPTS)-1:04d}", flush=True)
    done = 0
    for out, prompt, w, h in jobs:
        if out.exists() and out.stat().st_size > 1000:
            print(f"SKIP {out.name}", flush=True); done += 1; continue
        t = time.time()
        img = pipe(prompt=prompt, width=w, height=h, num_inference_steps=4, guidance_scale=1.0).images[0]
        img.save(out); done += 1
        print(f"SEED_DONE {out.name} {w}x{h} ({time.time()-t:.0f}s) [{done}/{len(jobs)}]", flush=True)
    print(f"BATCH_DONE {len(jobs)} seeds", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
