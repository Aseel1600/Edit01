#!/usr/bin/env python3
"""Batch-generate a NEW mixed batch of Stoic b-roll SEEDS with FLUX.2-klein (local, free).

Loads the model ONCE, then generates:
  - 20 horizontal (16:9) -> library/seeds/lf/hb00NN.png  @ 2752x1536
  - 20 vertical   (9:16) -> library/seeds/vert/vb0NNN.png @ 1536x2752

Fresh concepts, deliberately LIGHT on statues/busts and candles/lanterns (pool is already
saturated with those, and centered candle stills make Wan i2v hallucinate flames). No people,
no modern objects, no text -> less for Wan i2v to hallucinate onto. Next hb/vb numbers are
auto-detected and existing files are skipped (resumable). After this, i2v with dispatch_i2v.py.
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
    f"Storm clouds rolling over a vast empty ocean horizon at dusk, heavy swell, dramatic, {TAIL}",
    f"Ancient Roman amphitheater ruins under a clear sky, long raking shadows across worn stone, {TAIL}",
    f"A weathered wooden pier stretching into a calm fog-covered lake at dawn, still water, {TAIL}",
    f"Rolling emerald highland hills under a broken sky with a distant curtain of rain, {TAIL}",
    f"A vast mirror-still salt flat reflecting a pastel twilight sky, minimal and serene, {TAIL}",
    f"Wind-blown dune grass on a headland above a churning grey sea, cold spray, {TAIL}",
    f"A weathered stone bridge arching over a rushing alpine stream, mist and spray, {TAIL}",
    f"Snow drifting through a silent dark spruce forest at blue hour, hushed and still, {TAIL}",
    f"A dry cracked desert riverbed stretching to distant red mesas under a low sun, {TAIL}",
    f"A calm fishing harbor at first light, glassy water and moored wooden hulls, {TAIL}",
    f"Layered sandstone canyon walls glowing deep orange at sunset, long shadows, {TAIL}",
    f"A lavender field bending in the wind under a heavy overcast sky, wide cinematic shot, {TAIL}",
    f"Terraced hillside vineyards fading into soft morning haze, rolling rows, {TAIL}",
    f"A slow dark river winding through a deep mossy forest gorge, long-exposure water, {TAIL}",
    f"Sunbeams flooding a vast empty stone cathedral nave through high arched windows, dust motes, {TAIL}",
    f"A lone ancient gnarled oak tree on an empty windswept moor at dawn, bare branches, {TAIL}",
    f"Distant lightning over a flat empty plain beneath a towering wall of storm cloud, {TAIL}",
    f"A frozen mountain tarn with cracked ice under cold flat overcast light, bleak, {TAIL}",
    f"Autumn mist hanging over a still reed-lined lake at sunrise, golden and quiet, {TAIL}",
    f"A rugged headland of dark basalt columns meeting a heavy grey sea, brooding, {TAIL}",
]

VERT_PROMPTS = [
    f"A single towering ancient stone column vanishing upward into thick mist, low angle, {TAIL}",
    f"A tall thin waterfall plunging down a sheer dark cliff into a misty pool, vertical, {TAIL}",
    f"A lone cypress tree silhouetted against a pale dawn sky, tall vertical framing, {TAIL}",
    f"A vertical shaft of sunlight falling from a cave mouth onto wet dark stone, {TAIL}",
    f"A tall gothic arched window with light streaming down into deep shadow, {TAIL}",
    f"A solitary lighthouse on black rocks beneath a towering stormy sky, vertical, {TAIL}",
    f"Immense redwood trunks rising into fog, dramatic low upward angle, {TAIL}",
    f"A towering sheer sea cliff plunging to a foaming grey shore, vertical framing, {TAIL}",
    f"A steep mountain ridge climbing into low rolling cloud, tall vertical composition, {TAIL}",
    f"A narrow slot canyon glowing with light filtering from high above, {TAIL}",
    f"Weathered ancient stone monastery steps spiraling steeply upward, worn and mossy, {TAIL}",
    f"Tall golden reeds against a still misty lake at dawn, vertical framing, {TAIL}",
    f"A towering thundercloud rising over a lone dark hill, dramatic vertical sky, {TAIL}",
    f"A tall frozen icicle curtain over a dark dripping rock wall, pale winter light, {TAIL}",
    f"A single tall ancient tree with sprawling roots on a foggy ridge, tall crop, {TAIL}",
    f"A vertical ribbon of green aurora over a jagged dark mountain peak, night, {TAIL}",
    f"A tall worn temple doorway opening into warm inner shadow, ancient steps, {TAIL}",
    f"Rain streaking down a tall dark stone wall lit by a distant warm glow, melancholy, {TAIL}",
    f"A steep forest waterfall tumbling through mossy boulders, tall vertical crop, {TAIL}",
    f"A tall slanting dust-filled sunbeam cutting through a dim ancient stone hall, {TAIL}",
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
            print(f"SKIP {out.name} (exists)", flush=True)
            done += 1
            continue
        t = time.time()
        img = pipe(prompt=prompt, width=w, height=h, num_inference_steps=4, guidance_scale=1.0).images[0]
        img.save(out)
        done += 1
        print(f"SEED_DONE {out.name} {w}x{h} ({time.time()-t:.0f}s) [{done}/{len(jobs)}]", flush=True)
    print(f"BATCH_DONE {len(jobs)} seeds", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
