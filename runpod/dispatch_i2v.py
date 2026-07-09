#!/usr/bin/env python3
"""Dual-machine Wan 2.2-5B image-to-video dispatcher.

Keeps BOTH the rented GPU pod and the local box rendering motion clips from a
shared queue of seed stills, interleaving vertical and horizontal so the two
orientations progress together.

  - Pod worker: scp the still up, run runpod/render.py on the pod over SSH,
    scp the finished clip back. Pod is 24GB -> model offload (faster).
  - Local worker: render directly through the isolated .venv-wan22.
    Local is 12GB -> sequential offload (slower but fits 720p).

Resumable: a still whose output clip already exists is skipped, so you can
Ctrl-C and re-run and it picks up where it left off. One process, two threads,
one thread-safe queue -> no claim files, no double work.

Usage:
    python3 runpod/dispatch_i2v.py \
        --vert-dir  projects/the-quiet-stoic/library/seeds/vert \
        --horiz-dir projects/the-quiet-stoic/library/seeds/lf \
        --out-dir   projects/the-quiet-stoic/library/gen \
        [--limit N]   # only do the first N items (smoke test)
        [--pod-only | --local-only]
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path

# Camera-DRIVEN motion for mostly-static Stoic stills: the realism comes from a slow
# grounded camera move with real depth/parallax while the SUBJECT stays solid. Asking
# the scene itself to "come alive" makes static subjects (busts, candles) morph or
# erupt -- so we move the camera, lock the subject, and let ambient motion appear only
# where it physically belongs. The negative prompt actively fights deformation.
# Per-category prompts: SAME near-locked-off camera everywhere (fixes the "camera too
# fast" issue), but the ambient clause differs by scene type so water flows / fire
# flickers / clouds drift while static scenes stay calm. Category comes from CLIP
# (runpod/classify_stills.py -> library/categories.json); unknown id => static.
_CAM = ("an extremely slow, gentle, barely-perceptible cinematic camera push-in, the "
        "camera almost locked-off, the subject and structures stay still and solid")
_TAIL = "photorealistic, cinematic, sharp focus, stable geometry"
PROMPTS = {
    "static": f"{_CAM}, with only faint natural ambient motion, {_TAIL}",
    "water":  f"{_CAM}, while the water flows and cascades continuously and naturally with gentle ripples and drifting mist, {_TAIL}",
    "fire":   f"{_CAM}, while the fire flickers and dances with glowing embers and a soft rising heat-shimmer, {_TAIL}",
    "sky":    f"{_CAM}, while the clouds and mist drift and roll slowly across the sky, {_TAIL}",
}
# CAMERA-specific negatives only (leave ambient water/fire/clouds alone). Guidance stays 5.0.
NEGATIVE = (
    "person, people, human, man, woman, figure, silhouette, body, hands, walking, "
    "crowd, animal, new objects appearing, added objects, extra objects, "
    "morphing, warping, distortion, deforming, melting, wobbling, unstable geometry, "
    "shifting shapes, jitter, flickering artifacts, billowing smoke, "
    "fast camera movement, quick camera push-in, rapid zoom, sweeping camera move, "
    "fast dolly, fast pan, camera shake"
)
_CATEGORIES: dict = {}  # {still_stem: category}; populated in main() from categories.json


def prompt_for(stem: str) -> str:
    return PROMPTS.get(_CATEGORIES.get(stem, "static"), PROMPTS["static"])

# --- pod connection (see memory: runpod-gpu-rental) ---
POD_HOST = "root@69.30.85.134"
POD_PORT = "22075"
POD_KEY = str(Path.home() / ".ssh" / "id_ed25519")
POD_REPO = "/workspace/OpenMontage"
POD_TMP = "/workspace/out/queue"
SSH = ["ssh", "-p", POD_PORT, "-i", POD_KEY, "-o", "StrictHostKeyChecking=no",
       "-o", "ConnectTimeout=45", "-o", "ServerAliveInterval=10"]
SCP = ["scp", "-P", POD_PORT, "-i", POD_KEY, "-o", "StrictHostKeyChecking=no"]

# --- local isolated venv with diffusers-main ---
LOCAL_PY = str(Path(__file__).resolve().parent.parent / ".venv-wan22" / "Scripts" / "python.exe")
RENDER = "runpod/render.py"
BATCH_RENDER = "runpod/batch_render.py"
# Chunk sizes: each chunk loads the 5B model ONCE then renders every clip in it,
# amortising the ~5-min load. Pod (48GB, fast) gets big chunks; local (12GB) smaller.
POD_CHUNK = 8
LOCAL_CHUNK = 3

VARIANT = "wan2.2-ti2v-5b"
_print_lock = threading.Lock()


def log(who: str, msg: str) -> None:
    with _print_lock:
        print(f"[{time.strftime('%H:%M:%S')}] {who}: {msg}", flush=True)


def dims_for(orient: str) -> tuple[int, int]:
    return (704, 1280) if orient == "vert" else (1280, 704)


def build_queue(vert_dir: Path, horiz_dir: Path, out_dir: Path, limit: int | None):
    """Interleave vertical + horizontal stills that don't yet have a _w22 clip."""
    def todo(d: Path, orient: str):
        items = []
        for png in sorted(d.glob("*.png")):
            out = out_dir / f"{png.stem}_w22.mp4"   # e.g. vb0168_w22.mp4 / lf0007_w22.mp4
            if out.exists() and out.stat().st_size > 1000:
                continue
            items.append((png, orient, out))
        return items

    vert = todo(vert_dir, "vert")
    horiz = todo(horiz_dir, "horiz")
    interleaved = []
    for i in range(max(len(vert), len(horiz))):
        if i < len(vert):
            interleaved.append(vert[i])
        if i < len(horiz):
            interleaved.append(horiz[i])
    if limit:
        interleaved = interleaved[:limit]
    return interleaved, len(vert), len(horiz)


def render_local_batch(chunk: list) -> list:
    """Render a chunk on the local box in ONE batch_render process (model loaded once)."""
    manifest = [{"ref": str(s), "out": str(out), "width": dims_for(o)[0], "height": dims_for(o)[1],
                 "prompt": prompt_for(s.stem)}
                for (s, o, out) in chunk]
    mf = Path(tempfile.gettempdir()) / f"wan22_local_manifest_{os.getpid()}.json"
    mf.write_text(json.dumps(manifest))
    cmd = [LOCAL_PY, BATCH_RENDER, str(mf), "--offload-mode", "sequential"]
    full_env = {**os.environ, "VIDEO_GEN_LOCAL_ENABLED": "true", "HF_HUB_DISABLE_XET": "1"}
    r = subprocess.run(cmd, capture_output=True, text=True, env=full_env)
    if r.returncode != 0:
        tail = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "unknown"
        log("LOCAL", f"batch FAILED: {tail}")
    return [out for (_, _, out) in chunk if out.exists() and out.stat().st_size > 1000]


def render_pod_batch(chunk: list) -> list:
    """scp the chunk's stills up, render them in ONE batch_render process on the pod
    (model loaded once, --no-offload on the 48GB card), scp the clips back."""
    subprocess.run(SSH + [POD_HOST, f"mkdir -p {POD_TMP}"])
    remote = []  # (remote_ref, remote_out, w, h, local_out, prompt)
    for (s, o, out) in chunk:
        rref = f"{POD_TMP}/{s.name}"
        rout = f"{POD_TMP}/{out.name}"
        if subprocess.run(SCP + [str(s), f"{POD_HOST}:{rref}"]).returncode != 0:
            log("POD", f"scp-up FAILED {s.name}")
            continue
        w, h = dims_for(o)
        remote.append((rref, rout, w, h, out, prompt_for(s.stem)))
    if not remote:
        return []
    manifest = [{"ref": r, "out": ro, "width": w, "height": h, "prompt": pr}
                for (r, ro, w, h, _, pr) in remote]
    mf = Path(tempfile.gettempdir()) / f"wan22_pod_manifest_{os.getpid()}.json"
    mf.write_text(json.dumps(manifest))
    rmani = f"{POD_TMP}/manifest.json"
    if subprocess.run(SCP + [str(mf), f"{POD_HOST}:{rmani}"]).returncode != 0:
        log("POD", "scp manifest FAILED")
        return []
    remote_cmd = (
        f"cd {POD_REPO} && export HF_HOME=/workspace/hf_cache HF_HUB_DISABLE_XET=1 "
        f"VIDEO_GEN_LOCAL_ENABLED=true && python3 {BATCH_RENDER} {rmani} --no-offload"
    )
    subprocess.run(SSH + [POD_HOST, remote_cmd])
    done = []
    for (r, ro, w, h, out, _pr) in remote:
        if (subprocess.run(SCP + [f"{POD_HOST}:{ro}", str(out)]).returncode == 0
                and out.exists() and out.stat().st_size > 1000):
            done.append(out)
    subprocess.run(SSH + [POD_HOST, f"rm -f {POD_TMP}/*.mp4 {POD_TMP}/*.png {rmani}"])
    return done


def worker(name: str, q: "queue.Queue", batch_fn, chunk_size: int, counter: dict):
    while True:
        chunk = []
        for _ in range(chunk_size):
            try:
                chunk.append(q.get_nowait())
            except queue.Empty:
                break
        if not chunk:
            return
        log(name, f"start chunk of {len(chunk)}: {', '.join(s.name for (s, _, _) in chunk)}")
        t0 = time.time()
        done = batch_fn(chunk)
        dt = (time.time() - t0) / 60
        with _print_lock:
            counter["done"] += len(done)
            counter["fail"] += len(chunk) - len(done)
            n = counter["done"]
        per = dt / max(1, len(done))
        log(name, f"chunk done {len(done)}/{len(chunk)} in {dt:.1f}min ({per:.1f}min/clip)  [{n}/{counter['total']} total]")
        for _ in chunk:
            q.task_done()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vert-dir", required=True)
    ap.add_argument("--horiz-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--pod-only", action="store_true")
    ap.add_argument("--local-only", action="store_true")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    global _CATEGORIES
    cat_file = out_dir.parent / "categories.json"
    if cat_file.exists():
        _CATEGORIES = json.load(open(cat_file))
    from collections import Counter
    print(f"categories: {len(_CATEGORIES)} tagged {dict(Counter(_CATEGORIES.values()))}")
    items, nv, nh = build_queue(Path(args.vert_dir), Path(args.horiz_dir), out_dir, args.limit)
    print(f"Queue: {len(items)} clips to render ({nv} vertical + {nh} horizontal pending; interleaved)")
    if not items:
        print("Nothing to do -- every still already has a _w22 clip.")
        return 0

    q: "queue.Queue" = queue.Queue()
    for it in items:
        q.put(it)
    counter = {"done": 0, "fail": 0, "total": len(items)}

    threads = []
    if not args.local_only:
        threads.append(threading.Thread(target=worker, args=("POD", q, render_pod_batch, POD_CHUNK, counter), daemon=True))
    if not args.pod_only:
        threads.append(threading.Thread(target=worker, args=("LOCAL", q, render_local_batch, LOCAL_CHUNK, counter), daemon=True))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"\nDONE. {counter['done']} rendered, {counter['fail']} failed, "
          f"{q.qsize()} left unclaimed.")
    return 0 if counter["fail"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
