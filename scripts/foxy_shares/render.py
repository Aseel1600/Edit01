"""Render the Foxy Shares cartoon to PNG frames (1080x1920 @ 30fps)."""
import json, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from lib import (BASE, IMG_DIR, FRAME_DIR, W, H, FPS, hex_rgb, mix, cover_resize,
                 text_tile, paste_scaled, heart_tile, sparkle_tile,
                 ease_out_back, ease_out_cubic, ease_in_out_sine, ease_out_quad, smoothstep)

spec = json.load(open(os.path.join(BASE, "spec.json")))
TOTAL = spec["duration"]
NF = int(TOTAL * FPS)
CROSS = 0.30  # crossfade between beats

# work resolution for ken-burns headroom (1.5x canvas)
WW, WH = 1620, 2880

def load(img):
    im = Image.open(os.path.join(IMG_DIR, img)).convert("RGB")
    return cover_resize(im, WW, WH).convert("RGBA")

imgs = {}
for b in spec["beats"]:
    if b.get("images"):
        for k in ("a", "b"):
            imgs[(b["id"], k)] = load(b["images"][k])

# ---------------- cached text tiles (rendered 2x) ----------------
# captions: Luckiest Guy, white with colored outline + soft shadow
# titles:   Luckiest Guy, white with orange outline + shadow
# moral:    Baloo 2 ExtraBold
# chip:     Baloo 2 Bold
# bubbles:  Patrick Hand + rounded rect + tail

BUBBLE_SCALE_BASE = 0.5  # tiles rendered at 2x, shown at 0.5x => effective 1x

def make_caption_tiles():
    d = {}
    for b in spec["beats"]:
        for c in b.get("captions", []):
            acc = hex_rgb(b["accent"])
            dark = (50, 34, 26)
            d[id(c)] = text_tile(c["text"], "luckiest-guy.ttf", 156, (255, 255, 255),
                                 acc, stroke_w=16, shadow=(dark, 8, 10, 8))
        if b.get("title"):
            t = b["title"]
            d[id(t)] = text_tile(t["text"], "luckiest-guy.ttf", 208, (255, 255, 255),
                                 hex_rgb(b["accent"]), stroke_w=22, shadow=((40, 26, 16), 10, 12, 10))
        if b.get("moral"):
            m = b["moral"]
            d[id(m)] = text_tile(m["text"], "baloo2-extrabold.ttf", 92, (255, 255, 255),
                                 (255, 140, 90), stroke_w=10, shadow=((40, 26, 16), 6, 8, 8))
        if b.get("chip"):
            ch = b["chip"]
            d[id(ch)] = text_tile(ch["text"], "baloo2-bold.ttf", 64, (255, 255, 255),
                                  (255, 107, 53), stroke_w=8, shadow=((40, 26, 16), 5, 6, 6))
    return d

def make_bubble_tiles():
    d = {}
    dark = (58, 42, 34)
    textcol = (74, 46, 27)
    for b in spec["beats"]:
        for bb in b.get("bubbles", []):
            tint = hex_rgb(bb["color"])
            fill = mix((255, 255, 255), tint, 0.35)
            t = text_tile(bb["text"], "patrick-hand.ttf", 104, textcol, dark, stroke_w=4)
            pad = 46
            tw, th = t.width, t.height
            bw, bh = tw + pad * 2, th + pad * 2
            tile = Image.new("RGBA", (bw, bh + 70), (0, 0, 0, 0))
            dr = ImageDraw.Draw(tile)
            r = 46
            dr.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=r,
                                 fill=fill + (255,), outline=dark + (255,), width=10)
            # tail (pointing down)
            cx = bw // 2
            dr.polygon([(cx - 46, bh - 8), (cx + 46, bh - 8), (cx, bh + 62)],
                       fill=fill + (255,))
            dr.line([(cx - 46, bh - 8), (cx, bh + 62), (cx + 46, bh - 8)],
                    fill=dark + (255,), width=8)
            # redraw rounded rect top over the tail seam
            dr.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=r,
                                 outline=dark + (255,), width=10)
            tile.alpha_composite(t, (pad, pad))
            d[id(bb)] = tile
    return d

CAP = make_caption_tiles()
BUB = make_bubble_tiles()

# ---------------- endcard background ----------------
def make_endcard_bg():
    img = Image.new("RGBA", (W, H))
    dr = ImageDraw.Draw(img)
    top = hex_rgb("#FFD9A0"); mid = hex_rgb("#FFB1B8"); bot = hex_rgb("#FF8FB3")
    for y in range(H):
        tt = y / H
        if tt < 0.5:
            c = mix(top, mid, tt * 2)
        else:
            c = mix(mid, bot, (tt - 0.5) * 2)
        dr.line([(0, y), (W, y)], fill=c + (255,))
    # bokeh circles
    rng = np.random.default_rng(3)
    for _ in range(46):
        x = int(rng.uniform(0, W)); y = int(rng.uniform(0, H))
        r = int(rng.uniform(20, 90))
        col = (255, 255, 255, int(rng.uniform(14, 34)))
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(lay).ellipse([x - r, y - r, x + r, y + r], fill=col)
        lay = lay.filter(ImageFilter.GaussianBlur(r * 0.55))
        img.alpha_composite(lay)
    return img

ENDCARD_BG = make_endcard_bg()

def make_bottom_shade():
    """Bottom gradient for text legibility over the end-card background."""
    sh = Image.new("RGBA", (W, H), (58, 26, 58, 255))
    a = np.zeros((H, W), dtype=np.uint8)
    start = int(H * 0.44)
    if H - start > 0:
        ramp = np.linspace(0, 175, H - start, dtype=np.uint8)
        a[start:, :] = ramp[:, None]
    sh.putalpha(Image.fromarray(a, "L"))
    return sh

ENDCARD_SHADE = make_bottom_shade()

# ---------------- hearts / sparkles ----------------
HEART_COLORS = [(255, 107, 107), (255, 153, 178), (255, 214, 90), (255, 130, 160)]
heart_imgs = [heart_tile(s, c) for s, c in
              [(96, HEART_COLORS[0]), (120, HEART_COLORS[1]), (80, HEART_COLORS[2]), (140, HEART_COLORS[3])]]
spark_imgs = [sparkle_tile(s, (255, 244, 180)) for s in (70, 110, 50)]
SPARK_IMG = sparkle_tile(120, (255, 240, 170))

def floating_particles(beat, tl, canvas):
    """Deterministic floating hearts/sparkles."""
    if not beat.get("hearts"):
        return
    seed = hash(beat["id"]) & 0xFFFF
    rng = np.random.default_rng(seed)
    n = 16 if beat["type"] != "endcard" else 26
    for i in range(n):
        # per-particle params (deterministic)
        x0 = rng.uniform(60, W - 60)
        speed = rng.uniform(70, 170)
        size = rng.uniform(0.7, 1.4)
        amp = rng.uniform(10, 40)
        freq = rng.uniform(0.5, 1.2)
        phase = rng.uniform(0, 2 * math.pi)
        start = rng.uniform(0, beat["dur"] * 0.8)
        life = beat["dur"] - start
        lt = tl - start
        if lt < 0 or lt > life:
            continue
        prog = lt / life
        y = H + 80 - prog * (H + 200)
        x = x0 + amp * math.sin(2 * math.pi * freq * lt + phase)
        a = int(255 * math.sin(math.pi * prog))
        if a <= 0:
            continue
        is_heart = (i % 3 != 0)
        tile = heart_imgs[i % len(heart_imgs)] if is_heart else SPARK_IMG
        sc = size * (1.0 if is_heart else 0.55)
        paste_scaled(canvas, tile, x, y, sc, alpha=a)

# ---------------- ken burns image ----------------
def kenburns_img(work, tl, dur, z0=1.0, z1=1.18, pan=0.03):
    p = tl / max(dur, 1e-6)
    e = ease_in_out_sine(p)
    z = z0 + (z1 - z0) * e
    cw, ch = work.width / z, work.height / z
    x0 = (work.width - cw) / 2
    y0 = (work.height - ch) * (0.5 + (e - 0.5) * pan * 2)
    x0 = max(0, min(work.width - cw, x0)); y0 = max(0, min(work.height - ch, y0))
    box = (int(x0), int(y0), int(x0 + cw), int(y0 + ch))
    return work.crop(box).resize((W, H), Image.LANCZOS)

def render_beat(beat, tl):
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if beat["type"] in ("scene", "hook"):
        a = imgs[(beat["id"], "a")]; b = imgs[(beat["id"], "b")]
        z0, z1 = 1.0, 1.16
        frame = kenburns_img(a, tl, beat["dur"], z0, z1)
        swap = beat["images"]["swap"]
        if swap and swap >= 0:
            alpha = smoothstep((tl - swap) / 0.5)
            if alpha > 0:
                fb = kenburns_img(b, tl, beat["dur"], z0, z1)
                frame = Image.blend(frame, fb, min(alpha, 1.0))
        canvas.alpha_composite(frame)
    elif beat["type"] == "endcard":
        if beat.get("images") and (beat["id"], "a") in imgs:
            bg = imgs[(beat["id"], "a")]
            canvas.alpha_composite(kenburns_img(bg, tl, beat["dur"], 1.0, 1.10, 0.04))
            canvas.alpha_composite(ENDCARD_SHADE)
        else:
            canvas.alpha_composite(ENDCARD_BG)

    # title
    if beat.get("title"):
        t = beat["title"]
        tt = tl - t["t"]
        tile = CAP[id(t)]
        if 0 <= tt <= t["dur"]:
            pop = ease_out_back(min(1.0, tt / 0.5))
            bob = 1.0 + 0.012 * math.sin((tl - t["t"]) * 3.0)
            sc = 0.5 * pop * bob
            cy = H * 0.24
            paste_scaled(canvas, tile, W / 2, cy, sc)
            if tt > t["dur"] - 0.4:
                fade = ease_out_cubic((t["dur"] - tt) / 0.4)
                canvas = Image.blend(canvas, canvas_prev(canvas), 0)  # noop keep
                # simple fade handled by not drawing near end
    # moral
    if beat.get("moral"):
        m = beat["moral"]
        tt = tl - m["t"]
        tile = CAP[id(m)]
        if 0 <= tt <= m["dur"]:
            pop = ease_out_back(min(1.0, tt / 0.6))
            sc = 0.5 * pop
            paste_scaled(canvas, tile, W / 2, H * 0.62, sc)
    # chip
    if beat.get("chip"):
        ch = beat["chip"]
        tt = tl - ch["t"]
        tile = CAP[id(ch)]
        if 0 <= tt <= ch["dur"]:
            pop = ease_out_back(min(1.0, tt / 0.5))
            sc = 0.5 * pop
            paste_scaled(canvas, tile, W / 2, H * 0.80, sc)
    # captions
    for c in beat.get("captions", []):
        tt = tl - c["t"]
        tile = CAP[id(c)]
        if 0 <= tt <= c["dur"]:
            pop = ease_out_back(min(1.0, tt / 0.4))
            sc = 0.5 * pop
            paste_scaled(canvas, tile, W / 2, H * 0.845, sc)
    # bubbles
    for bb in beat.get("bubbles", []):
        tt = tl - bb["t"]
        tile = BUB[id(bb)]
        if 0 <= tt <= bb["dur"]:
            pop = ease_out_back(min(1.0, tt / 0.3))
            sc = BUBBLE_SCALE_BASE * pop
            cy = H * 0.16
            paste_scaled(canvas, tile, W / 2, cy, sc)
        elif -0.3 <= tt < 0:
            pass
    # particles
    floating_particles(beat, tl, canvas)
    return canvas

def canvas_prev(c):
    return c

def vignette():
    x = np.linspace(-1, 1, W, dtype=np.float32)
    y = np.linspace(-1.6, 1.6, H, dtype=np.float32)
    X, Y = np.meshgrid(x, y)
    r = np.sqrt(X ** 2 + (Y / 1.6) ** 2)
    m = np.clip(r, 0, 1.0)
    a = (np.clip(m - 0.55, 0, 1) * 90).astype(np.uint8)
    alpha = Image.fromarray(a, mode="L")
    black = Image.new("RGBA", (W, H), (20, 10, 20, 255))
    black.putalpha(alpha)
    return black

VIG = vignette()

os.makedirs(FRAME_DIR, exist_ok=True)
print("rendering", NF, "frames ...")
def main():
    for fi in range(NF):
        t = fi / FPS
        # find active beat
        bi = 0
        for idx, b in enumerate(spec["beats"]):
            if b["start"] <= t < b["end"]:
                bi = idx; break
        else:
            bi = len(spec["beats"]) - 1
        beat = spec["beats"][bi]
        tl = t - beat["start"]
        canvas = render_beat(beat, tl)
        # crossfade into next beat
        nxt = spec["beats"][bi + 1] if bi + 1 < len(spec["beats"]) else None
        if nxt and (beat["end"] - t) < CROSS:
            p = 1 - (beat["end"] - t) / CROSS
            ncanvas = render_beat(nxt, t - nxt["start"])
            canvas = Image.blend(canvas, ncanvas, smoothstep(p))
        canvas.alpha_composite(VIG)
        canvas.convert("RGB").save(os.path.join(FRAME_DIR, f"{fi:05d}.png"), compress_level=1)
        if fi % 200 == 0:
            print(f"  frame {fi}/{NF} ({t:.1f}s)")
    print("done frames")

if __name__ == "__main__":
    main()
