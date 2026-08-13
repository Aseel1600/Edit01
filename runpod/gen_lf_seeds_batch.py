#!/usr/bin/env python3
"""Batch-generate new horizontal (16:9) Stoic b-roll SEEDS with FLUX.2-klein (local, free).

Loads the model ONCE, then generates every prompt -> library/seeds/lf/hb00NN.png at 2752x1536.
Prompts avoid people / modern objects to reduce what Wan i2v can hallucinate onto. Next hb number
is auto-detected. After this, i2v the new seeds with Wan 2.2 (dispatch_i2v.py).
"""
from __future__ import annotations
import sys, time, re, glob, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.base_tool import _load_dotenv
_load_dotenv()
import torch
from diffusers import Flux2KleinPipeline

SEEDS = Path(r"C:\OpenMontage\projects\the-quiet-stoic\library\seeds\lf")
W, H = 2752, 1536   # horizontal 16:9

TAIL = "cinematic, moody, atmospheric, 35mm film grain, soft natural light, no people, no text, no watermark"
PROMPTS = [
    f"An ancient Roman marble bust of a bearded philosopher on a weathered stone pedestal in a dim candlelit crypt, shafts of light, {TAIL}",
    f"A misty mountain valley at dawn, layered ridges fading into soft fog, cold blue light, wide vista, {TAIL}",
    f"Crumbling ancient Greek temple ruins with weathered stone columns under a heavy stormy grey sky, dramatic light, {TAIL}",
    f"A candlelit stone monastery corridor with arched vaults, warm glow, dust motes drifting in the air, {TAIL}",
    f"A rugged rocky coastline with dark cliffs beneath heavy clouds at dusk, distant sea, brooding, {TAIL}",
    f"An old leather-bound book lying open on a dark wooden desk beside a brass oil lamp, warm candlelight, {TAIL}",
    f"A foggy pine forest at dawn with god rays breaking through tall trees, thick mist, silent, {TAIL}",
    f"A weathered ancient stone staircase descending into fog on a bleak mountainside, timeworn, {TAIL}",
    f"A snow-covered old graveyard with worn celtic stone crosses at dusk, bare black trees, cold and still, {TAIL}",
    f"Vast rippled desert sand dunes at golden hour, long soft shadows, minimal and serene, {TAIL}",
    f"A dark still mountain lake mirroring a starry night sky and distant peaks, long exposure, {TAIL}",
    f"A vast ancient library with towering wooden shelves of old books, warm light from a high arched window, {TAIL}",
    f"A single dramatic shaft of sunlight breaking through a stormy sky over a barren windswept moor, {TAIL}",
    f"A weathered marble statue of a draped robed figure overtaken by ivy and moss in an overgrown ruin, {TAIL}",
    f"Rain streaking down a dark old window overlooking a blurred stone courtyard, melancholy, {TAIL}",
    f"A single candle flame burning on an old wooden table in a very dark room, shallow depth of field, {TAIL}",
    f"A jagged snow-capped mountain peak piercing a glowing sea of clouds at sunrise, sublime, {TAIL}",
    f"A ruined ancient stone archway framing a misty distant landscape beyond, moody dawn, {TAIL}",
    f"Glowing embers in a stone fireplace in a rustic dark cottage, warm firelight flickering, {TAIL}",
    f"A field of tall golden wheat swaying under a heavy overcast sky, wind, wide cinematic shot, {TAIL}",
    f"A lone empty wooden rowboat on a calm misty fjord surrounded by steep dark cliffs at dawn, {TAIL}",
    f"A weathered brass hourglass on a stone ledge with soft window light, sand mid-fall, {TAIL}",
    f"A narrow cobblestone medieval alley at night lit by a single iron lantern, wet stones, drifting fog, {TAIL}",
    f"A frozen waterfall over dark mossy rock in a silent snowy gorge, pale winter light, {TAIL}",
]


def next_hb() -> int:
    nums = [int(m.group(1)) for f in glob.glob(str(SEEDS / "hb*.png"))
            for m in [re.match(r"hb0*(\d+)\.png", os.path.basename(f))] if m]
    return (max(nums) + 1) if nums else 1


def main() -> int:
    SEEDS.mkdir(parents=True, exist_ok=True)
    print(f"Loading FLUX.2-klein-4B...", flush=True)
    t0 = time.time()
    pipe = Flux2KleinPipeline.from_pretrained("black-forest-labs/FLUX.2-klein-4B", torch_dtype=torch.bfloat16)
    pipe.enable_model_cpu_offload()
    print(f"MODEL_LOADED {time.time()-t0:.0f}s", flush=True)
    start = next_hb()
    for i, prompt in enumerate(PROMPTS):
        hb = f"hb{start + i:04d}"
        out = SEEDS / f"{hb}.png"
        t = time.time()
        img = pipe(prompt=prompt, width=W, height=H, num_inference_steps=4, guidance_scale=1.0).images[0]
        img.save(out)
        print(f"SEED_DONE {hb} ({time.time()-t:.0f}s)", flush=True)
    print(f"BATCH_DONE {len(PROMPTS)} seeds hb{start:04d}..hb{start+len(PROMPTS)-1:04d}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
