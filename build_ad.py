#!/usr/bin/env python3
"""RAXE — 30s viral Reels ad builder (9:16, 1080x1920, clean/premium).
Edit the copy in SCENES/text constants and swap files in assets/ — then rerun.
Requires: pillow, numpy, imageio-ffmpeg."""
import os, subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(ROOT, "assets")
W, H, FPS = 1080, 1920, 30
DUR = 30.0
N_FRAMES = int(DUR * FPS)
SR = 44100
BPM = 140.0
SPB = 60.0 / BPM

RED = (215, 52, 48)
OFFWHITE = (245, 242, 236)
BG = (14, 14, 16)
GREY = (150, 148, 144)

FB = os.path.join(A, "fonts/Montserrat-master/fonts/ttf")
F_BLACK  = lambda s: ImageFont.truetype(os.path.join(FB, "Montserrat-Black.ttf"), s)
F_XBOLD  = lambda s: ImageFont.truetype(os.path.join(FB, "Montserrat-ExtraBold.ttf"), s)
F_SEMI   = lambda s: ImageFont.truetype(os.path.join(FB, "Montserrat-SemiBold.ttf"), s)

# ---------------- ease helpers ----------------
def eo_cubic(t): return 1 - (1 - t) ** 3
def ei_cubic(t): return t ** 3
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))

# ---------------- image loading ----------------
def load_cover(path, base_w=1400):
    im = Image.open(path).convert("RGB")
    tw, th = base_w, int(base_w * H / W)
    s = max(tw / im.width, th / im.height)
    im = im.resize((int(im.width * s + 0.5), int(im.height * s + 0.5)), Image.LANCZOS)
    x = (im.width - tw) // 2; y = (im.height - th) // 2
    return im.crop((x, y, x + tw, y + th))

IMGS = {
    "hero":    load_cover(os.path.join(A, "shot1_hero_black_tee.png")),
    "cream":   load_cover(os.path.join(A, "shot2_cream_tee.png")),
    "macro":   load_cover(os.path.join(A, "shot3_macro_print.png")),
    "flatlay": load_cover(os.path.join(A, "shot4_flatlay.png")),
    "model":   load_cover(os.path.join(A, "shot5_model.png")),
}

# ---------------- camera ----------------
def cam(base, k, cx, cy):
    """Crop window of size base/k centred at (cx,cy) in base px, resize to frame."""
    bw, bh = base.size
    cw, ch = bw / k, bh / k
    cx = min(max(cx, cw / 2), bw - cw / 2)
    cy = min(max(cy, ch / 2), bh - ch / 2)
    box = (int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))
    return base.crop(box).resize((W, H), Image.LANCZOS)

def shake_amp(dt, amp=7, freq=13, decay=16):
    return (int(amp * math.sin(2 * math.pi * freq * dt) * math.exp(-decay * dt)),
            int(amp * 0.7 * math.cos(2 * math.pi * freq * dt * 0.9) * math.exp(-decay * dt)))

# ---------------- text ----------------
def draw_ctext(d, y, txt, font, fill, stroke=0, stroke_fill=(0, 0, 0), x=None, tracking=0):
    if tracking:
        widths = [d.textlength(ch, font=font) for ch in txt]
        total = sum(widths) + tracking * (len(txt) - 1)
        cx = (W - total) / 2 if x is None else x
        for ch, wch in zip(txt, widths):
            d.text((cx, y), ch, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
            cx += wch + tracking
        return total
    tw = d.textlength(txt, font=font)
    cx = (W - tw) / 2 if x is None else x
    d.text((cx, y), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return tw

_TCACHE = {}

def text_img(txt, font, fill, stroke=0, tracking=0):
    """Render tight-bbox RGBA text (cached)."""
    key = (txt, font.path, font.size, fill, stroke, tracking)
    if key in _TCACHE: return _TCACHE[key]
    pad = stroke + 8
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    if tracking:
        ws = [d0.textlength(ch, font=font) for ch in txt]
        tw = int(sum(ws) + tracking * (len(txt) - 1))
    else:
        tw = int(d0.textlength(txt, font=font))
    th = font.size + 30
    im = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if tracking:
        x = pad
        for ch, wch in zip(txt, ws):
            d.text((x, pad + 10), ch, font=font, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
            x += wch + tracking
    else:
        d.text((pad, pad + 10), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    im = im.crop(im.getbbox())
    _TCACHE[key] = im
    return im

def pop_paste(base, timg, t_start, t_now, cy, pop=0.32, dur=0.22, rise_px=26):
    """Scale-pop + fade + rise; image centred horizontally, final centre at cy."""
    dt = t_now - t_start
    if dt < 0: return
    p = eo_cubic(clamp(dt / dur))
    scale = 1 + pop * (1 - p)
    lw, lh = timg.size
    nw, nh = max(1, int(lw * scale)), max(1, int(lh * scale))
    tmp = timg.resize((nw, nh), Image.LANCZOS) if scale != 1 else timg
    if p < 1:
        tmp = tmp.copy()
        tmp.putalpha(tmp.getchannel("A").point(lambda v: int(v * p)))
    rise = int((1 - p) * rise_px)
    base.alpha_composite(tmp, ((W - nw) // 2, int(cy - nh / 2) + rise))

def wordmark_img():
    if "wm" in _TCACHE: return _TCACHE["wm"]
    f = F_BLACK(300)
    a = text_img("RAXE", f, OFFWHITE, 6)
    b = text_img(".", f, RED, 6)
    # align on text baseline: canvases differ in height, paste dot at bottom-right
    im = Image.new("RGBA", (a.width + b.width, a.height), (0, 0, 0, 0))
    im.alpha_composite(a, (0, 0))
    im.alpha_composite(b, (a.width, a.height - b.height))
    _TCACHE["wm"] = im
    return im

def cta_img():
    if "cta" in _TCACHE: return _TCACHE["cta"]
    f = F_XBOLD(52)
    t1 = text_img("SHOP THE DROP", f, OFFWHITE, 0)
    t2 = text_img("↗", F_XBOLD(56), RED, 0)
    gapx, padx, pady = 26, 52, 30
    w = t1.width + gapx + t2.width + padx * 2
    h = max(t1.height, t2.height) + pady * 2
    im = Image.new("RGBA", (w + 10, h + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([5, 5, w + 4, h + 4], radius=h // 2, outline=RED + (255,), width=5)
    im.alpha_composite(t1, (padx + 5, (h - t1.height) // 2 + 4))
    im.alpha_composite(t2, (padx + 5 + t1.width + gapx, (h - t2.height) // 2 + 2))
    _TCACHE["cta"] = im
    return im

def caption_block(frame, title, index, t_start, t_now):
    dt = t_now - t_start
    if dt < 0: return
    p = eo_cubic(clamp(dt / 0.3))
    a = int(255 * p)
    slide = int((1 - p) * 40)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # scrim: bottom-up dark gradient for legibility
    gh = 460
    grad = np.zeros((gh, W, 4), dtype=np.uint8)
    alpha_col = (np.linspace(140, 0, gh) ** 1.15).astype(np.uint8)[::-1][:, None]
    grad[..., 3] = np.broadcast_to(alpha_col, (gh, W))
    scrim = Image.fromarray(grad, "RGBA")
    ov.paste(scrim, (0, H - gh))
    d = ImageDraw.Draw(ov)
    x = 80 + slide
    d.rectangle([x, 1360, x + 14, 1360 + 96], fill=RED + (a,))
    d.text((x + 40, 1360), title, font=F_XBOLD(58), fill=OFFWHITE + (a,), stroke_width=2, stroke_fill=(0,0,0,a))
    d.text((x + 40, 1438), index, font=F_SEMI(34), fill=(200, 198, 193, a))
    frame.alpha_composite(ov)

def top_tag(frame, txt, t_now, t_start=0.0):
    dt = t_now - t_start
    if dt < 0: return
    p = eo_cubic(clamp(dt / 0.35))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    a = int(230 * p)
    f = F_SEMI(30)
    tw = d.textlength(txt, font=f, )
    tw = d.textlength(txt, font=f)
    x = (W - tw) / 2
    d.text((x, 130), txt, font=f, fill=(200, 198, 193, a))
    d.line([x, 178, x + tw, 178], fill=RED + (a,), width=3)
    frame.alpha_composite(ov)

# ---------------- finishing ----------------
def vignette_arr():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W / 2, H / 2
    r = np.sqrt(((xx - cx) / (W * 0.62)) ** 2 + ((yy - cy) / (H * 0.62)) ** 2)
    v = 1 - 0.28 * np.clip(r - 0.55, 0, 1) ** 1.6
    return v[..., None]

VIG = vignette_arr()

def finish(pil_im, grain=2.4):
    arr = np.asarray(pil_im.convert("RGB"), dtype=np.float32)
    arr *= VIG
    arr += np.random.normal(0, grain, (H, W, 1)).astype(np.float32)
    return np.clip(arr, 0, 255).astype(np.uint8)

# ---------------- scene timeline ----------------
# t boundaries
T0, T1, T2, T3, T4, T5, T6, T7 = 0.0, 2.133, 6.867, 11.133, 15.433, 19.70, 24.00, 27.00
TEND = 30.0
BEAT_KICKS_S4 = [15.433 + i * SPB for i in range(0, 11, 3)]

def render_frame(f):
    t = f / FPS
    im = Image.new("RGB", (W, H), BG)

    if t < T1:  # S0 hook
        ov = im.convert("RGBA")
        pop_paste(ov, text_img("STOP",    F_BLACK(190), OFFWHITE, 4), 0.4286, t, 700)
        pop_paste(ov, text_img("WEARING", F_BLACK(190), OFFWHITE, 4), 0.8571, t, 952)
        pop_paste(ov, text_img("BASIC.",  F_BLACK(190), RED,      4), 1.2857, t, 1204)
        im = ov.convert("RGB")
        if t >= T1 - 2 / FPS:  # white flash out
            im = Image.new("RGB", (W, H), (235, 233, 228))

    elif t < T2:  # S1 hero tee
        dt = t - T1
        k = 1.02 + 0.10 * eo_cubic(clamp(dt / (T2 - T1)))
        dtp = max(0.0, dt - 0.0)
        off = shake_amp(dtp) if dt < 0.25 else (0, 0)
        base = IMGS["hero"]
        bw, bh = base.size
        im = cam(base, k, bw / 2 + off[0], bh / 2 + 20 + off[1] - 30 * eo_cubic(clamp(dt / (T2 - T1))))
        # shine sweep
        sp = clamp((dt - 1.9) / 0.7)
        if 0 < sp < 1:
            arr = np.asarray(im, dtype=np.float32)
            xpos = int(sp * (W + 700) - 350)
            xx = np.arange(W, dtype=np.float32)[None, :]
            band = np.exp(-((xx - xpos) ** 2) / (2 * 130 ** 2)) * 26
            arr = np.clip(arr + band[..., None] * 0.9, 0, 255)
            im = Image.fromarray(arr.astype(np.uint8))
        ov = im.convert("RGBA")
        caption_block(ov, "THE ONI TEE", "01 — HEAVYWEIGHT DROP-SHOULDER", T1 + 0.35, t)
        top_tag(ov, "RAXE", t, T1 + 0.1)
        im = ov.convert("RGB")

    elif t < T3:  # S2 macro
        dt = t - T2
        dur = T3 - T2
        k = 1.18 - 0.10 * eo_cubic(clamp(dt / dur))
        bw, bh = IMGS["macro"].size
        cx = bw / 2 + (eo_cubic(clamp(dt / dur)) - 0.5) * 140
        im = cam(IMGS["macro"], k, cx, bh / 2)
        ov = im.convert("RGBA")
        pop_paste(ov, text_img("HEAVY COTTON.",    F_BLACK(96), OFFWHITE, 3), T2 + 0.3, t, 870, pop=0.14)
        pop_paste(ov, text_img("PRINT THAT POPS.", F_BLACK(96), RED,      3), T2 + 2.1, t, 1060, pop=0.14)
        im = ov.convert("RGB")

    elif t < T4:  # S3 cream tee
        dt = t - T3
        dur = T4 - T3
        k = 1.14 - 0.10 * eo_cubic(clamp(dt / dur))
        bw, bh = IMGS["cream"].size
        im = cam(IMGS["cream"], k, bw / 2, bh / 2 + 10)
        ov = im.convert("RGBA")
        caption_block(ov, "THE KATANA TEE", "02 — MINIMAL LINE ART", T3 + 0.35, t)
        top_tag(ov, "RAXE", t, T3 + 0.1)
        im = ov.convert("RGB")
        if t >= T4 - 3 / FPS:  # red flash out into the drop
            a = (t - (T4 - 3 / FPS)) / (3 / FPS)
            red = Image.new("RGB", (W, H), RED)
            im = Image.blend(im, red, 0.25 + 0.75 * a)

    elif t < T5:  # S4 model (the drop)
        dt = t - T4
        dur = T5 - T4
        k = 1.03 + 0.09 * eo_cubic(clamp(dt / dur))
        off = (0, 0)
        for kb in BEAT_KICKS_S4:
            dtk = t - kb
            if 0 <= dtk < 0.35:
                s = shake_amp(dtk, amp=8)
                off = (off[0] + s[0], off[1] + s[1])
        bw, bh = IMGS["model"].size
        im = cam(IMGS["model"], k, bw / 2 + off[0], bh / 2 - 40 + off[1])
        ov = im.convert("RGBA")
        pop_paste(ov, text_img("WEAR",         F_BLACK(150), OFFWHITE, 5), T4 + 0.4286, t, 845)
        pop_paste(ov, text_img("YOUR ANIME.",  F_BLACK(150), RED,      5), T4 + 0.8571, t, 1070)
        im = ov.convert("RGB")

    elif t < T6:  # S5 flatlay lineup
        dt = t - T5
        dur = T6 - T5
        k = 1.30
        bw, bh = IMGS["flatlay"].size
        p = eo_cubic(clamp(dt / dur))
        cy = bh * (0.30 + 0.42 * p)
        im = cam(IMGS["flatlay"], k, bw / 2, cy)
        ov = im.convert("RGBA")
        caption_block(ov, "THE FULL DROP", "03 DESIGNS — ONE RELEASE", T5 + 0.3, t)
        im = ov.convert("RGB")

    elif t < T7:  # S6 urgency
        ov = im.convert("RGBA")
        pop_paste(ov, text_img("LIMITED", F_BLACK(200), OFFWHITE, 4), T6 + 0.5, t, 830)
        pop_paste(ov, text_img("DROP.",   F_BLACK(200), RED,      4), T6 + 1.3571, t, 1072)
        pop_paste(ov, text_img("ONCE IT'S GONE, IT'S GONE.", F_SEMI(38), GREY, 0), T6 + 2.2, t, 1560, pop=0.1, dur=0.3, rise_px=18)
        im = ov.convert("RGB")

    else:  # S7 logo lockup
        ov = im.convert("RGBA")
        wm = wordmark_img()
        pop_paste(ov, wm, T7 + 0.25, t, 880, pop=0.30, dur=0.28, rise_px=30)
        pop_paste(ov, text_img("ANIME STREETWEAR", F_XBOLD(44), (190, 188, 183), 0, tracking=18),
                  T7 + 0.95, t, 1180, pop=0.12, dur=0.3, rise_px=18)
        pop_paste(ov, cta_img(), T7 + 1.65, t, 1352, pop=0.14, dur=0.3, rise_px=20)
        pop_paste(ov, text_img("@RAXE", F_SEMI(40), (125, 123, 119), 0), T7 + 2.15, t, 1500, pop=0.08, dur=0.3, rise_px=14)
        im = ov.convert("RGB")
        if t > TEND - 0.497:  # final hit → fade to black
            a = clamp((t - (TEND - 0.5)) / 0.4)
            im = Image.blend(im, Image.new("RGB", (W, H), (0, 0, 0)), a)

    return finish(im)

# ---------------- audio ----------------
def adsr(n, a, d, s_level, s_frac, r, sr=SR):
    env = np.ones(n, dtype=np.float32) * s_level
    na, nd, nr = int(a * sr), int(d * sr), int(r * sr)
    ns = max(0, n - na - nd - nr)
    idx = 0
    if na > 0:
        env[:na] = np.linspace(0, 1, na); idx = na
    if nd > 0:
        env[idx:idx+nd] = np.linspace(1, s_level, nd); idx += nd
    env[idx:idx+ns] = s_level; idx += ns
    if nr > 0:
        env[idx:idx+nr] = np.linspace(s_level, 0, nr)[:max(0, n - idx)]
    return env[:n]

def kick(dur=0.4):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 150 * np.exp(-t * 28) + 44
    ph = np.cumsum(2 * np.pi * f / SR)
    return np.sin(ph) * np.exp(-t * 8.5)

def bass(note_f, dur, glide_from=None):
    n = int(dur * SR); t = np.arange(n) / SR
    if glide_from:
        f = note_f + (glide_from - note_f) * np.exp(-t * 18)
    else:
        f = np.full(n, note_f, dtype=np.float32)
    ph = np.cumsum(2 * np.pi * f / SR)
    y = np.sin(ph) + 0.25 * np.sin(2 * ph) * np.exp(-t * 4)
    return y * adsr(n, 0.008, 0.1, 0.9, 1, min(0.15, dur * 0.3))

def hat(dur=0.05, open_=False):
    n = int(dur * SR)
    y = np.random.randn(n).astype(np.float32)
    y = np.diff(y, prepend=0)  # crude highpass
    env = np.exp(-np.arange(n) / SR / (0.16 if open_ else 0.018))
    return y * env * (0.5 if not open_ else 0.42)

def clap():
    n = int(0.3 * SR)
    y = np.random.randn(n).astype(np.float32)
    t = np.arange(n) / SR
    env = np.exp(-t * 22) + 0.6 * np.exp(-((t - 0.02).clip(0)) * 30) + 0.5 * np.exp(-((t - 0.041).clip(0)) * 30)
    # bandpass-ish: smooth then diff mix
    k = np.ones(24) / 24
    low = np.convolve(y, k, mode="same")
    bp = y - low
    return bp * env * 0.8

def impact(dur=1.2):
    n = int(dur * SR); t = np.arange(n) / SR
    sub = np.sin(np.cumsum(2 * np.pi * (90 * np.exp(-t * 6) + 32) / SR)) * np.exp(-t * 3.2)
    nz = np.random.randn(n).astype(np.float32)
    k = np.ones(64) / 64
    swe = np.convolve(nz, k, mode="same") * np.exp(-t * 5)
    return sub * 1.1 + swe * 0.7

def riser(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.random.randn(n).astype(np.float32)
    # sweep: varying smoothing window = crude upward filter sweep
    out = np.zeros(n, dtype=np.float32)
    chunk = int(0.05 * SR)
    for i in range(0, n, chunk):
        frc = i / n
        wn = max(2, int(200 * (1 - frc) ** 2) + 2)
        k = np.ones(wn) / wn
        seg = y[i:i+chunk]
        out[i:i+chunk] = seg - np.convolve(seg, k, mode="same")
    amp = (t / dur) ** 1.7
    tone = np.sin(2 * np.pi * (220 + 1400 * (t / dur) ** 2) * t) * 0.12 * (t / dur) ** 2
    return out * amp * 0.6 + tone

def whoosh(dur=0.22):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.random.randn(n).astype(np.float32)
    k = np.ones(48) / 48
    y = y - np.convolve(y, k, mode="same")
    env = np.sin(np.pi * t / dur) ** 2
    return y * env * 0.5

def build_audio():
    mix = np.zeros(int(DUR * SR) + SR, dtype=np.float32)
    duck = np.zeros_like(mix)

    def add(sig, t, gain=1.0):
        i = int(t * SR)
        j = min(len(mix), i + len(sig))
        mix[i:j] += sig[:j - i] * gain

    def duck_at(t, depth=0.75, rel=0.22):
        i = int(t * SR); n = int(rel * SR)
        j = min(len(duck), i + n)
        tt = np.arange(j - i) / SR
        duck[i:j] = np.maximum(duck[i:j], depth * np.exp(-tt * 16))

    bar = 4 * SPB
    n_bars = int(DUR / bar) + 1
    intro_end = T1

    for b in range(n_bars):
        t0 = b * bar
        if t0 > DUR: break
        beats = [0, 1, 2, 3]
        kt = [0] if t0 + bar < intro_end else [0, 1.75, 2.5, 3.5] if b % 2 == 0 else [0, 1.75, 3.0]
        for kb in kt:
            kt_abs = t0 + kb * SPB
            if kt_abs < DUR - 0.6:
                add(kick(), kt_abs, 0.95)
                duck_at(kt_abs)
        # clap on beat 3 (halftime)
        if t0 + 2 * SPB < DUR - 0.6 and t0 + bar > intro_end:
            add(clap(), t0 + 2 * SPB, 0.75)
        # hats: 1/8ths after intro
        if t0 + bar > intro_end - SPB:
            for e in range(8):
                ht = t0 + e * SPB / 2
                if intro_end <= ht < DUR - 0.6:
                    add(hat(open_=(e == 7 and b % 2 == 1)), ht, 0.34 if e % 2 else 0.22)

    # 808 bass line: D minor groove
    D2, F2, C2, G1 = 73.42, 87.31, 65.41, 49.0
    line = [(D2, 2 * SPB), (D2, SPB), (F2, SPB), (D2, 2 * SPB), (C2, 2 * SPB)]
    tcur = intro_end
    li = 0
    seq = line * 8
    while tcur < DUR - 0.9 and li < len(seq):
        nf, d_ = seq[li]
        glide = seq[li - 1][0] if li > 0 and seq[li - 1][0] != nf else None
        # end-of-drop pitch fall
        if tcur > DUR - 1.2: nf, glide = D2 * 0.5, D2
        add(bass(nf, min(d_, DUR - tcur), glide), tcur, 0.62)
        tcur += d_; li += 1

    # riser into the drop (S4)
    add(riser(T4 - 13.85), 13.85, 0.9)
    add(impact(), T4, 1.15); duck_at(T4, 0.9, 0.4)
    # impacts/whooshes at cuts
    add(whoosh(), T1 - 0.11, 0.8)
    add(whoosh(), T2 - 0.11, 0.6)
    add(whoosh(), T3 - 0.11, 0.6)
    add(whoosh(0.3), T5 - 0.15, 0.8)
    add(whoosh(), T6 - 0.11, 0.6)
    add(impact(0.9), T7 + 0.045, 0.9)
    add(impact(0.7), TEND - 0.5, 1.0)

    # cuts on hook word pops get a muted kick pulse
    for wp in (0.4286, 0.8571, 1.2857):
        add(kick(0.3), wp, 0.8); duck_at(wp, 0.6)

    # sidechain
    mix = mix * (1 - 0.55 * np.clip(duck, 0, 1))
    # master fade out
    fo = int(0.55 * SR)
    mix[-fo:] *= np.linspace(1, 0, fo)
    mix = mix[: int(DUR * SR)]
    # soft clip + normalize
    mix = np.tanh(mix * 1.15)
    mix /= max(1e-6, np.abs(mix).max()) / 0.96
    return (mix * 32767).astype(np.int16)

def write_wav(path, pcm):
    import wave
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())

# ---------------- main ----------------
def main():
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    wav = os.path.join(ROOT, "assets", "_score.wav")
    print("scoring…", flush=True)
    write_wav(wav, build_audio())

    out = os.path.join(ROOT, "raxe_ad_30s.mp4")
    cmd = [ffmpeg, "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav,
           "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    qc = {39, 120, 260, 400, 520, 660, 770, 860}
    os.makedirs(os.path.join(ROOT, "qc"), exist_ok=True)
    print("rendering frames…", flush=True)
    for f in range(N_FRAMES):
        fr = render_frame(f)
        if f in qc:
            Image.fromarray(fr).save(os.path.join(ROOT, "qc", f"f{f:04d}.jpg"), quality=88)
        proc.stdin.write(fr.tobytes())
        if f % 90 == 0:
            print(f"  {f}/{N_FRAMES}", flush=True)
    proc.stdin.close(); proc.wait()
    # cover frame
    Image.fromarray(render_frame(852)).save(os.path.join(ROOT, "cover.jpg"), quality=92)
    print("done:", out, flush=True)
    r = subprocess.run([ffmpeg, "-i", out], capture_output=True, text=True)
    tail = [l for l in r.stderr.splitlines() if "Duration" in l or "Video:" in l or "Audio:" in l]
    print("\n".join(tail), flush=True)

if __name__ == "__main__":
    main()
