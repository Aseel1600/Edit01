#!/usr/bin/env python3
"""Zero-shot CLIP classifier to tag b-roll seed stills by dominant motion type,
so the i2v dispatcher can pick a per-category prompt (water flows, fire flickers,
clouds drift, static scenes stay locked). Writes categories.json {still_id: cat}.

Usage: .venv-wan22/Scripts/python.exe runpod/classify_stills.py <vert_dir> <horiz_dir> <out_json>
"""
import glob
import json
import os
import sys

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

LABELS = {
    "water": "a waterfall, river, ocean, sea waves, rain, or flowing water",
    "fire": "fire, flames, a lit candle, a fireplace, or glowing burning embers",
    "sky": "a wide open sky or landscape with drifting clouds, fog, or rolling mist",
    "static": "a stone statue or bust, stone ruins, architecture, an object, a book, or a still dark interior",
}


def main() -> int:
    vert_dir, horiz_dir, out_json = sys.argv[1], sys.argv[2], sys.argv[3]
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(dev).eval()
    proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    keys = list(LABELS)
    texts = [LABELS[k] for k in keys]

    result, counts = {}, {k: 0 for k in keys}
    for d in (vert_dir, horiz_dir):
        for f in sorted(glob.glob(os.path.join(d, "*.png"))):
            img = Image.open(f).convert("RGB")
            inp = proc(text=texts, images=img, return_tensors="pt", padding=True).to(dev)
            with torch.no_grad():
                probs = model(**inp).logits_per_image.softmax(-1)[0]
            cat = keys[int(probs.argmax())]
            result[os.path.splitext(os.path.basename(f))[0]] = cat
            counts[cat] += 1
    json.dump(result, open(out_json, "w"), indent=1)
    print("counts:", counts, "total:", len(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
