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
PROMPT = (
    "a slow, smooth cinematic camera push-in with natural depth and parallax, "
    "the subject stays still and solid, with gentle but clearly visible natural "
    "ambient motion where it belongs, photorealistic, cinematic, sharp focus, "
    "stable geometry"
)
# NB: keep "billowing smoke" (stops the candle smoke-bomb) + all anti-morph/anti-person
# terms; but DROP "fast motion, chaotic movement" so ambient motion reads more clearly.
NEGATIVE = (
    "person, people, human, man, woman, figure, silhouette, body, hands, walking, "
    "crowd, animal, new objects appearing, added objects, extra objects, "
    "morphing, warping, distortion, deforming, melting, wobbling, unstable geometry, "
    "shifting shapes, jitter, flickering artifacts, billowing smoke"
)

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


def render_local(still: Path, orient: str, out: Path) -> bool:
    w, h = dims_for(orient)
    cmd = [
        LOCAL_PY, RENDER, "wan", "--variant", VARIANT, "--operation", "image_to_video",
        "--ref", str(still), "--width", str(w), "--height", str(h),
        "--steps", "50", "--offload-mode", "sequential",
        "--prompt", PROMPT, "--negative", NEGATIVE, "--out", str(out),
    ]
    env = {"VIDEO_GEN_LOCAL_ENABLED": "true", "HF_HUB_DISABLE_XET": "1"}
    import os
    full_env = {**os.environ, **env}
    r = subprocess.run(cmd, capture_output=True, text=True, env=full_env)
    if r.returncode != 0:
        log("LOCAL", f"FAILED {still.name}: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else 'unknown'}")
        return False
    return out.exists()


def render_pod(still: Path, orient: str, out: Path) -> bool:
    w, h = dims_for(orient)
    remote_ref = f"{POD_TMP}/{still.name}"
    remote_out = f"{POD_TMP}/{out.name}"
    # 1) upload still
    if subprocess.run(SSH + [POD_HOST, f"mkdir -p {POD_TMP}"]).returncode != 0:
        return False
    if subprocess.run(SCP + [str(still), f"{POD_HOST}:{remote_ref}"]).returncode != 0:
        log("POD", f"scp-up FAILED {still.name}")
        return False
    # 2) render
    remote_cmd = (
        f"cd {POD_REPO} && export HF_HOME=/workspace/hf_cache HF_HUB_DISABLE_XET=1 "
        f"VIDEO_GEN_LOCAL_ENABLED=true && python3 {RENDER} wan --variant {VARIANT} "
        f"--operation image_to_video --ref {remote_ref} --width {w} --height {h} "
        f"--steps 50 --no-offload --prompt '{PROMPT}' --negative '{NEGATIVE}' "
        f"--out {remote_out}"
    )
    if subprocess.run(SSH + [POD_HOST, remote_cmd]).returncode != 0:
        log("POD", f"render FAILED {still.name}")
        return False
    # 3) pull clip back
    if subprocess.run(SCP + [f"{POD_HOST}:{remote_out}", str(out)]).returncode != 0:
        log("POD", f"scp-down FAILED {out.name}")
        return False
    subprocess.run(SSH + [POD_HOST, f"rm -f {remote_ref} {remote_out}"])
    return out.exists() and out.stat().st_size > 1000


def worker(name: str, q: "queue.Queue", render_fn, counter: dict):
    while True:
        try:
            still, orient, out = q.get_nowait()
        except queue.Empty:
            return
        log(name, f"start {still.name} ({orient})")
        t0 = time.time()
        ok = render_fn(still, orient, out)
        dt = (time.time() - t0) / 60
        with _print_lock:
            counter["done" if ok else "fail"] += 1
            n = counter["done"]
        log(name, f"{'OK' if ok else 'FAIL'} {still.name} in {dt:.1f}min  [{n}/{counter['total']} done]")
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
        threads.append(threading.Thread(target=worker, args=("POD", q, render_pod, counter), daemon=True))
    if not args.pod_only:
        threads.append(threading.Thread(target=worker, args=("LOCAL", q, render_local, counter), daemon=True))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"\nDONE. {counter['done']} rendered, {counter['fail']} failed, "
          f"{q.qsize()} left unclaimed.")
    return 0 if counter["fail"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
