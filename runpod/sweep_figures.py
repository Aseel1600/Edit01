#!/usr/bin/env python3
"""Sweep the seed pool for baked-in PEOPLE / figurative (human) statues.

CLIP (clip-vit-base-patch32) scores each seed against figure vs clean prompts. Emits a
ranked suspect list (highest figure-probability first) so the flagged ones can be eyeballed
and rejected. Recall-biased (flag generously; verify visually) -- catches the fountain-statue
and cliff-hermit class of defect that cropdetect/frame-diff can't.

  python runpod/sweep_figures.py            # both orientations
Output: prints ranked suspects + writes runpod/_figure_suspects.json
"""
import glob, json, os, sys
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
]
FIGURE = [
    "a photograph containing a real person, a man or a woman",
    "a human figure, a person sitting or standing in the scene",
    "a statue or stone sculpture of a human body or a nude figure",
    "a carved figure of a person, a bust or a caryatid",
]
PROMPTS = CLEAN + FIGURE
N_CLEAN = len(CLEAN)


def main() -> int:
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"device={dev}; loading CLIP...", flush=True)
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(dev).eval()
    proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    seeds = sorted(glob.glob(str(VERT / "vb*.png"))) + \
            sorted(glob.glob(str(HORIZ / "hb*.png"))) + sorted(glob.glob(str(HORIZ / "lb*.png")))
    print(f"scanning {len(seeds)} seeds", flush=True)

    rows = []
    for i, p in enumerate(seeds):
        try:
            img = Image.open(p).convert("RGB")
        except Exception:
            continue
        inp = proc(text=PROMPTS, images=img, return_tensors="pt", padding=True).to(dev)
        with torch.no_grad():
            probs = model(**inp).logits_per_image.softmax(-1)[0]   # prob over prompts
        p_fig = float(probs[N_CLEAN:].sum())                       # total prob mass on figure prompts
        rows.append((os.path.basename(p)[:-4], round(p_fig, 3)))
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(seeds)}", flush=True)

    rows.sort(key=lambda r: r[1], reverse=True)
    json.dump(rows, open(r"C:\OpenMontage\runpod\_figure_suspects.json", "w"))
    flagged = [r for r in rows if r[1] >= 0.45]
    print(f"\n=== FLAGGED (p_figure >= 0.45): {len(flagged)} ===", flush=True)
    for name, pf in flagged:
        print(f"  {name}  p_fig={pf}", flush=True)
    print(f"\n(next 15 below threshold, for reference)")
    for name, pf in rows[len(flagged):len(flagged)+15]:
        print(f"  {name}  p_fig={pf}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
