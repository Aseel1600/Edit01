#!/usr/bin/env python3
"""TILED figure sweep -- catches SMALL people that the whole-image sweep misses.

Why this exists: runpod/sweep_figures.py runs CLIP over the ENTIRE image, so a person occupying
~1% of a 1536x2752 frame is drowned out by the dominant scene ("a cliff", "a forest") and scores
clean. vb0161 (a seated woman at the base of a cliff) passed that sweep and shipped in 4 videos.
Ken Burns then zooms IN, making the figure far more prominent in the video than in the seed.

Fix: score overlapping square tiles as well as the full frame, and take the MAX figure
probability across them. A small figure fills a big fraction of its own tile, so it scores high.

  python runpod/sweep_figures_tiled.py [--orient vert|horiz|both]
Output: ranked suspects -> runpod/_figure_suspects_tiled.json
"""
import argparse, glob, json, os
from pathlib import Path
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

PROJ = Path(r"C:\OpenMontage") / "projects" / "the-quiet-stoic"
VERT = PROJ / "library" / "seeds" / "vert"
HORIZ = PROJ / "library" / "seeds" / "lf"

CLEAN = [
    "an empty landscape or nature scene with no people",
    "old architecture, ruins or a building with no people and no statues",
    "an object, doorway or interior with no people",
    "rock, stone texture, foliage or sky",
]
FIGURE = [
    "a photograph containing a real person, a man or a woman",
    "a human figure, a person sitting or standing in the scene",
    "a statue or stone sculpture of a human body or a nude figure",
    "a carved figure of a person, a bust or a caryatid",
]
PROMPTS = CLEAN + FIGURE
N_CLEAN = len(CLEAN)
TILE, STRIDE = 768, 512          # square tiles, 33% overlap -> a small figure fills its own tile


def tiles_of(im):
    """Full frame + overlapping square tiles."""
    W, H = im.size
    out = [im]
    for top in range(0, max(1, H - TILE + 1), STRIDE):
        for left in range(0, max(1, W - TILE + 1), STRIDE):
            out.append(im.crop((left, top, min(left + TILE, W), min(top + TILE, H))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--orient", choices=["vert", "horiz", "both"], default="vert")
    ap.add_argument("--thresh", type=float, default=0.55)
    args = ap.parse_args()

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"device={dev}; loading CLIP...", flush=True)
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(dev).eval()
    proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    seeds = []
    if args.orient in ("vert", "both"):
        seeds += sorted(glob.glob(str(VERT / "vb*.png")))
    if args.orient in ("horiz", "both"):
        seeds += sorted(glob.glob(str(HORIZ / "hb*.png"))) + sorted(glob.glob(str(HORIZ / "lb*.png")))
    print(f"scanning {len(seeds)} seeds with tiling (tile={TILE} stride={STRIDE})", flush=True)

    rows = []
    for i, p in enumerate(seeds):
        try:
            im = Image.open(p).convert("RGB")
        except Exception:
            continue
        crops = tiles_of(im)
        best, best_j = 0.0, 0
        for b in range(0, len(crops), 16):                 # batch tiles
            batch = crops[b:b + 16]
            # same call shape as sweep_figures.py (works across transformers versions;
            # get_text_features returns an output object, not a tensor, on 5.x)
            inp = proc(text=PROMPTS, images=batch, return_tensors="pt", padding=True).to(dev)
            with torch.no_grad():
                probs = model(**inp).logits_per_image.softmax(-1)
            for k in range(probs.shape[0]):
                pf = float(probs[k, N_CLEAN:].sum())
                if pf > best:
                    best, best_j = pf, b + k
        rows.append((os.path.basename(p)[:-4], round(best, 3), best_j))
        if (i + 1) % 25 == 0:
            print(f"  {i+1}/{len(seeds)}", flush=True)

    rows.sort(key=lambda r: r[1], reverse=True)
    json.dump(rows, open(r"C:\OpenMontage\runpod\_figure_suspects_tiled.json", "w"))
    flagged = [r for r in rows if r[1] >= args.thresh]
    print(f"\n=== FLAGGED (max-tile p_figure >= {args.thresh}): {len(flagged)} ===", flush=True)
    for name, pf, j in flagged:
        print(f"  {name}  p_fig={pf}  (tile #{j}{' = FULL FRAME' if j == 0 else ''})", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
