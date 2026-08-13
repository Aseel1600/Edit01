#!/usr/bin/env python3
"""PERSON sweep over the seed pool using a real object detector (YOLOS-small, COCO 'person').

Replaces the CLIP-based runpod/sweep_figures.py for finding PEOPLE. CLIP scores a whole image
against text prompts, so a person filling ~1% of a 1536x2752 frame is drowned out by the dominant
scene and reads "clean" -- that is how vb0161 (a seated woman at the base of a cliff) passed the
old sweep and shipped in 4 videos. Tiling CLIP did not fix it either (the known figure scored
LOWER than a clean seed). An object detector localises instead of summarising, so a small person
is still a confident detection with a bounding box you can eyeball.

  python runpod/sweep_people.py [--orient vert|horiz|both] [--thresh 0.5]

Reports every seed with a detected person, its confidence, box, and the box's area as a % of the
frame (small-but-real figures matter here because Ken Burns zooms IN on them). Writes
runpod/_people_suspects.json. Note CLIP is still the right tool for STATUES/sculpture, which COCO
'person' does not reliably cover -- keep sweep_figures.py for that pass.
"""
import argparse, glob, json, os
from pathlib import Path
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForObjectDetection

PROJ = Path(r"C:\OpenMontage") / "projects" / "the-quiet-stoic"
VERT = PROJ / "library" / "seeds" / "vert"
HORIZ = PROJ / "library" / "seeds" / "lf"
MODEL = "hustvl/yolos-small"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--orient", choices=["vert", "horiz", "both"], default="both")
    ap.add_argument("--thresh", type=float, default=0.35)
    args = ap.parse_args()

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"device={dev}; loading {MODEL}...", flush=True)
    proc = AutoImageProcessor.from_pretrained(MODEL)
    model = AutoModelForObjectDetection.from_pretrained(MODEL).to(dev).eval()

    seeds = []
    if args.orient in ("vert", "both"):
        seeds += sorted(glob.glob(str(VERT / "vb*.png")))
    if args.orient in ("horiz", "both"):
        seeds += sorted(glob.glob(str(HORIZ / "hb*.png"))) + sorted(glob.glob(str(HORIZ / "lb*.png")))
    print(f"scanning {len(seeds)} seeds for people (thresh={args.thresh})", flush=True)

    hits = []
    for i, p in enumerate(seeds):
        try:
            im = Image.open(p).convert("RGB")
        except Exception:
            continue
        W, H = im.size
        inp = proc(images=im, return_tensors="pt").to(dev)
        with torch.no_grad():
            out = model(**inp)
        res = proc.post_process_object_detection(
            out, target_sizes=torch.tensor([[H, W]]).to(dev), threshold=args.thresh)[0]
        people = []
        for s, l, b in zip(res["scores"], res["labels"], res["boxes"]):
            if model.config.id2label[int(l)] != "person":
                continue
            x0, y0, x1, y1 = [float(v) for v in b]
            area = abs((x1 - x0) * (y1 - y0)) / (W * H) * 100
            people.append({"conf": round(float(s), 3),
                           "box": [round(x0), round(y0), round(x1), round(y1)],
                           "area_pct": round(area, 2)})
        if people:
            people.sort(key=lambda d: -d["conf"])
            hits.append({"seed": os.path.basename(p)[:-4], "n": len(people), "people": people})
        if (i + 1) % 40 == 0:
            print(f"  {i+1}/{len(seeds)}  ({len(hits)} with people so far)", flush=True)

    hits.sort(key=lambda h: -h["people"][0]["conf"])
    json.dump(hits, open(r"C:\OpenMontage\runpod\_people_suspects.json", "w"), indent=1)
    print(f"\n=== SEEDS WITH A DETECTED PERSON: {len(hits)} / {len(seeds)} ===", flush=True)
    for h in hits:
        top = h["people"][0]
        print(f"  {h['seed']}  conf={top['conf']}  area={top['area_pct']}%  box={top['box']}"
              f"{'  (+%d more)' % (h['n'] - 1) if h['n'] > 1 else ''}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
