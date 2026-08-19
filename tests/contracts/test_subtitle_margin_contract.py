"""Contract tests for Engineering Revision 2C (canonical subtitle vertical margin).

Adds one optional canonical field, `edit_decisions.subtitles.vertical_margin`,
expressed in video-space pixels (the same contract as
`video_stitch.pip_margin`: integer, minimum 0, "margin in pixels ... from
edges"). It converts to ASS MarginV through the PlayRes relationship
established in Revision 2A; an explicit native `margin_v` still wins.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from schemas.artifacts import validate_artifact
from tools.video.video_compose import VideoCompose

REPO_ROOT = Path(__file__).resolve().parents[2]
V = VideoCompose


def force_style(style: dict, video_height: int | None = 1080) -> dict[str, str]:
    raw = V._build_subtitle_style(style, video_height=video_height)
    return dict(part.split("=", 1) for part in raw.split(","))


def resolve(explicit=None, edit_decisions=None, playbook=None) -> dict:
    return V._resolve_subtitle_style(explicit, edit_decisions, playbook)


def _edit_decisions(**subtitle_fields) -> dict:
    return {
        "version": "1.0", "render_runtime": "ffmpeg",
        "cuts": [{"id": "c1", "source": "a.mp4", "in_seconds": 0, "out_seconds": 1}],
        "subtitles": {"enabled": True, "style": "sentence", "source": "s.srt", **subtitle_fields},
    }


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

def test_existing_artifact_without_the_field_still_validates():
    validate_artifact("edit_decisions", _edit_decisions(font_size=42, color="#111827"))


def test_artifact_with_vertical_margin_validates():
    validate_artifact("edit_decisions", _edit_decisions(vertical_margin=68))


def test_zero_margin_is_allowed():
    validate_artifact("edit_decisions", _edit_decisions(vertical_margin=0))


@pytest.mark.parametrize("bad", ["68", 68.5, None, True])
def test_invalid_margin_type_rejected(bad):
    with pytest.raises(Exception):
        validate_artifact("edit_decisions", _edit_decisions(vertical_margin=bad))


def test_negative_margin_rejected():
    with pytest.raises(Exception):
        validate_artifact("edit_decisions", _edit_decisions(vertical_margin=-10))


def test_unknown_subtitle_fields_remain_rejected():
    with pytest.raises(Exception):
        validate_artifact("edit_decisions", _edit_decisions(margin_v=18))
    with pytest.raises(Exception):
        validate_artifact("edit_decisions", _edit_decisions(invented_field=1))


def test_field_follows_the_pip_margin_precedent():
    """Naming/type contract mirrors the repository's only existing margin field."""
    subs = json.loads((REPO_ROOT / "schemas/artifacts/edit_decisions.schema.json").read_text(encoding="utf-8"))
    field = subs["properties"]["subtitles"]["properties"]["vertical_margin"]
    pip = json.loads((REPO_ROOT / "schemas/tools/video_stitch.schema.json").read_text(encoding="utf-8"))
    pip_margin = pip["properties"]["pip_margin"]
    assert field["type"] == pip_margin["type"] == "integer"
    assert field["minimum"] == pip_margin["minimum"] == 0
    assert "pixel" in field["description"].lower()


# ---------------------------------------------------------------------------
# Mapping and conversion
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(("height", "expected"), [(1080, "18"), (720, "27"), (2160, "9")])
def test_canonical_margin_converts_per_resolution(height, expected):
    parts = force_style(resolve(edit_decisions=_edit_decisions(vertical_margin=68)), video_height=height)
    assert parts["MarginV"] == expected


@pytest.mark.parametrize("height", [1080, 720, 2160])
def test_margin_is_proportionally_consistent(height):
    """68 canonical px must sit the same distance from the edge at every resolution."""
    margin_ass = float(force_style(resolve(edit_decisions=_edit_decisions(vertical_margin=68)),
                                   video_height=height)["MarginV"])
    effective_px = margin_ass * height / V.ASS_PLAYRES_Y
    assert effective_px == pytest.approx(68, abs=2)


def test_native_margin_v_overrides_canonical():
    parts = force_style(resolve(explicit={"margin_v": 40},
                                edit_decisions=_edit_decisions(vertical_margin=68)))
    assert parts["MarginV"] == "40"


def test_omission_reproduces_revision_2a_default():
    """No canonical margin -> the exact Revision 2A force_style."""
    assert V._build_subtitle_style(resolve(), video_height=1080) == (
        "FontName=Inter,FontSize=28,Bold=1,BorderStyle=1,Outline=2,Shadow=0,MarginV=40,Alignment=2"
    )


def test_zero_margin_maps_to_zero():
    assert force_style(resolve(edit_decisions=_edit_decisions(vertical_margin=0)))["MarginV"] == "0"


def test_margin_does_not_disturb_other_revision_2a_mappings():
    parts = force_style(resolve(edit_decisions=_edit_decisions(
        font_size=42, color="#111827", outline_color="#FFFFFF",
        position="bottom-center", vertical_margin=68)))
    assert parts["FontSize"] == "11.2"
    assert parts["PrimaryColour"] == "&H00271811"
    assert parts["OutlineColour"] == "&H00FFFFFF"
    assert parts["Alignment"] == "2"


# ---------------------------------------------------------------------------
# Burn integration
# ---------------------------------------------------------------------------

def _clip(tmp_path: Path, size: str) -> Path:
    out = tmp_path / f"clip_{size}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                    "-i", f"color=c=white:s={size}:d=2:r=30",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out)], check=True, timeout=180)
    return out


def _srt(tmp_path: Path) -> Path:
    p = tmp_path / "c.srt"
    p.write_text("1\n00:00:00,200 --> 00:00:01,800\n"
                 "And a trillion seconds is nearly\nthirty-one thousand seven hundred years.\n\n",
                 encoding="utf-8")
    return p


def _ink_rows(png: Path, threshold: int = 120) -> list[int]:
    from PIL import Image
    with Image.open(png) as img:
        grey = img.convert("L"); w, h = grey.size; px = grey.load()
        return [y for y in range(h) if any(px[x, y] < threshold for x in range(0, w, 3))]


def _burn(tmp_path: Path, size: str, margin: int) -> tuple[Path, int]:
    width, height = (int(v) for v in size.split("x"))
    clip, srt = _clip(tmp_path, size), _srt(tmp_path)
    out = tmp_path / f"burned_{size}_{margin}.mp4"
    result = VideoCompose().execute({
        "operation": "burn_subtitles", "input_path": str(clip), "subtitle_path": str(srt),
        "output_path": str(out),
        "subtitle_style": V._resolve_subtitle_style(None, {"subtitles": {
            "style": "sentence", "font": "Inter", "font_size": 42, "color": "#111827",
            "outline_color": "#FFFFFF", "position": "bottom-center", "vertical_margin": margin}}, None),
    })
    assert result.success, result.error
    frame = tmp_path / f"frame_{size}_{margin}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1.0", "-i", str(out),
                    "-frames:v", "1", str(frame)], check=True, timeout=120)
    return frame, height


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg unavailable")
def test_canonical_margin_achieves_requested_bottom_spacing(tmp_path):
    frame, height = _burn(tmp_path, "1920x1080", 68)
    rows = _ink_rows(frame)
    assert rows, "no caption ink found"
    bottom_gap = height - max(rows)
    assert bottom_gap == pytest.approx(68, abs=25), f"bottom gap {bottom_gap}px, expected ~68px"
    assert max(rows) < height * 0.99, "caption runs past the safe area"


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg unavailable")
def test_smaller_margin_moves_captions_lower(tmp_path):
    low, height = _burn(tmp_path, "1920x1080", 20)
    high, _ = _burn(tmp_path, "1920x1080", 200)
    assert max(_ink_rows(low)) > max(_ink_rows(high)), "a smaller margin must sit closer to the bottom edge"


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg unavailable")
def test_two_line_cue_spacing_and_no_centre_collision(tmp_path):
    frame, height = _burn(tmp_path, "1920x1080", 68)
    rows = _ink_rows(frame)
    assert (max(rows) - min(rows)) > 42, "expected two caption lines"
    assert not [y for y in rows if height * 0.35 <= y <= height * 0.65], "captions intrude into the centre band"


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg unavailable")
@pytest.mark.parametrize("size", ["1920x1080", "1280x720"])
def test_margin_visually_consistent_across_resolutions(tmp_path, size):
    """The canonical margin is video-space PIXELS, matching pip_margin and the
    Revision 2A font_size semantic: 68 px stays 68 px from the edge at every
    output resolution (it does not re-scale as a fraction of frame height)."""
    frame, height = _burn(tmp_path, size, 68)
    bottom_gap = height - max(_ink_rows(frame))
    assert bottom_gap == pytest.approx(68, abs=8), (
        f"bottom gap is {bottom_gap}px at {size}; expected ~68px in video-space pixels"
    )
