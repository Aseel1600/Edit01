#!/usr/bin/env python3
"""Generate 20 fresh HORIZONTAL Stoic b-roll seeds with FLUX.2-klein (local, free).

Expands the exhausted horizontal pool so the figure-affected long-forms can rebuild at cap-3.
STRENGTHENED anti-figure prompt (no people, no statues/sculptures of people, no busts) after the
figure-sweep found baked-in people/statues. Pure landscape / architecture / nature only.

2752x1536 -> library/seeds/lf/hb00NN.png. Auto-numbers, resumable. i2v afterwards with dispatch_i2v.py.
"""
from __future__ import annotations
import sys, time, re, glob, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.base_tool import _load_dotenv
_load_dotenv()
import torch
from diffusers import Flux2KleinPipeline

HORIZ = Path(r"C:\OpenMontage\projects\the-quiet-stoic\library\seeds\lf")
W, H = 2752, 1536

TAIL = ("cinematic, moody, atmospheric, 35mm film grain, soft natural light, full frame edge-to-edge, "
        "no black bars, no letterbox, "
        "absolutely NO people, no human figures, NO statues or sculptures of people, no busts, "
        "no text, no watermark, an empty deserted place with no one present")

PROMPTS = [
    f"A vast frozen lake at dawn with cracked ice patterns stretching toward distant snowy peaks, {TAIL}",
    f"A dense misty bamboo forest with soft light filtering through tall stalks, silent, {TAIL}",
    f"A dramatic sea cave opening onto crashing grey waves with a shaft of light, {TAIL}",
    f"Terraced rice paddies on a misty mountainside at dawn, layered green curves, {TAIL}",
    f"An ancient stone aqueduct marching across a lush green valley under a moody sky, {TAIL}",
    f"A field of sunflowers bowed under a heavy grey overcast sky, wind moving the rows, {TAIL}",
    f"A deep narrow fjord with sheer dark cliffs and mirror-still black water, {TAIL}",
    f"A desert canyon river bend glowing deep orange at sunset, sweeping cliffs, {TAIL}",
    f"A misty tea plantation on rolling green hills at dawn, soft rows of shrubs, {TAIL}",
    f"A snow-laden evergreen forest under a heavy silent snowfall, muffled and still, {TAIL}",
    f"A vast field of red poppies under a dark stormy sky, wind rippling the blooms, {TAIL}",
    f"An old stone breakwater pier battered by heavy grey waves and sea spray, {TAIL}",
    f"A deep mountain gorge with fog suspended between towering rock walls, {TAIL}",
    f"An alpine wildflower meadow below jagged snow-capped peaks, clear cold light, {TAIL}",
    f"A lone weathered wooden barn in a golden wheat field under dark storm clouds, {TAIL}",
    f"A black volcanic sand beach with rolling mist and dark crashing surf, {TAIL}",
    f"A grove of ancient gnarled olive trees on a dry Mediterranean hillside, {TAIL}",
    f"A frozen waterfall in a blue-ice canyon under pale winter light, {TAIL}",
    f"Rolling fog drifting over a dark pine forest at dawn, aerial view, {TAIL}",
    f"A vast marshland at sunrise with drifting mist over still reflective water, {TAIL}",
]


def next_hb() -> int:
    nums = [int(m.group(1)) for f in glob.glob(str(HORIZ / "hb*.png"))
            for m in [re.match(r"hb0*(\d+)\.png", os.path.basename(f))] if m]
    return (max(nums) + 1) if nums else 1


def main() -> int:
    HORIZ.mkdir(parents=True, exist_ok=True)
    print("Loading FLUX.2-klein-4B...", flush=True)
    t0 = time.time()
    pipe = Flux2KleinPipeline.from_pretrained("black-forest-labs/FLUX.2-klein-4B", torch_dtype=torch.bfloat16)
    pipe.enable_model_cpu_offload()
    print(f"MODEL_LOADED {time.time()-t0:.0f}s", flush=True)
    start = next_hb()
    print(f"PLAN hb{start:04d}..hb{start+len(PROMPTS)-1:04d}", flush=True)
    for i, prompt in enumerate(PROMPTS):
        hb = f"hb{start+i:04d}"; out = HORIZ / f"{hb}.png"
        if out.exists() and out.stat().st_size > 1000:
            print(f"SKIP {hb}", flush=True); continue
        t = time.time()
        img = pipe(prompt=prompt, width=W, height=H, num_inference_steps=4, guidance_scale=1.0).images[0]
        img.save(out)
        print(f"SEED_DONE {hb} ({time.time()-t:.0f}s) [{i+1}/{len(PROMPTS)}]", flush=True)
    print(f"BATCH_DONE {len(PROMPTS)} seeds hb{start:04d}..hb{start+len(PROMPTS)-1:04d}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
