"""Build spec.json (the master timeline) from voice clip durations."""
import json, os, subprocess
from lib import BASE, FFMPEG, VOICE_DIR, FPS

def probe_dur(path):
    try:
        r = subprocess.run([FFMPEG, "-hide_banner", "-i", path],
                           capture_output=True, text=True)
        for line in (r.stderr or "").splitlines():
            if "Duration" in line:
                d = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = d.split(":")
                return int(h) * 3600 + int(m) * 60 + float(s)
    except Exception:
        pass
    return 1.0

VOICES = {
    # id -> (file, who, text, bubble color)
    "foxy_hook":     ("foxy_hook.mp3",     "Foxy",     "Whoa! The biggest berry ever!",       "#FFE0B3"),
    "foxy_mine":     ("foxy_mine.mp3",     "Foxy",     "No way! It's mine! All mine!",        "#FFE0B3"),
    "foxy_selfish":  ("foxy_selfish.mp3",  "Foxy",     "I'll keep it ALL to myself!",         "#FFE0B3"),
    "foxy_realize":  ("foxy_realize.mp3",  "Foxy",     "Wait... sharing is... actually fun!", "#FFE0B3"),
    "foxy_share":    ("foxy_share.mp3",    "Foxy",     "Let's share everything!",             "#FFE0B3"),
    "foxy_yay":      ("foxy_yay.mp3",      "Foxy",     "Yayyy! Sharing is the best!",         "#FFE0B3"),
    "bunny_hungry":  ("bunny_hungry.mp3",  "Bunny",    "I'm so hungry... one little bite?",   "#FDE7F3"),
    "bunny_thanks":  ("bunny_thanks.mp3",  "Bunny",    "Thank you, Foxy!",                    "#FDE7F3"),
    "hog_help":      ("hog_help.mp3",      "Hedgehog", "Need a hand, Foxy?",                  "#E8F1E3"),
    "hog_moral":     ("hog_moral.mp3",     "Hedgehog", "Friends make everything sweeter!",    "#E8F1E3"),
}

durs = {k: probe_dur(os.path.join(VOICE_DIR, v[0])) for k, v in VOICES.items()}

def bubble(vid, t):
    f, who, text, col = VOICES[vid]
    return {"file": f, "who": who, "text": text, "t": t,
            "dur": durs[vid] + 0.25, "color": col}

def caption(text, t, dur, color="#FFFFFF"):
    return {"text": text, "t": t, "dur": dur, "color": color}

BEATS = [
    # ---- HOOK ----
    {"id": "hook", "type": "hook", "min": 4.2, "accent": "#FF6B35",
     "images": {"a": "s1_a.png", "b": "s1_b.png", "swap": 2.2},
     "title": {"text": "FOXY'S BIG BERRY!", "t": 0.4, "dur": 3.8},
     "captions": [caption("A little fox found a GIANT berry!", 1.8, 2.4)],
     "bubbles": [bubble("foxy_hook", 0.9)],
     "sfx": [("pop", 0.2), ("sparkle", 2.2)], "hearts": False},

    # ---- BUNNY ASKS ----
    {"id": "bunny", "type": "scene", "min": 6.4, "accent": "#FF5C8A",
     "images": {"a": "s2_a.png", "b": "s2_b.png", "swap": 3.2},
     "captions": [caption("Uh oh... Foxy won't share!", 4.3, 2.3)],
     "bubbles": [bubble("bunny_hungry", 0.4), bubble("foxy_mine", 3.6)],
     "sfx": [("sad", 3.6)], "hearts": False},

    # ---- STUCK ON HILL ----
    {"id": "stuck", "type": "scene", "min": 6.6, "accent": "#7C5CFF",
     "images": {"a": "s3_a.png", "b": "s3_b.png", "swap": 3.4},
     "captions": [caption("Uh-oh! The berry is STUCK!", 1.6, 2.4)],
     "bubbles": [bubble("foxy_selfish", 0.4), bubble("hog_help", 3.6)],
     "sfx": [("thud", 2.8), ("boing", 3.0)], "hearts": False},

    # ---- REALIZATION ----
    {"id": "realize", "type": "scene", "min": 6.4, "accent": "#FFC43D",
     "images": {"a": "s4_a.png", "b": "s4_b.png", "swap": 3.4},
     "captions": [caption("Sharing is... FUN!", 4.6, 2.0)],
     "bubbles": [bubble("foxy_realize", 4.2)],
     "sfx": [("whoosh", 0.3), ("ding", 4.6), ("sparkle", 5.4)], "hearts": True},

    # ---- PICNIC ----
    {"id": "picnic", "type": "scene", "min": 7.2, "accent": "#2EC4B6",
     "images": {"a": "s5_a.png", "b": "s5_b.png", "swap": 4.4},
     "captions": [caption("YAY! Friends forever!", 6.0, 1.4)],
     "bubbles": [bubble("bunny_thanks", 0.4), bubble("hog_moral", 2.6), bubble("foxy_share", 4.4)],
     "sfx": [("ding", 4.4), ("sparkle", 5.2)], "hearts": True},

    # ---- END CARD ----
    {"id": "endcard", "type": "endcard", "min": 8.0, "accent": "#FF6B35",
     "images": {"a": "s6_bg.png", "b": "s6_bg.png", "swap": -1},
     "title": {"text": "SHARING IS SWEET!", "t": 0.5, "dur": 7.5},
     "moral": {"text": "Friends make everything sweeter!", "t": 2.4, "dur": 5.4},
     "chip": {"text": "LIKE  \u00b7  SHARE  \u00b7  SUBSCRIBE", "t": 4.8, "dur": 3.0},
     "bubbles": [bubble("foxy_yay", 0.6)],
     "sfx": [("sparkle", 0.4), ("ding", 2.4)], "hearts": True},
]

# ---- compute absolute times ----
t = 0.0
out_beats = []
for b in BEATS:
    start = t
    end = start + b["min"]
    for bb in b.get("bubbles", []):
        end = max(end, start + bb["t"] + bb["dur"] + 0.35)
    dur = end - start
    nb = dict(b)
    nb["start"] = start
    nb["end"] = end
    nb["dur"] = dur
    # make bubble times absolute
    for bb in nb.get("bubbles", []):
        bb["t"] = start + bb["t"]
        bb["end"] = bb["t"] + bb["dur"]
    out_beats.append(nb)
    t = end

total = t
spec = {
    "fps": FPS, "width": 1080, "height": 1920,
    "duration": total,
    "beats": out_beats,
    "sfx": [],  # filled below (absolute)
}
# flatten sfx to absolute
sfx_list = []
for b in out_beats:
    for name, tt in b.get("sfx", []):
        sfx_list.append({"name": name, "t": b["start"] + tt})
spec["sfx"] = sfx_list

with open(os.path.join(BASE, "spec.json"), "w") as fh:
    json.dump(spec, fh, indent=2)

print("total duration:", round(total, 2), "s  ->", int(total * FPS), "frames")
for k, v in durs.items():
    print(f"  {k:14s} {v:5.2f}s")
print("wrote spec.json")
