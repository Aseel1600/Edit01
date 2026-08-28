#!/usr/bin/env python3
"""Procedural cinematic score for the 'Milo goes to space' short.

Pure-stdlib synth (no numpy). Writes a 55.5s stereo WAV bed:
  - sustained string-ish pad on Am - F - C - G
  - sub-bass root
  - heartbeat kick that enters with the training montage
  - noise riser through the countdown, boom on liftoff
  - high shimmer once he reaches orbit
  - soft whooshes on every one of the 30 cuts
Mixed low so the narration always sits on top.
"""
import math
import struct
import wave

SR = 44100
DUR = 55.5
N = int(SR * DUR)

SHOT_COUNT = 30
SHOT_LEN = 55.0 / SHOT_COUNT  # 1.8333s

CHORDS = [
    (110.00, 130.81, 164.81),  # Am
    (87.31, 130.81, 174.61),   # F
    (130.81, 164.81, 196.00),  # C
    (98.00, 123.47, 146.83),   # G
] * 2
SEG = DUR / len(CHORDS)

# deterministic noise
_seed = 987654321


def rnd():
    global _seed
    _seed = (1103515245 * _seed + 12345) & 0x7FFFFFFF
    return (_seed / 0x3FFFFFFF) - 1.0


def env(t, start, attack, hold, release):
    if t < start or t > start + attack + hold + release:
        return 0.0
    x = t - start
    if x < attack:
        return x / attack
    if x < attack + hold:
        return 1.0
    return max(0.0, 1.0 - (x - attack - hold) / release)


cut_times = [i * SHOT_LEN for i in range(1, SHOT_COUNT)]
kick_times = [t for t in [19.6 + 0.75 * i for i in range(0, 34)] if t < 44.0]

buf = [0.0] * N
lp = 0.0
lp2 = 0.0

for i in range(N):
    t = i / SR
    s = 0.0

    # ---- pad -------------------------------------------------------------
    seg = min(int(t / SEG), len(CHORDS) - 1)
    st = seg * SEG
    a = env(t, st, 0.9, SEG - 1.8, 0.9)
    if a > 0:
        swell = 0.85 + 0.15 * math.sin(2 * math.pi * 0.07 * t)
        for k, f in enumerate(CHORDS[seg]):
            w = 2 * math.pi * f * t
            det = 2 * math.pi * (f * 1.004) * t
            voice = (
                0.50 * math.sin(w)
                + 0.42 * math.sin(det)
                + 0.16 * math.sin(2 * w)
                + 0.06 * math.sin(3 * w)
            )
            s += voice * a * swell * (0.10 if k else 0.12)

        # sub root
        s += 0.16 * math.sin(2 * math.pi * (CHORDS[seg][0] / 2) * t) * a

    # arrival shimmer (orbit)
    if t > 43.8:
        sh = env(t, 43.8, 1.6, 8.0, 2.0)
        trem = 0.6 + 0.4 * math.sin(2 * math.pi * 0.9 * t)
        s += 0.035 * sh * trem * math.sin(2 * math.pi * 1046.50 * t)
        s += 0.022 * sh * trem * math.sin(2 * math.pi * 1567.98 * t)
        s += 0.018 * sh * math.sin(2 * math.pi * 2093.00 * t)

    # ---- kick ------------------------------------------------------------
    for kt in kick_times:
        if 0 <= t - kt < 0.22:
            x = t - kt
            e = math.exp(-x * 22)
            f = 58 - 20 * (x / 0.22)
            drive = 0.30 if t > 33.0 else 0.20
            s += drive * e * math.sin(2 * math.pi * f * x)
            break

    # ---- riser through the countdown -------------------------------------
    if 33.2 < t < 41.6:
        x = (t - 33.2) / 8.4
        amp = 0.16 * (x ** 2.2)
        sweep = 180 + 1700 * (x ** 2.0)
        s += amp * math.sin(2 * math.pi * sweep * t)
        lp = lp * 0.86 + rnd() * 0.14
        s += amp * 0.9 * lp

    # ---- liftoff boom + engine rumble ------------------------------------
    if 41.3 < t < 44.6:
        x = t - 41.3
        e = math.exp(-x * 1.5)
        s += 0.42 * e * math.sin(2 * math.pi * (52 - 12 * x) * x)
        lp2 = lp2 * 0.93 + rnd() * 0.07
        s += 0.30 * e * lp2

    # ---- cut whooshes ----------------------------------------------------
    for ct in cut_times:
        if 0 <= t - (ct - 0.16) < 0.32:
            x = t - (ct - 0.16)
            e = math.sin(math.pi * (x / 0.32)) ** 2
            s += 0.055 * e * rnd()
            break

    buf[i] = s

# ---- master: gentle soft-clip + fades ------------------------------------
fade_in = int(SR * 0.6)
fade_out = int(SR * 1.6)
frames = bytearray()
for i, s in enumerate(buf):
    g = 1.0
    if i < fade_in:
        g *= i / fade_in
    if i > N - fade_out:
        g *= max(0.0, (N - i) / fade_out)
    v = math.tanh(s * 1.25 * g) * 0.72
    iv = max(-32767, min(32767, int(v * 32767)))
    frames += struct.pack("<hh", iv, iv)

with wave.open("remotion-composer/public/cat-space/score.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(bytes(frames))

print("wrote score.wav", round(DUR, 2), "s")
