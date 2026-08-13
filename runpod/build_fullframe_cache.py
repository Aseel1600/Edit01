#!/usr/bin/env python3
"""Refreshable full-frame cache for b-roll selection (shorts + long-forms).

Runs ffmpeg cropdetect over every Wan clip in library/gen and records whether it is TRUE
full-frame or letterboxed (baked black bars scale/crop can't remove). The mix composers
read these caches so they never pick a letterboxed clip. Rejected clips (moved to
library/_rejected) aren't in gen, so they're absent from the cache. Re-run after rendering
new clips; already-scanned ids are skipped unless --force.

  --orient vert  : vb*_w22.mp4 (native 704x1280) -> library/fullframe_vert.json   ff = w>=696 & h>=1244
  --orient horiz : hb*/lb*/lf*_w22.mp4 (native 1280x704) -> library/fullframe_horiz.json  ff = w>=1244 & h>=696
  (no --orient   : does BOTH)

Output: { "vb0006": true, "vb0048": false, ... }
"""
import json, os, re, subprocess, sys
from pathlib import Path

PROJ = Path(r"C:\OpenMontage") / "projects" / "the-quiet-stoic"
GEN = PROJ / "library" / "gen"

ORIENTS = {
    "vert":  {"patterns": ["vb*_w22.mp4"],                               "out": "fullframe_vert.json",  "min_w": 696,  "min_h": 1244},
    "horiz": {"patterns": ["hb*_w22.mp4", "lb*_w22.mp4", "lf*_w22.mp4"], "out": "fullframe_horiz.json", "min_w": 1244, "min_h": 696},
}


def cropdetect(mp4: Path, min_w: int, min_h: int):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-ss", "1", "-i", str(mp4),
                        "-vf", "cropdetect=24:2:0", "-frames:v", "20", "-f", "null", "-"],
                       capture_output=True, text=True)
    ms = re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", r.stderr)
    if not ms:
        return None
    w, h = int(ms[-1][0]), int(ms[-1][1])
    return (w, h, w >= min_w and h >= min_h)


def build(orient: str, force: bool):
    cfg = ORIENTS[orient]
    out = PROJ / "library" / cfg["out"]
    cache = json.load(open(out)) if out.exists() else {}
    clips = sorted(f for pat in cfg["patterns"] for f in GEN.glob(pat))
    scanned = 0
    for mp4 in clips:
        stem = mp4.stem.replace("_w22", "")
        if stem in cache and not force:
            continue
        res = cropdetect(mp4, cfg["min_w"], cfg["min_h"])
        cache[stem] = bool(res and res[2])
        scanned += 1
        if scanned % 25 == 0:
            print(f"  [{orient}] {scanned} newly scanned", flush=True)
    json.dump(cache, open(out, "w"), indent=1)
    full = sum(1 for v in cache.values() if v)
    print(f"DONE [{orient}] cache={len(cache)}  full-frame={full}  letterboxed={len(cache)-full}  (+{scanned} new)  -> {out}")


def main():
    force = "--force" in sys.argv
    orients = [a for a in ("vert", "horiz") if f"--orient={a}" in sys.argv or a in sys.argv]
    if not orients:
        orients = ["vert", "horiz"]
    for o in orients:
        build(o, force)


if __name__ == "__main__":
    main()
