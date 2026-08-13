"""Conform batch i2v clips to stock-marketplace spec (4K UHD) + metadata sidecar.

Stock sites that accept AI video (Adobe Stock, Pond5, Blackbox) require
3840x2160 minimum, clean H.264, >=5s, and an explicit generative-AI label.
This script takes rendered clips (e.g. Wan 2.2-5B 1280x704), Real-ESRGAN
upscales them, cover-crops to exactly 3840x2160, QC-probes the result, and
emits a `stock_metadata.csv` row per clip (title/keywords/category/AI flag)
ready to adapt to each marketplace's upload form.

Usage:
  python tools/video/stock_conform.py <clip.mp4 | dir> --out <dir>
         [--meta categories.json]   # optional: {basename: {category, prompt}}
         [--limit N]                # conform only the first N clips

Titles/keywords are DRAFTS derived from category/prompt — review the CSV
before any upload. Uploading itself is user-only.
"""
import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

TARGET_W, TARGET_H = 3840, 2160
MIN_SECONDS = 5.0

# per-category draft keyword banks (extend as categories grow)
KEYWORDS = {
    "water": "water, ocean, waves, flowing, calm, nature, sea, ripple, meditation, background",
    "fire": "fire, flames, ember, glow, warm, flicker, cozy, dark, background, abstract",
    "clouds": "clouds, sky, drifting, timelapse, weather, atmosphere, serene, background, nature",
    "static_calm": "calm, minimal, still life, ambient, mood, cinematic, background, atmosphere",
    "nature": "nature, landscape, outdoor, scenic, tranquil, environment, background, cinematic",
    "city": "city, urban, street, architecture, evening, lights, cinematic, background",
}
BASE_TAGS = "generative ai, ai generated, 4k, uhd, b-roll, no people"


def probe(path: Path) -> dict:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json",
         "-show_format", "-show_streams", str(path)],
        capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def conform_one(src: Path, out_dir: Path) -> Path | None:
    """Upscale + cover-crop one clip to 3840x2160. Returns output path or None."""
    info = probe(src)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    w, h = int(v["width"]), int(v["height"])
    if h > w:
        print(f"  [skip] {src.name}: vertical ({w}x{h}) — stock spec is landscape UHD")
        return None
    dur = float(info["format"]["duration"])
    if dur < MIN_SECONDS:
        print(f"  [skip] {src.name}: {dur:.1f}s < {MIN_SECONDS}s stock minimum")
        return None

    out = out_dir / f"{src.stem}_4k.mp4"
    if out.exists():
        print(f"  [ok/cached] {out.name}")
        return out

    # 1) Real-ESRGAN 4x (frame-accurate, local GPU) via the registry tool.
    # tile=512 bounds VRAM so 4x on a 12GB card doesn't CUDA-OOM (whole-frame
    # 5120x2816 fp16 tensors overflow); ~identical quality, marginally slower.
    from tools.enhancement.upscale import Upscale
    up = out_dir / f"{src.stem}_esrgan.mp4"
    r = Upscale().execute({"input_path": str(src), "output_path": str(up),
                           "scale": 4, "tile": 512})
    if not r.success:
        print(f"  [FAIL] {src.name}: upscale — {r.error}")
        return None

    # 2) Cover-crop to exactly 3840x2160 (lanczos), clean H.264
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(up),
         "-vf", (f"scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=increase"
                 f":flags=lanczos,crop={TARGET_W}:{TARGET_H}"),
         "-c:v", "libx264", "-crf", "16", "-preset", "slow",
         "-pix_fmt", "yuv420p", "-an", str(out)],
        check=True)
    up.unlink(missing_ok=True)  # ESRGAN intermediate is huge — drop it

    # 3) QC probe
    q = probe(out)
    qv = next(s for s in q["streams"] if s["codec_type"] == "video")
    ok = (int(qv["width"]), int(qv["height"])) == (TARGET_W, TARGET_H)
    print(f"  [{'ok' if ok else 'FAIL'}] {out.name}: {qv['width']}x{qv['height']} "
          f"{float(q['format']['duration']):.1f}s {int(q['format']['size'])/1e6:.0f}MB")
    return out if ok else None


def draft_metadata(src: Path, meta: dict) -> dict:
    m = meta.get(src.stem, meta.get(src.name, {}))
    cat = m.get("category", "nature")
    prompt = m.get("prompt", "")
    subject = prompt.split(",")[0].strip() if prompt else src.stem.replace("_", " ")
    return {
        "file": f"{src.stem}_4k.mp4",
        "title": f"{subject[:1].upper()}{subject[1:]} — cinematic 4K background loop"[:70],
        "keywords": f"{KEYWORDS.get(cat, KEYWORDS['nature'])}, {BASE_TAGS}",
        "category": cat,
        "generative_ai": "true",
        "source_clip": src.name,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--out", required=True)
    ap.add_argument("--meta", help="categories.json: {basename: {category, prompt}}")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    src = Path(a.input)
    clips = sorted(src.glob("*.mp4")) if src.is_dir() else [src]
    if a.limit:
        clips = clips[:a.limit]
    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = json.loads(Path(a.meta).read_text(encoding="utf-8")) if a.meta else {}

    rows, done = [], 0
    for c in clips:
        r = conform_one(c, out_dir)
        if r:
            rows.append(draft_metadata(c, meta))
            done += 1

    if rows:
        csv_path = out_dir / "stock_metadata.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"\n{done}/{len(clips)} conformed -> {out_dir}")
        print(f"metadata drafts -> {csv_path}  (review before upload; uploads are user-only)")
    else:
        print(f"\n0/{len(clips)} conformed — nothing to submit")


if __name__ == "__main__":
    main()
