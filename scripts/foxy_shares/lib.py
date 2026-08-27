"""Shared helpers for the Foxy Shares kids-cartoon render pipeline."""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from imageio_ffmpeg import get_ffmpeg_exe

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets")
IMG_DIR = os.path.join(ASSETS, "images")
FONT_DIR = os.path.join(ASSETS, "fonts")
VOICE_DIR = os.path.join(BASE, "audio", "voices")
FRAME_DIR = os.path.join(BASE, "frames")
FFMPEG = get_ffmpeg_exe()

W, H = 1080, 1920
FPS = 30

# ---------------- easing ----------------
def clamp01(x):
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)

def ease_out_cubic(x):
    x = clamp01(x); return 1 - (1 - x) ** 3

def ease_out_back(x):
    x = clamp01(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def ease_in_out_sine(x):
    x = clamp01(x); return -(math.cos(math.pi * x) - 1) / 2

def ease_out_quad(x):
    x = clamp01(x); return 1 - (1 - x) ** 2

def smoothstep(x):
    x = clamp01(x); return x * x * (3 - 2 * x)

# ---------------- color ----------------
def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

# ---------------- fonts ----------------
_font_cache = {}
def font(name, size):
    key = (name, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    return _font_cache[key]

# ---------------- text tiles ----------------
def text_tile(text, fname, size, fill, stroke, stroke_w=0, shadow=None, line_gap=1.18):
    """Render multiline text into a tight RGBA tile. Render at 2x for crispness."""
    f = font(fname, size)
    lines = text.split("\n")
    d0 = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    lw, lh = [], []
    for ln in lines:
        b = d0.textbbox((0, 0), ln, font=f, stroke_width=stroke_w)
        lw.append(b[2] - b[0]); lh.append(b[3] - b[1])
    asc, desc = f.getmetrics()
    line_h = asc + desc
    line_adv = int(line_h * line_gap)
    pad = stroke_w * 2 + int(size * 0.12)
    maxw = max(lw)
    Wt = maxw + pad * 2
    Ht = line_adv * (len(lines) - 1) + max(lh) + pad * 2
    tile = Image.new("RGBA", (Wt, Ht), (0, 0, 0, 0))
    if shadow:
        sh_col, sh_dx, sh_dy, sh_blur = shadow
        sh = Image.new("RGBA", (Wt, Ht), (0, 0, 0, 0))
        shd = ImageDraw.Draw(sh)
        y = pad
        for ln, w in zip(lines, lw):
            x = pad + (maxw - w) // 2
            shd.text((x + sh_dx, y + sh_dy), ln, font=f, fill=sh_col,
                     stroke_width=stroke_w, stroke_fill=sh_col)
            y += line_adv
        if sh_blur > 0:
            sh = sh.filter(ImageFilter.GaussianBlur(sh_blur))
        tile.alpha_composite(sh)
    d = ImageDraw.Draw(tile)
    y = pad
    for ln, w in zip(lines, lw):
        x = pad + (maxw - w) // 2
        d.text((x, y), ln, font=f, fill=fill, stroke_width=stroke_w, stroke_fill=stroke)
        y += line_adv
    return tile

def paste_scaled(base, tile, cx, cy, scale, alpha=255):
    if tile is None or scale <= 0.004:
        return
    tw = max(1, int(tile.width * scale)); th = max(1, int(tile.height * scale))
    t = tile.resize((tw, th), Image.LANCZOS)
    if alpha < 255:
        a = t.getchannel("A").point(lambda v: v * alpha // 255)
        t.putalpha(a)
    base.alpha_composite(t, (int(cx - tw / 2), int(cy - th / 2)))

# ---------------- shapes ----------------
def heart_tile(size, color):
    s = size
    n = 160
    pts = []
    for i in range(n + 1):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((x, -y))
    # normalize pts to [0,1] box
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    xmin, xmax = min(xs), max(xs); ymin, ymax = min(ys), max(ys)
    span = max(xmax - xmin, ymax - ymin)
    pad = int(s * 0.12)
    img = Image.new("RGBA", (s + pad * 2, s + pad * 2), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    poly = []
    for x, y in pts:
        px = pad + (x - xmin) / span * s
        py = pad + (y - ymin) / span * s
        poly.append((px, py))
    dr.polygon(poly, fill=color + (255,))
    return img

def sparkle_tile(size, color):
    s = size
    img = Image.new("RGBA", (s * 2, s * 2), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cx = cy = s
    outer = s; inner = s * 0.28
    pts = []
    import math as _m
    for i in range(8):
        ang = _m.pi / 4 * i - _m.pi / 2
        r = outer if i % 2 == 0 else inner
        pts.append((cx + r * _m.cos(ang), cy + r * _m.sin(ang)))
    dr.polygon(pts, fill=color + (255,))
    return img

# ---------------- image loading ----------------
def cover_resize(im, tw, th):
    """Resize+crop to exactly tw x th, keep aspect (cover)."""
    sw, sh = im.size
    scale = max(tw / sw, th / sh)
    nw, nh = max(1, int(sw * scale)), max(1, int(sh * scale))
    im = im.resize((nw, nh), Image.LANCZOS)
    x0 = (nw - tw) // 2; y0 = (nh - th) // 2
    return im.crop((x0, y0, x0 + tw, y0 + th))
