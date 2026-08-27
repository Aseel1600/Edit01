# Foxy's Big Berry — kids-cartoon short pipeline

A self-contained, key-free pipeline that renders a **44-second vertical (9:16) kids
cartoon short**: a brave little fox finds a giant strawberry, refuses to share,
gets it stuck, then learns that *"sharing is sweet"*.

Everything is deterministic and local:

- **Art** — 11 AI-generated stills (colorful flat cartoon), locked to a single
  character reference sheet for design consistency. Regenerate the stills with
  any image model using the prompts below.
- **Voices** — 3 character voices (Foxy, Bunny, Hedgehog) as plain MP3 clips.
  Any TTS works; the pipeline only needs the files named as listed.
- **Music + SFX** — synthesized in `audio.py` (music-box melody, pop / sparkle /
  ding / boing / whoosh / sad / thud), no audio assets required.
- **Render** — `render.py` draws every frame with Pillow (Ken Burns motion,
  speech bubbles, kinetic captions, floating hearts, crossfades) and encodes with
  a static ffmpeg (via `imageio-ffmpeg`), so **no system ffmpeg and no API keys
  are needed**.

## Pipeline overview

```
spec.py   -> spec.json            # build the master timeline from voice clip durations
audio.py  -> audio/final_mix.wav  # BGM + SFX + ducked voice mix
render.py -> frames/*.png         # 1080x1920 @ 30fps frame sequence
ffmpeg    -> foxy-shares.mp4      # H.264 + AAC, 9:16
```

## Folder layout (relative to this directory)

```
assets/
  images/            # the 11 generated stills (see "Art prompts")
  fonts/             # chunky kid-friendly TTFs (see "Fonts")
audio/
  voices/            # 10 dialogue MP3s (see "Voice lines")
```

Run from this directory (the assets listed above are already included):

```bash
pip install pillow numpy imageio-ffmpeg fonttools brotli   # fonttools/brotli only for font conversion
python spec.py                       # writes spec.json + prints per-clip durations
python audio.py                      # writes audio/final_mix.wav
python render.py                     # writes frames/*.png (~1.3k frames; delete after encode)
FF=$(python -c "from imageio_ffmpeg import get_ffmpeg_exe; print(get_ffmpeg_exe())")
"$FF" -y -framerate 30 -i frames/%05d.png -i audio/final_mix.wav \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -profile:v high \
  -c:a aac -b:a 192k -shortest -movflags +faststart foxy-shares.mp4
```

The render loop is gated under `if __name__ == "__main__":`, so the modules can be
imported for previews/tests without triggering a full render.

## Story beats

| # | Beat | Images | Key dialogue |
|---|---|---|---|
| 1 | Hook — fox finds a giant berry | `s1_a.png` → `s1_b.png` | "Whoa! The biggest berry ever!" |
| 2 | Bunny asks for a bite | `s2_a.png` → `s2_b.png` | "I'm so hungry… one little bite?" / "No way! It's mine!" |
| 3 | The berry gets stuck | `s3_a.png` → `s3_b.png` | "I'll keep it ALL to myself!" / "Need a hand, Foxy?" |
| 4 | Realization | `s4_a.png` → `s4_b.png` | "Wait… sharing is… actually fun!" |
| 5 | Picnic + group hug | `s5_a.png` → `s5_b.png` | "Let's share everything!" |
| 6 | End card | `s6_bg.png` | "Yayyy! Sharing is the best!" |

## Art prompts

Generate a **character reference sheet** first, then pass it as the image
reference for every scene so the three characters stay on-model.

> Style constant (append to every prompt): *Cute 2D flat vector kids cartoon,
> soft cel shading, bright saturated candy colors, big sparkly expressive eyes,
> rounded chubby shapes, clean bold dark outlines, storybook illustration,
> Pixar-like charm, kawaii. Vertical 9:16 composition, no text, no words, no letters.*

1. `ref_sheet.png` — **reference sheet**: orange fox cub (red bandana, white chest,
   white-tipped tail), cream-white bunny (floppy pink-tipped ears, rosy cheeks),
   round brown hedgehog (cream face/belly). Full body, side by side, plain pastel-blue bg.
2. `s1_a.png` — fox, jaw dropped, staring at an enormous glossy red strawberry twice
   his size, sparkles around it.
3. `s1_b.png` — fox hugging the giant strawberry with both arms, eyes sparkling with joy.
4. `s2_a.png` — bunny rubbing her tummy, shy hopeful smile, looking at the berry.
5. `s2_b.png` — fox hugging the berry protectively and turning away with a pout;
   bunny sad with drooping ears and teary eyes beside him.
6. `s3_a.png` — fox straining to push the berry up a steep hill, cheeks puffed,
   sweat drops, berry wedged between two rocks.
7. `s3_b.png` — berry stuck on the hill against a tree root; fox slumped tired;
   hedgehog walking in, waving and smiling.
8. `s4_a.png` — fox and hedgehog pushing the berry together, it pops free with
   motion lines and sparkles.
9. `s4_b.png` — fox, paws on cheeks, eyes huge and sparkling, pink hearts floating
   around his head (realization).
10. `s5_a.png` — the three friends on a red checkered picnic blanket under a tree,
    eating strawberry slices, golden sunset.
11. `s5_b.png` — the three friends in a happy group hug, hearts floating up, a
    partly eaten berry beside them.
12. `s6_bg.png` — dreamy sunset-meadow background, pink-orange gradient sky, bokeh
    sparkles and tiny hearts, a distant tree, **no characters**.

## Voice lines

Place these MP3s in `audio/voices/` (durations are probed automatically; the
timeline is built around them):

| File | Voice | Line |
|---|---|---|
| `foxy_hook.mp3` | Foxy | Whoa! The biggest berry ever! |
| `foxy_mine.mp3` | Foxy | No way! It's mine! All mine! |
| `foxy_selfish.mp3` | Foxy | I'll keep it ALL to myself! |
| `foxy_realize.mp3` | Foxy | Wait… sharing is… actually fun! |
| `foxy_share.mp3` | Foxy | Let's share everything! |
| `foxy_yay.mp3` | Foxy | Yayyy! Sharing is the best! |
| `bunny_hungry.mp3` | Bunny | I'm so hungry… can I have one little bite? |
| `bunny_thanks.mp3` | Bunny | Thank you, Foxy! |
| `hog_help.mp3` | Hedgehog | Need a hand, Foxy? |
| `hog_moral.mp3` | Hedgehog | Friends make everything sweeter! |

## Fonts

The renderer needs these TTFs in `assets/fonts/`:

- `luckiest-guy.ttf` (title/captions), `bangers.ttf` (alt display),
  `baloo2-extrabold.ttf` + `baloo2-bold.ttf` (end card), `patrick-hand.ttf`
  (speech bubbles).

`patrick-hand.ttf` ships with the repo at `ink-theater/assets/patrickhand.ttf`
(SIL OFL — copy it over). For the Google Fonts, `@fontsource/*` npm packages can
be converted from woff2 with fonttools:

```bash
npm i @fontsource/luckiest-guy @fontsource/bangers @fontsource/baloo-2
python - <<'EOF'
from fontTools.ttLib import TTFont
m = {
  "node_modules/@fontsource/luckiest-guy/files/luckiest-guy-latin-400-normal.woff2": "luckiest-guy.ttf",
  "node_modules/@fontsource/bangers/files/bangers-latin-400-normal.woff2": "bangers.ttf",
  "node_modules/@fontsource/baloo-2/files/baloo-2-latin-800-normal.woff2": "baloo2-extrabold.ttf",
  "node_modules/@fontsource/baloo-2/files/baloo-2-latin-700-normal.woff2": "baloo2-bold.ttf",
}
for src, out in m.items():
    f = TTFont(src); f.flavor = None; f.save(out)
EOF
```

> The full font file matters: single-subset woff2 downloads silently fall back to
> a serif for ASCII (see `ink-theater/README.md` "font gotcha"). Convert the
> **latin** subset and keep the whole file.

## Notes

- All assets are **included in this package** — the 12 art stills
  (`assets/images/`), the chunky fonts (`assets/fonts/`), the 10 voice lines
  (`audio/voices/`), the full mix (`audio/final_mix.wav`), and the finished
  render (`foxy-shares.mp4`). You can re-render from scratch or just grab the
  MP4 directly.
- `audio.py` ducks the BGM under dialogue and normalizes the master; peak levels
  are fine for social platforms (verified: <0.001% clipped samples after AAC).
- Re-run `spec.py` after changing any voice clip so the timeline re-derives from
  the new durations.
