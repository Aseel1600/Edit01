#!/usr/bin/env python3
"""
CINEMATIC CAMERA PACK renderer — camera-only animation over a frozen still.

The source image is treated as a perfectly frozen photograph. NOTHING inside
the image is animated, deformed, morphed or redesigned. A virtual cinema
camera moves over a 9:16 composition built from the source:

  * the COMPLETE original image, sharp, fitted to the frame width and
    centered (no subject cropping at all), mounted over
  * a heavily blurred, dimmed copy of itself filling the 9:16 canvas
    (standard intentional vertical-video treatment).

Each camera move is a smoothstep-eased keyframed crop window (pan + zoom)
over that canvas, rendered to 1080x1920 @ 30fps, exactly 300 frames
(= 10.000 s), H.264 MP4.

Usage:
    python3 render_cam_pack.py <source_image> <out_dir> <PREFIX> [move ...]

Example:
    python3 render_cam_pack.py source.png CINEMATIC_CAMERA_PACK/IMAGE_01 IMAGE_01
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFilter

try:
    import imageio_ffmpeg
    FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_BIN = "ffmpeg"

FPS = 30
DURATION = 10.0
OUT_W, OUT_H = 1080, 1920
CAN_W, CAN_H = 1620, 2880          # canvas = 1.5x output -> zoom headroom w/o upscaling blur

# ---------------------------------------------------------------------------
# Camera moves. Keyframes: (t_sec, cx, cy, zoom)
#   cx, cy in [0,1] position the crop window inside the available pan range.
#   zoom 1.0 = full canvas; the window is (CAN_W/zoom)x(CAN_H/zoom).
# Ranges are deliberately constrained (cx 0.45-0.55, cy 0.30-0.70, zoom <= 1.45)
# so the COMPLETE original print stays inside the frame for every move —
# the camera never crops the subject, only drifts/zooms over the mount.
# ---------------------------------------------------------------------------
MOVES = {
    # Slow cinematic push-in toward the artwork, ending just past 1:1 pixels.
    "CAM_01": [(0.0, 0.50, 0.50, 1.02), (10.0, 0.50, 0.48, 1.45)],
    # Slow pull-back reveal: start tight on the print, ease out to full mount.
    "CAM_02": [(0.0, 0.50, 0.48, 1.45), (10.0, 0.50, 0.50, 1.02)],
    # Subtle left-to-right dolly at constant depth.
    "CAM_03": [(0.0, 0.45, 0.50, 1.22), (10.0, 0.55, 0.50, 1.22)],
    # Slow low-angle rise: typography -> figure -> sun, constant depth.
    "CAM_04": [(0.0, 0.50, 0.68, 1.28), (10.0, 0.50, 0.32, 1.28)],
    # Diagonal dolly: bottom-left to top-right, gentle.
    "CAM_05": [(0.0, 0.46, 0.64, 1.20), (10.0, 0.54, 0.38, 1.26)],
    # Push-in combined with subtle lateral parallax drift.
    "CAM_06": [(0.0, 0.46, 0.54, 1.08), (5.0, 0.50, 0.50, 1.24),
               (10.0, 0.54, 0.47, 1.40)],
}


def smoothstep(a, b, x):
    x = np.clip((x - a) / (b - a), 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def make_interpolator(kf):
    def interp(t):
        if t <= kf[0][0]:
            return kf[0][1], kf[0][2], kf[0][3]
        if t >= kf[-1][0]:
            return kf[-1][1], kf[-1][2], kf[-1][3]
        for i in range(len(kf) - 1):
            t0, t1 = kf[i][0], kf[i + 1][0]
            if t0 <= t <= t1:
                s = smoothstep(t0, t1, t)
                cx = kf[i][1] + (kf[i + 1][1] - kf[i][1]) * s
                cy = kf[i][2] + (kf[i + 1][2] - kf[i][2]) * s
                zz = kf[i][3] + (kf[i + 1][3] - kf[i][3]) * s
                return cx, cy, zz
        return kf[-1][1], kf[-1][2], kf[-1][3]
    return interp


def build_canvas(src_path):
    """9:16 canvas: blurred self-fill background + complete sharp image."""
    img = Image.open(src_path).convert("RGB")
    sw, sh = img.size

    # background: cover-crop, heavy blur, slight dim
    scale = max(CAN_W / sw, CAN_H / sh)
    bw, bh = int(round(sw * scale)), int(round(sh * scale))
    bg = img.resize((bw, bh), Image.LANCZOS)
    bx = (bw - CAN_W) // 2
    by = (bh - CAN_H) // 2
    bg = bg.crop((bx, by, bx + CAN_W, by + CAN_H))
    bg = bg.filter(ImageFilter.GaussianBlur(38))
    bg = bg.point(lambda v: int(v * 0.72))

    # foreground: complete image fitted to canvas width, centered vertically
    fw = CAN_W
    fh = int(round(sh * (CAN_W / sw)))
    fg = img.resize((fw, fh), Image.LANCZOS)
    fy = (CAN_H - fh) // 2
    bg.paste(fg, (0, fy))
    return bg


def render_move(canvas, kf, out_path):
    interp = make_interpolator(kf)
    n_frames = int(round(DURATION * FPS))
    cmd = [
        FFMPEG_BIN, "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{OUT_W}x{OUT_H}", "-r", str(FPS), "-i", "-",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        out_path,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(n_frames):
        t = f / FPS
        cx, cy, zz = interp(t)
        ww = CAN_W / zz
        wh = CAN_H / zz
        x = (CAN_W - ww) * cx
        y = (CAN_H - wh) * cy
        frame = canvas.crop((int(x), int(y), int(x + ww), int(y + wh)))
        frame = frame.resize((OUT_W, OUT_H), Image.LANCZOS)
        proc.stdin.write(np.asarray(frame, dtype=np.uint8).tobytes())
    proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"ffmpeg failed rc={rc} for {out_path}")


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "source.png"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "CINEMATIC_CAMERA_PACK/IMAGE_01"
    prefix = sys.argv[3] if len(sys.argv) > 3 else "IMAGE_01"
    wanted = sys.argv[4:] or list(MOVES.keys())

    os.makedirs(out_dir, exist_ok=True)
    canvas = build_canvas(src)
    for name in wanted:
        out_path = os.path.join(out_dir, f"{prefix}_{name}.mp4")
        print(f"rendering {out_path} ...", flush=True)
        render_move(canvas, MOVES[name], out_path)
        print(f"done {out_path}", flush=True)


if __name__ == "__main__":
    main()
