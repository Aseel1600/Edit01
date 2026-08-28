#!/usr/bin/env python3
"""
Cinematic camera-move renderer for a single still image.

Produces a 1920x1080 @30fps MP4 by driving a virtual camera (pan + zoom)
over the source image using smoothly-eased keyframes, then piping raw frames
into ffmpeg for H.264 encoding with a light film grade.
"""
import subprocess
import sys
import numpy as np
from PIL import Image

try:
    import imageio_ffmpeg
    FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_BIN = "ffmpeg"

SRC = sys.argv[1] if len(sys.argv) > 1 else "uploads/img.png"
OUT = sys.argv[2] if len(sys.argv) > 2 else "cinematic.mp4"
DURATION = float(sys.argv[3]) if len(sys.argv) > 3 else 15.0
FPS = 30
W, H = 1920, 1080

# ---- Load source and establish a 16:9 "base" crop region ----
img = Image.open(SRC).convert("RGB")
sw, sh = img.size
# Crop to 16:9 (crop the height vertically, centered with a slight upward bias)
target_ar = W / H
base_w = sw
base_h = int(round(sw / target_ar))
if base_h > sh:                       # too tall crop -> switch to height-based
    base_h = sh
    base_w = int(round(sh * target_ar))
base_w = min(base_w, sw)
base_h = min(base_h, sh)
# center the 16:9 window vertically, bias slightly toward the upper half
top = max(0, (sh - base_h) // 2)
base = img.crop((0, top, base_w, top + base_h))  # (base_w, base_h) 16:9
BW, BH = base.size

# ---- Keyframes: (t, cx, cz, zoom)  cx,cz in [-1,1] horizontal/vertical drift
# cx,cz move the camera center within the pan range; zoom >= 1 (1 = full base frame)
KF = [
    (0.0,   0.00,  0.00, 1.00),   # start, wide, centered  (push-in begins)
    (2.5,   0.00,  0.00, 1.22),   # slow push-in
    (5.0,  -0.32,  0.00, 1.45),   # reach left for the pan
    (7.5,   0.00,  0.00, 1.45),   # pan through center
    (10.0,  0.32,  0.00, 1.45),   # pan ends right
    (12.5,  0.26,  0.05, 2.05),   # settle toward right detail, push deeper
    (15.0,  0.30,  0.06, 2.50),   # final detail push-in
]

def smoothstep(a, b, x):
    x = np.clip((x - a) / (b - a), 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)

def interp(t):
    cx = cy = zoom = 0.0
    if t <= KF[0][0]:
        return KF[0][1], KF[0][2], KF[0][3]
    if t >= KF[-1][0]:
        return KF[-1][1], KF[-1][2], KF[-1][3]
    for i in range(len(KF) - 1):
        t0 = KF[i][0]; t1 = KF[i + 1][0]
        if t0 <= t <= t1:
            s = smoothstep(t0, t1, t)
            cx = KF[i][1] + (KF[i + 1][1] - KF[i][1]) * s
            cy = KF[i][2] + (KF[i + 1][2] - KF[i][2]) * s
            zoom = KF[i][3] + (KF[i + 1][3] - KF[i][3]) * s
            break
    return cx, cy, zoom

# ---- Render frames and pipe to ffmpeg ----
cmd = [
    FFMPEG_BIN, "-y", "-loglevel", "error",
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
    "-i", "-",
    "-vf", (
        "vignette=PI/5,"
        "eq=contrast=1.06:saturation=1.12:brightness=-0.01,"
        "drawbox=x=0:y=0:w=iw:h=134:color=black:t=fill,"
        "drawbox=x=0:y=ih-134:w=iw:h=134:color=black:t=fill,"
        "noise=alls=2.5:allf=t+u"
    ),
    "-c:v", "libx264", "-preset", "slow", "-crf", "18",
    "-pix_fmt", "yuv420p", "-movflags", "+faststart",
    OUT,
]

n_frames = int(round(DURATION * FPS))
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

for f in range(n_frames):
    t = f / FPS
    cx, cy, zoom = interp(t)
    zw = BW / zoom
    zh = zw * (H / W)
    pan_w = max(0.0, BW - zw)
    pan_h = max(0.0, BH - zh)
    cxr = (cx * 0.5 + 0.5)   # 0..1
    cyr = (cy * 0.5 + 0.5)
    px = pan_w * cxr
    py = pan_h * cyr
    box = (px, py, px + zw, py + zh)
    frame = base.crop(box).resize((W, H), Image.LANCZOS)
    arr = np.asarray(frame, dtype=np.uint8)
    proc.stdin.write(arr.tobytes())
    if f % 60 == 0:
        print(f"frame {f}/{n_frames}  cx={cx:.2f} zoom={zoom:.2f}", flush=True)

proc.stdin.close()
proc.wait()
print("encode done, rc=", proc.returncode)
