"""Synthesize BGM + SFX, decode voices, and mix the full soundtrack."""
import json, os, subprocess
import numpy as np
from lib import BASE, FFMPEG, VOICE_DIR

SR = 48000
spec = json.load(open(os.path.join(BASE, "spec.json")))
DUR = spec["duration"] + 0.6
N = int(DUR * SR)

def t2i(t):
    return int(t * SR)

def place(buf, start_t, sig, gain=1.0):
    i0 = t2i(start_t)
    i1 = min(len(buf), i0 + len(sig))
    if i1 > i0:
        buf[i0:i1] += sig[:i1 - i0] * gain

# ---------------- voice decode ----------------
def load_wav(path):
    r = subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error",
                        "-i", path, "-ar", str(SR), "-ac", "1", "-f", "f32le", "-"],
                       capture_output=True)
    if r.returncode != 0 or len(r.stdout) == 0:
        print("WARN decode failed:", path, r.stderr.decode()[:200])
        return np.zeros(SR // 2, dtype=np.float32)
    return np.frombuffer(r.stdout, dtype=np.float32)

# ---------------- BGM: gentle music-box ----------------
def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)

def pluck(freq, dur, amp=1.0, bright=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    env = np.exp(-t * 6.0)
    w = np.sin(2 * np.pi * freq * t) + bright * np.sin(2 * np.pi * freq * 2 * t) + \
        0.12 * np.sin(2 * np.pi * freq * 3 * t)
    return (w * env * amp).astype(np.float32)

def pad_chord(freqs, dur, amp=0.05):
    n = int(dur * SR)
    t = np.arange(n) / SR
    att = np.clip(t / 0.5, 0, 1)
    rel = np.clip((dur - t) / 0.4, 0, 1)
    env = np.minimum(att, rel)
    w = np.zeros(n, dtype=np.float32)
    for f in freqs:
        w += np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2 * t)
    return (w * env * amp).astype(np.float32)

EIGHTH = 0.24
melody = [  # (midi, eighths) - C pentatonic, cheerful
    (72, 1), (76, 1), (79, 1), (84, 1), (79, 1), (76, 1), (72, 1), (76, 1),
    (74, 1), (76, 1), (79, 1), (81, 1), (79, 1), (76, 1), (74, 1), (72, 1),
    (72, 1), (74, 1), (76, 1), (79, 1), (81, 1), (84, 1), (81, 1), (79, 1),
    (76, 1), (79, 1), (84, 1), (88, 1), (84, 1), (79, 1), (76, 1), (72, 1),
]
chords = [  # per bar: (bass midi, chord midis)
    (48, [60, 64, 67]),
    (43, [55, 59, 62]),
    (45, [57, 60, 64]),
    (41, [53, 57, 60]),
]
BAR_EIGHTHS = 8

bgm = np.zeros(N, dtype=np.float32)
tcur = 0.05
bar = 0
i = 0
loop = 0
while tcur < DUR - 0.5:
    # chord / bass at bar start
    if i % BAR_EIGHTHS == 0:
        bass, chord = chords[bar % 4]
        place(bgm, tcur, pluck(midi(bass), EIGHTH * 6, 0.55, 0.2))
        place(bgm, tcur, pad_chord([midi(c) for c in chord], EIGHTH * BAR_EIGHTHS, 0.035))
        bar += 1
    m, e = melody[i % len(melody)]
    # lift melody an octave on the final loop for a happy ending
    mm = m + (12 if loop >= 2 else 0)
    place(bgm, tcur, pluck(midi(mm), EIGHTH * e * 1.9, 0.5, 0.45))
    tcur += EIGHTH * e
    i += 1
    if i % len(melody) == 0:
        loop += 1

# fade in/out bgm
fi = t2i(0.3); bgm[:fi] *= np.linspace(0, 1, fi)
fo = t2i(1.6); bgm[-fo:] *= np.linspace(1, 0, fo)

# ---------------- SFX ----------------
def sfx_pop():
    n = int(0.12 * SR); t = np.arange(n) / SR
    f = 200 + 900 * (t / 0.12)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22)).astype(np.float32)

def sfx_sparkle():
    out = np.zeros(int(0.5 * SR), dtype=np.float32)
    for k, m in enumerate([81, 84, 88, 93]):
        sig = pluck(midi(m), 0.4, 0.25, 0.6)
        place(out, k * 0.055, sig)
    return out

def sfx_ding():
    n = int(1.4 * SR); t = np.arange(n) / SR
    w = np.sin(2 * np.pi * 1320 * t) * np.exp(-t * 3.0) + \
        0.5 * np.sin(2 * np.pi * 1980 * t) * np.exp(-t * 5.0) + \
        0.25 * np.sin(2 * np.pi * 2640 * t) * np.exp(-t * 8.0)
    return (w * 0.6).astype(np.float32)

def sfx_boing():
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 500 * (1 - 0.6 * np.sin(np.pi * t / 0.45))
    w = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return (w * np.exp(-t * 6) * 0.5).astype(np.float32)

def sfx_whoosh():
    n = int(0.5 * SR); t = np.arange(n) / SR
    rng = np.random.default_rng(7)
    noise = rng.standard_normal(n).astype(np.float32)
    env = np.sin(np.pi * t / 0.5) ** 2
    # crude bandpass: difference (highpass) then moving average (lowpass)
    hp = np.diff(noise, prepend=0)
    k = int(0.004 * SR)
    lp = np.convolve(hp, np.ones(k) / k, mode="same")
    return (lp * env * 0.7).astype(np.float32)

def sfx_sad():
    n = int(0.7 * SR); t = np.arange(n) / SR
    f = np.linspace(420, 220, n)
    w = np.sin(2 * np.pi * np.cumsum(f) / SR)
    vib = 1 + 0.02 * np.sin(2 * np.pi * 6 * t)
    return (w * vib * np.exp(-t * 1.2) * 0.5).astype(np.float32)

def sfx_thud():
    n = int(0.3 * SR); t = np.arange(n) / SR
    w = np.sin(2 * np.pi * 90 * t) * np.exp(-t * 16)
    click = np.zeros(n, dtype=np.float32); click[:int(0.01 * SR)] = 1
    return ((w + click) * 0.8).astype(np.float32)

SFX = {"pop": sfx_pop, "sparkle": sfx_sparkle, "ding": sfx_ding, "boing": sfx_boing,
       "whoosh": sfx_whoosh, "sad": sfx_sad, "thud": sfx_thud}

sfxbuf = np.zeros(N, dtype=np.float32)
for s in spec["sfx"]:
    fn = SFX.get(s["name"])
    if fn:
        place(sfxbuf, s["t"], fn(), 1.0)

# ---------------- voices ----------------
voicebuf = np.zeros(N, dtype=np.float32)
voice_intervals = []
for b in spec["beats"]:
    for bb in b.get("bubbles", []):
        sig = load_wav(os.path.join(VOICE_DIR, bb["file"]))
        if sig.max() > 0:
            sig = sig / (np.abs(sig).max() + 1e-6) * 0.85
        place(voicebuf, bb["t"], sig)
        voice_intervals.append((bb["t"], bb["end"]))

# ---------------- ducking ----------------
duck = np.zeros(N, dtype=np.float32)
for a, b in voice_intervals:
    duck[t2i(a):t2i(b)] = 1.0
k = int(0.06 * SR)
duck = np.convolve(duck, np.ones(k) / k, mode="same")
bgm *= (1.0 - 0.62 * duck)

# ---------------- final mix ----------------
mix = bgm * 0.5 + voicebuf + sfxbuf * 0.8
mix = np.clip(mix, -1.0, 1.0)
mix = mix / (np.abs(mix).max() + 1e-6) * 0.96

stereo = np.stack([mix, mix], axis=1)
pcm = (stereo * 32767).astype(np.int16)

import wave
out = os.path.join(BASE, "audio", "final_mix.wav")
with wave.open(out, "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes(pcm.tobytes())
print("wrote", out, f"{len(mix)/SR:.2f}s")
