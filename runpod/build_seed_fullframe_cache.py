#!/usr/bin/env python3
"""Seed-based full-frame cache for Ken-Burns STILL selection.

The clip cache (fullframe_vert/horiz.json) is built from the Wan CLIPS, which fill any
letterbox bars with generated content -> clips read full-frame. But Ken-Burns stills pull
the RAW seed png, which can still have baked black bars. So stills need their OWN cache,
cropdetected from the seed pngs directly.

  full-frame test: cropdetected content covers >=98% of the png's real width AND height.
Outputs: library/fullframe_seeds_vert.json  and  library/fullframe_seeds_lf.json
"""
import json, os, re, subprocess, glob, sys

PROJ = r"C:\OpenMontage\projects\the-quiet-stoic"

def dims(png):
    r = subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height",
                        "-of","csv=p=0:s=x", png], capture_output=True, text=True).stdout.strip()
    try:
        w,h = r.split("x"); return int(w), int(h)
    except Exception:
        return None

def content(png):
    # limit=10 -> only cut NEAR-PURE-BLACK pixels (real letterbox bars are ~0). Genuinely dark
    # photo edges (value 20+) are NOT cut, so they don't get mistaken for bars.
    r = subprocess.run(["ffmpeg","-hide_banner","-loop","1","-i",png,"-t","0.5","-vf","cropdetect=10:2:0","-f","null","-"],
                       capture_output=True, text=True)
    ms = re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", r.stderr)
    if not ms: return None
    return int(ms[-1][0]), int(ms[-1][1])

def build(seed_dir, out_path):
    cache = {}
    n_ff = 0
    pngs = sorted(glob.glob(os.path.join(seed_dir, "*.png")))
    for i, png in enumerate(pngs):
        stem = os.path.splitext(os.path.basename(png))[0]
        d = dims(png); c = content(png)
        if not d or not c:
            cache[stem] = True   # cropdetect gave nothing -> assume full (don't over-exclude)
            n_ff += 1
        else:
            # Only flag SIGNIFICANT letterbox/pillarbox (real bars ~<85% of a dim). Dark
            # image edges (night skies etc.) sit ~90-99% and must NOT be flagged.
            ff = (c[0] >= 0.92 * d[0]) and (c[1] >= 0.92 * d[1])
            cache[stem] = ff; n_ff += ff
        if (i+1) % 25 == 0: print(f"  {i+1}/{len(pngs)}", flush=True)
    json.dump(cache, open(out_path, "w"), indent=1)
    print(f"DONE {out_path}: {len(cache)} seeds, full-frame={n_ff}, letterboxed={len(cache)-n_ff}")

build(os.path.join(PROJ, "library", "seeds", "vert"), os.path.join(PROJ, "library", "fullframe_seeds_vert.json"))
build(os.path.join(PROJ, "library", "seeds", "lf"), os.path.join(PROJ, "library", "fullframe_seeds_lf.json"))
