#!/usr/bin/env python3
"""'The Backlot' — a Comfy Cloud showcase spot for OpenMontage.

A 30-second commercial whose premise is the product's own metaphor: a studio
backlot that fills itself with worlds. It is also a coverage harness — every
surface the Comfy Cloud adapter supports is used to make one of the shots, so
a successful render is proof the whole integration works:

    flux2-txt2img      stills for the animated shots
    wan22-i2v-4step    animates those stills
    wan22-t2v-4step    one pure text-to-video shot
    ace-step-1-t2a     the score
    custom workflow    the voiceover, via the ElevenLabs partner node
    model_family       one hero shot through a hosted partner video node

Run the shoot (spends Comfy Cloud credits):

    python scripts/comfy_cloud_backlot.py --stage shoot

Then assemble:

    python scripts/comfy_cloud_backlot.py --stage cut
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.env_loader import load_env  # noqa: E402

load_env(ROOT)

from lib.checkpoint import init_project  # noqa: E402
from tools.tool_registry import registry  # noqa: E402

PROJECT = "comfy-cloud-backlot"
BACKEND = "cloud"

# A consistent grade across every shot is what keeps generated footage from
# reading as a pile of unrelated clips: one palette, one lens, one hour.
LOOK = (
    "anamorphic cinema still, 2.39:1 framing, deep teal shadows and warm "
    "sodium practicals, volumetric haze, fine 35mm grain, shallow depth of "
    "field, no text, no watermark"
)

# WAN 2.2 i2v wants a moving subject. Given a landscape and an instruction to
# move, it will invent one — crew walking through an "empty" soundstage, a
# dune buggy cresting an "untouched" ridge. Two things are needed together:
# a negative that names the inventions, and a motion prompt that gives the
# model something legitimate to animate (camera, dust, water, light).
NO_SUBJECTS = (
    "people, person, human figures, crew, extras, actors, silhouettes of "
    "people, walking figures, faces, hands, vehicles, car, truck, motorcycle, "
    "dune buggy, quad bike, aircraft, animals, birds, tracks in the sand, "
    "text, logos, watermark"
)

SHOTS: list[dict[str, Any]] = [
    {
        "id": "01_stage_empty",
        "mode": "i2v",
        "still": (
            "An empty film soundstage before dawn, vast dark volume, a single "
            "work light on a stand throwing one cone of light across bare "
            "concrete, dust suspended in the beam, cable coiled, nothing built "
            "yet, " + LOOK
        ),
        "motion": (
            "Locked-off camera, no camera move. Only dust drifting slowly "
            "through the beam and the light flickering once. The room stays "
            "completely empty and still."
        ),
        "negative": NO_SUBJECTS,
    },
    {
        "id": "02_desert",
        "mode": "i2v",
        "still": (
            "Endless sand dunes at first light, long blue shadows down the "
            "ridgelines, a thin band of warm sun on the crests, wind lifting a "
            "veil of sand, " + LOOK
        ),
        "motion": (
            "The aerial camera drifts slowly forward over the dune ridge. The "
            "only movement is wind lifting sand off the crest and the shadows "
            "creeping. The desert is completely deserted and nothing enters "
            "the frame."
        ),
        "negative": NO_SUBJECTS + ", buildings, roads, footprints, structures",
    },
    {
        "id": "03_ocean_partner",
        "mode": "partner",
        "model_family": "seedance_2.5",
        "prompt": (
            "A black basalt sea cliff taking a heavy storm swell, tower of "
            "white spray rising in slow motion, cold blue light through rain, "
            "anamorphic cinema, volumetric haze, 35mm grain"
        ),
    },
    {
        "id": "04_city",
        "mode": "i2v",
        "still": (
            "A narrow city street at night in heavy rain, neon signage bleeding "
            "red and cyan into wet asphalt, steam rising from a grate, one "
            "figure silhouetted far down the block, " + LOOK
        ),
        "motion": (
            "The camera dollies slowly down the wet street. Only rain, steam "
            "and the rippling neon reflections move. No one approaches the "
            "camera and nothing else enters the frame."
        ),
        # The still deliberately holds one distant silhouette; keep that and
        # suppress the crowd WAN would otherwise invent around it.
        "negative": (
            "crowds, groups of people, extras walking toward camera, faces, "
            "text, logos, watermark"
        ),
    },
    {
        "id": "05_stage_full",
        "mode": "t2v",
        # "Flooded with light" + "lamps" first produced a theatre auditorium
        # full of red seats. The finale has to be the SAME room as shot 01, so
        # the prompt now names the soundstage's architecture explicitly and the
        # negative rules out the performance venue WAN kept reaching for.
        "prompt": (
            "An empty film soundstage at night, vast industrial volume, bare "
            "polished concrete floor, black soundproofed walls, exposed steel "
            "lighting grid overhead. Enormous studio lamps ignite one after "
            "another down the length of the empty room, haze catching every "
            "beam. Completely empty floor, no seating of any kind, "
            "anamorphic cinema, deep teal shadows, warm practicals, 35mm grain"
        ),
        "negative": (
            NO_SUBJECTS
            + ", theatre, auditorium, cinema seats, rows of chairs, red seats, "
            "audience, proscenium stage, curtains, concert hall, balcony"
        ),
    },
]

TITLE_TEXT = "OpenMontage"
SUBTITLE_TEXT = "now running on Comfy Cloud"


def project_dir() -> Path:
    return Path(
        init_project(
            PROJECT, title="The Backlot", pipeline_type="cinematic"
        )
    )


def shoot(only: str | None = None, force: bool = False) -> int:
    registry.discover()
    image = registry._tools["comfyui_image"]
    video = registry._tools["comfyui_video"]
    music = registry._tools["comfyui_music"]
    root = project_dir()
    log: list[dict[str, Any]] = []

    def done(path: Path) -> bool:
        """Skip assets already on disk — reruns should not re-buy generations."""
        if path.exists() and path.stat().st_size > 0 and not force:
            print(f"  [skip] {path.name} already present")
            log.append({"asset": path.name, "success": True,
                        "bytes": path.stat().st_size, "error": None,
                        "skipped": True})
            return True
        return False

    def record(name: str, result, path: Path) -> bool:
        ok = bool(result.success and path.exists())
        size = path.stat().st_size if path.exists() else 0
        print(f"  [{'ok ' if ok else 'FAIL'}] {name}  {size:,} bytes")
        if not ok:
            print(f"         {result.error}")
        log.append({"asset": name, "success": ok, "bytes": size,
                    "error": None if ok else result.error})
        return ok

    for shot in SHOTS:
        if only and only != shot["id"]:
            continue
        print(f"\n=== {shot['id']}  ({shot['mode']})")
        clip = root / f"assets/video/{shot['id']}.mp4"

        if shot["mode"] == "i2v":
            still = root / f"assets/images/{shot['id']}.png"
            if not done(still):
                record(
                f"{shot['id']} still",
                image.execute({
                    "prompt": shot["still"], "width": 1280, "height": 720,
                    "steps": 20, "backend": BACKEND, "output_path": str(still),
                }),
                still,
                )
            if not still.exists():
                continue
            if done(clip):
                continue
            record(
                f"{shot['id']} clip",
                video.execute({
                    "operation": "image_to_video", "prompt": shot["motion"],
                    "negative_prompt": shot.get("negative", ""),
                    "reference_image_path": str(still),
                    "width": 704, "height": 400, "num_frames": 81,
                    "backend": BACKEND, "timeout_seconds": 2400,
                    "output_path": str(clip),
                }),
                clip,
            )

        elif shot["mode"] == "t2v":
            if done(clip):
                continue
            record(
                f"{shot['id']} clip",
                video.execute({
                    "operation": "text_to_video", "prompt": shot["prompt"],
                    "negative_prompt": shot.get("negative", ""),
                    "width": 832, "height": 480, "num_frames": 81,
                    "backend": BACKEND, "timeout_seconds": 2400,
                    "output_path": str(clip),
                }),
                clip,
            )

        elif shot["mode"] == "partner":
            if done(clip):
                continue
            record(
                f"{shot['id']} clip (partner {shot['model_family']})",
                video.execute({
                    "operation": "text_to_video", "prompt": shot["prompt"],
                    "model_family": shot["model_family"],
                    "duration": 5, "resolution": "720p",
                    "backend": BACKEND, "timeout_seconds": 2400,
                    "output_path": str(clip),
                }),
                clip,
            )

    if not only:
        print("\n=== score  (ace-step)")
        score = root / "assets/music/backlot_score.mp3"
        if not done(score):
            record(
            "score",
            music.execute({
                "prompt": (
                    "cinematic trailer score, slow swelling low strings, deep "
                    "sub pulse every two bars, distant choir pad, one bright "
                    "piano figure entering late, hopeful resolve, instrumental"
                ),
                "duration_seconds": 32, "steps": 50, "backend": BACKEND,
                "timeout_seconds": 1800, "output_path": str(score),
                }),
                score,
            )

    (root / "artifacts" / "shoot_log.json").write_text(json.dumps(log, indent=2))
    failed = [entry for entry in log if not entry["success"]]
    print(f"\n{len(log) - len(failed)}/{len(log)} assets produced")
    return 1 if failed else 0


def _pick_font(size: int):
    """Return a real typeface, falling back to PIL's bitmap default."""
    from PIL import ImageFont

    for path in (
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Avenir Next.ttc",
        "/System/Library/Fonts/Supplemental/Futura.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _render_end_card(dest: Path, size: tuple[int, int] = (1280, 536)) -> Path:
    """Draw the end card: product name over the spot's own shadow colour."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", size, (7, 11, 14))
    draw = ImageDraw.Draw(img)
    w, h = size

    title_font = _pick_font(76)
    sub_font = _pick_font(24)

    title_box = draw.textbbox((0, 0), TITLE_TEXT, font=title_font)
    sub_box = draw.textbbox((0, 0), SUBTITLE_TEXT, font=sub_font)
    title_h = title_box[3] - title_box[1]
    sub_h = sub_box[3] - sub_box[1]

    # Stack the three elements and centre the stack, rather than positioning
    # each from the middle — otherwise the rule lands inside the title's
    # descenders and reads as an underline.
    gap_above_rule, gap_below_rule = 34, 26
    stack_h = title_h + gap_above_rule + 1 + gap_below_rule + sub_h
    y = (h - stack_h) / 2

    def centered(text, font, top, fill, box):
        draw.text(((w - (box[2] - box[0])) / 2 - box[0], top - box[1]),
                  text, font=font, fill=fill)

    centered(TITLE_TEXT, title_font, y, (240, 244, 246), title_box)
    rule_y = y + title_h + gap_above_rule
    rule_w = 132
    draw.rectangle(
        [((w - rule_w) / 2, rule_y), ((w + rule_w) / 2, rule_y + 1)],
        fill=(52, 179, 196),
    )
    centered(SUBTITLE_TEXT, sub_font, rule_y + 1 + gap_below_rule,
             (126, 186, 197), sub_box)

    img.save(dest)
    return dest


def _ff(args: list[str]) -> None:
    proc = subprocess.run(["ffmpeg", "-v", "error", "-y", *args],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip()[:800])


# Cut timing. The voiceover is a single take, so the edit is timed around it
# rather than the other way round: shots are cut to SHOT_LEN, and VO_DELAY is
# set so the take's last line ("OpenMontage. Now running on Comfy Cloud.")
# lands on the end card instead of being stranded a shot early.
SHOT_LEN = 4.0
CARD_LEN = 4.0
VO_DELAY = 3.2


def cut() -> int:
    """Assemble the spot: graded clips, VO, score, and an end card."""
    root = project_dir()
    work = root / "assets" / "cut"
    work.mkdir(parents=True, exist_ok=True)

    clips = [root / f"assets/video/{s['id']}.mp4" for s in SHOTS]
    have = [c for c in clips if c.exists()]
    if not have:
        print("No clips found — run --stage shoot first.")
        return 1

    # Normalize to one 2.39:1 anamorphic frame with a short dip-to-black on
    # each cut, so the shots read as one piece rather than a reel.
    norm: list[Path] = []
    for i, clip in enumerate(have):
        out = work / f"n{i:02d}.mp4"
        _ff([
            "-i", str(clip),
            "-vf",
            (f"scale=1280:536:force_original_aspect_ratio=increase,"
             f"crop=1280:536,fps=24,setsar=1,"
             f"fade=t=in:st=0:d=0.3,fade=t=out:st={SHOT_LEN - 0.3:.2f}:d=0.3,"
             "format=yuv420p"),
            "-an", "-c:v", "libx264", "-crf", "18", "-t", f"{SHOT_LEN}", str(out),
        ])
        norm.append(out)

    # End card. This ffmpeg build has no drawtext filter compiled in, so the
    # type is rendered to a PNG with PIL and used as a still source — which
    # also gives real font control rather than drawtext's defaults.
    card_png = work / "card.png"
    _render_end_card(card_png)
    card = work / "card.mp4"
    _ff([
        "-loop", "1", "-i", str(card_png), "-t", f"{CARD_LEN}",
        "-vf", "fps=24,format=yuv420p,fade=t=in:st=0:d=0.8",
        "-c:v", "libx264", "-crf", "18", str(card),
    ])
    norm.append(card)

    concat = work / "list.txt"
    concat.write_text("\n".join(f"file '{p.name}'" for p in norm))
    silent = work / "silent.mp4"
    _ff(["-f", "concat", "-safe", "0", "-i", str(concat),
         "-c:v", "libx264", "-crf", "18", str(silent)])

    vo = root / "assets/audio/vo.mp3"
    score = root / "assets/music/backlot_score.mp3"
    final = root / "renders/final.mp4"
    final.parent.mkdir(parents=True, exist_ok=True)

    total = SHOT_LEN * (len(norm) - 1) + CARD_LEN
    if vo.exists() and score.exists():
        # Duck the score under the voiceover, then let it come back up and
        # carry the end card on its own.
        _ff([
            "-i", str(silent), "-i", str(vo), "-i", str(score),
            "-filter_complex",
            (f"[1:a]adelay={int(VO_DELAY * 1000)}|{int(VO_DELAY * 1000)},"
             f"volume=1.0[vo];"
             f"[2:a]atrim=0:{total:.2f},volume=0.34,"
             f"afade=t=in:st=0:d=1.5,afade=t=out:st={total - 2.5:.2f}:d=2.5[bed];"
             "[bed][vo]amix=inputs=2:duration=first:dropout_transition=0,"
             "dynaudnorm=f=200[a]"),
            "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest", str(final),
        ])
    else:
        _ff(["-i", str(silent), "-c", "copy", str(final)])

    print(f"Final cut: {final}  ({final.stat().st_size:,} bytes)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["shoot", "cut"], required=True)
    parser.add_argument("--only", help="Shoot a single shot id")
    parser.add_argument("--force", action="store_true",
                        help="Regenerate even if the asset already exists")
    args = parser.parse_args()
    return shoot(args.only, args.force) if args.stage == "shoot" else cut()


if __name__ == "__main__":
    raise SystemExit(main())
