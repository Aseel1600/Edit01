"""Contract tests for Engineering Revision 2A (E5 - subtitle style contract).

Covers the five independent problems recorded in the engineering plan:

  1. `subtitles.style` is schema-typed as a string but was passed to `.items()`
  2. canonical schema fields never reached the renderer
  3. colours need ASS &HAABBGGRR, not CSS hex
  4. font size must account for the libass PlayRes canvas, not screen pixels
  5. explicit native/ASS overrides must keep precedence

Burn-integration checks use the existing pytest + FFmpeg + Pillow approach.
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
    """Render a force_style string into a dict for assertions."""
    raw = V._build_subtitle_style(style, video_height=video_height)
    return dict(part.split("=", 1) for part in raw.split(","))


def resolve(explicit=None, edit_decisions=None, playbook=None) -> dict:
    return V._resolve_subtitle_style(explicit, edit_decisions, playbook)


# ---------------------------------------------------------------------------
# 1. The latent crash: schema-valid `style` strings
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("display_style", ["sentence", "word-by-word", "karaoke", "clean-professional"])
def test_string_style_does_not_crash(display_style):
    """A schema-valid display string must never reach `.items()`."""
    resolved = resolve(edit_decisions={"subtitles": {"enabled": True, "style": display_style}})
    assert resolved["display_style"] == display_style


def test_string_style_is_schema_valid():
    """Guard that the string form really is the public contract."""
    validate_artifact("edit_decisions", {
        "version": "1.0", "render_runtime": "ffmpeg",
        "cuts": [{"id": "c1", "source": "a.mp4", "in_seconds": 0, "out_seconds": 1}],
        "subtitles": {"enabled": True, "style": "sentence", "source": "s.srt"},
    })


def test_legacy_dict_style_still_tolerated():
    """Undocumented legacy shape keeps working; it is not schema-supported."""
    resolved = resolve(edit_decisions={"subtitles": {"style": {"margin_v": 12, "alignment": 8}}})
    assert resolved["margin_v"] == 12 and resolved["alignment"] == 8


@pytest.mark.parametrize("bad", [5, 1.5, ["sentence"]])
def test_invalid_style_type_fails_clearly(bad):
    """An unusable type must raise a clear error, not AttributeError."""
    with pytest.raises(ValueError, match="must be a string"):
        resolve(edit_decisions={"subtitles": {"style": bad}})


def test_non_dict_subtitles_block_fails_clearly():
    with pytest.raises(ValueError, match="must be an object"):
        resolve(edit_decisions={"subtitles": "yes"})


# ---------------------------------------------------------------------------
# 2 + 3. Canonical fields reach the renderer; colours convert to ASS
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(("css", "ass"), [
    ("#111827", "&H00271811"),   # BGR order, opaque
    ("#FFFFFF", "&H00FFFFFF"),
    ("#FF0000", "&H000000FF"),   # pure red -> BB=00 GG=00 RR=FF
    ("#00FF00", "&H0000FF00"),
    ("#0000FF", "&H00FF0000"),
    ("#FFF", "&H00FFFFFF"),      # short form
    ("#00000088", "&H77000000"), # CSS alpha 0x88 opaque -> ASS 0x77 transparency
    ("&H00ABCDEF", "&H00ABCDEF"),  # already ASS -> untouched
])
def test_css_colour_converts_to_ass(css, ass):
    assert V.css_color_to_ass(css) == ass


@pytest.mark.parametrize("bad", ["rgb(1,2,3)", "#12345", "notacolour"])
def test_invalid_colour_rejected(bad):
    with pytest.raises(ValueError, match="Unsupported subtitle colour"):
        V.css_color_to_ass(bad)


def test_canonical_fields_map_to_ass():
    parts = force_style(resolve(edit_decisions={"subtitles": {
        "style": "sentence", "font": "Inter", "font_size": 42,
        "color": "#111827", "outline_color": "#FFFFFF", "position": "bottom-center",
    }}))
    assert parts["FontName"] == "Inter"
    assert parts["PrimaryColour"] == "&H00271811"
    assert parts["OutlineColour"] == "&H00FFFFFF"
    assert parts["Alignment"] == "2"


def test_canonical_background_requests_a_caption_box():
    parts = force_style({"background": "#00000088"})
    assert parts["BackColour"] == "&H77000000"
    assert parts["BorderStyle"] == "3"


def test_playbook_hex_colours_now_convert():
    """Playbook-derived colours were emitted as raw hex and ignored by libass."""
    playbook = {"typography": {"body": {"family": "Inter"}},
                "visual_language": {"color_palette": {"text": "#111827", "background": "#F9FAFB"}}}
    parts = force_style(resolve(playbook=playbook))
    assert parts["PrimaryColour"] == "&H00271811"
    assert parts["OutlineColour"].startswith("&H")


# ---------------------------------------------------------------------------
# 4. Font size against the real libass PlayRes canvas
# ---------------------------------------------------------------------------

def test_playres_matches_ffmpeg_output(tmp_path):
    """The conversion constant must match what ffmpeg actually writes."""
    if not shutil.which("ffmpeg"):
        pytest.skip("ffmpeg unavailable")
    srt = tmp_path / "s.srt"
    srt.write_text("1\n00:00:00,000 --> 00:00:01,000\nhello\n\n", encoding="utf-8")
    ass = tmp_path / "s.ass"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(srt), str(ass)], check=True, timeout=60)
    header = ass.read_text(encoding="utf-8", errors="ignore")
    assert f"PlayResY: {V.ASS_PLAYRES_Y}" in header
    assert f"PlayResX: {V.ASS_PLAYRES_X}" in header


@pytest.mark.parametrize(("height", "expected"), [(1080, 11.2), (720, 16.8), (2160, 5.6)])
def test_canonical_px_scales_with_output_height(height, expected):
    assert V.canonical_px_to_ass_units(42, height) == pytest.approx(expected, rel=1e-6)


@pytest.mark.parametrize("height", [1080, 720, 2160])
def test_caption_height_is_visually_consistent_across_resolutions(height):
    """42 canonical px must occupy the same fraction of frame height everywhere."""
    ass_size = float(force_style({"font_size": 42}, video_height=height)["FontSize"])
    effective_px = ass_size * height / V.ASS_PLAYRES_Y
    assert effective_px == pytest.approx(42, rel=0.02)


def test_default_font_size_is_unchanged():
    """No canonical size supplied -> historical FontSize 28 (no regression)."""
    assert force_style(resolve())["FontSize"] == "28"


def test_defaults_render_identically_to_pre_fix_contract():
    """The whole default force_style must equal the historical string."""
    assert V._build_subtitle_style(resolve(), video_height=1080) == (
        "FontName=Inter,FontSize=28,Bold=1,BorderStyle=1,Outline=2,Shadow=0,MarginV=40,Alignment=2"
    )


# ---------------------------------------------------------------------------
# 5. Precedence: defaults -> canonical -> explicit native
# ---------------------------------------------------------------------------

CANONICAL_ED = {"subtitles": {"style": "sentence", "font_size": 42, "color": "#111827",
                              "position": "bottom-center"}}


def test_native_font_size_beats_canonical():
    parts = force_style(resolve(explicit={"ass_font_size": 13}, edit_decisions=CANONICAL_ED))
    assert parts["FontSize"] == "13"


def test_native_alignment_beats_canonical_position():
    parts = force_style(resolve(explicit={"alignment": 5}, edit_decisions=CANONICAL_ED))
    assert parts["Alignment"] == "5"


def test_native_primary_colour_beats_canonical_colour():
    parts = force_style(resolve(explicit={"primary_color": "&H000000FF"}, edit_decisions=CANONICAL_ED))
    assert parts["PrimaryColour"] == "&H000000FF"


def test_canonical_beats_playbook_and_defaults():
    playbook = {"visual_language": {"color_palette": {"text": "#FF0000", "background": "#FFFFFF"}}}
    parts = force_style(resolve(edit_decisions=CANONICAL_ED, playbook=playbook))
    assert parts["PrimaryColour"] == "&H00271811"
    assert parts["FontSize"] == "11.2"


# ---------------------------------------------------------------------------
# Position mapping
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(("position", "alignment"),
                         [("bottom-center", "2"), ("center", "5"), ("top-center", "8")])
def test_every_schema_position_maps(position, alignment):
    assert force_style({"position": position})["Alignment"] == alignment


def test_schema_position_enum_is_fully_covered():
    schema = json.loads((REPO_ROOT / "schemas/artifacts/edit_decisions.schema.json").read_text(encoding="utf-8"))
    enum = set(schema["properties"]["subtitles"]["properties"]["position"]["enum"])
    assert enum == set(V.SUBTITLE_POSITION_ALIGNMENT)


def test_unsupported_position_rejected():
    with pytest.raises(ValueError, match="Unsupported subtitle position"):
        force_style({"position": "bottom-left"})


# ---------------------------------------------------------------------------
# Backwards-compatibility paths A and B
# ---------------------------------------------------------------------------

def test_path_a_canonical_only_project():
    """A: only canonical schema fields -> honoured."""
    ed = {"version": "1.0", "render_runtime": "ffmpeg",
          "cuts": [{"id": "c1", "source": "a.mp4", "in_seconds": 0, "out_seconds": 1}],
          "subtitles": {"enabled": True, "style": "sentence", "source": "s.srt",
                        "font": "Inter", "font_size": 42, "color": "#111827",
                        "outline_color": "#FFFFFF", "position": "bottom-center"}}
    validate_artifact("edit_decisions", ed)
    parts = force_style(resolve(edit_decisions=ed))
    assert parts["FontSize"] == "11.2" and parts["PrimaryColour"] == "&H00271811" and parts["Alignment"] == "2"


def test_path_b_native_override_project():
    """B: explicit native ASS values -> untouched by the mapping layer."""
    native = {"ass_font_size": 13, "primary_color": "&H00271811", "outline_color": "&H00FFFFFF",
              "alignment": 2, "margin_v": 18, "border_style": 1, "outline_width": 2, "shadow": 0}
    parts = force_style(resolve(explicit=native))
    assert parts["FontSize"] == "13" and parts["MarginV"] == "18"
    assert parts["PrimaryColour"] == "&H00271811" and parts["Alignment"] == "2"


# ---------------------------------------------------------------------------
# Burn integration (FFmpeg + Pillow)
# ---------------------------------------------------------------------------

def _make_clip(tmp_path: Path, seconds: int = 2, size: str = "1920x1080") -> Path:
    clip = tmp_path / "clip.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                    "-i", f"color=c=white:s={size}:d={seconds}:r=30",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(clip)], check=True, timeout=180)
    return clip


def _make_srt(tmp_path: Path) -> Path:
    srt = tmp_path / "captions.srt"
    srt.write_text(
        "1\n00:00:00,200 --> 00:00:01,800\n"
        "And a trillion seconds is nearly\nthirty-one thousand seven hundred years.\n\n",
        encoding="utf-8")
    return srt


def _ink_rows(png: Path, threshold: int = 120) -> list[int]:
    from PIL import Image
    with Image.open(png) as img:
        grey = img.convert("L")
        w, h = grey.size
        px = grey.load()
        return [y for y in range(h) if any(px[x, y] < threshold for x in range(0, w, 3))]


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg unavailable")
def test_burn_places_canonical_bottom_captions_in_the_lower_band(tmp_path):
    """Canonical fields alone must produce bottom-centre captions of sane size."""
    clip, srt = _make_clip(tmp_path), _make_srt(tmp_path)
    out = tmp_path / "burned.mp4"
    result = VideoCompose().execute({
        "operation": "burn_subtitles", "input_path": str(clip), "subtitle_path": str(srt),
        "output_path": str(out),
        "subtitle_style": VideoCompose._resolve_subtitle_style(None, {"subtitles": {
            "style": "sentence", "font": "Inter", "font_size": 42,
            "color": "#111827", "outline_color": "#FFFFFF", "position": "bottom-center"}}, None),
    })
    assert result.success, result.error

    frame = tmp_path / "frame.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1.0", "-i", str(out),
                    "-frames:v", "1", str(frame)], check=True, timeout=120)
    rows = _ink_rows(frame)
    assert rows, "no caption ink found in the burned frame"

    top, bottom = min(rows), max(rows)
    assert top > 1080 * 0.60, f"caption starts at y={top}; expected the lower band, not centred"
    assert bottom < 1080 * 0.99, "caption runs past the safe area"
    # two semantic lines are preserved -> ink spans clearly more than one line box
    assert (bottom - top) > 42, f"expected two caption lines, ink height was {bottom - top}px"
    # size is reasonable: neither the pre-fix giant nor invisible
    assert (bottom - top) < 1080 * 0.25, "caption block is implausibly tall"


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg unavailable")
def test_burn_does_not_overlap_the_centre_band(tmp_path):
    """Scene content lives in the centre; captions must not cover it."""
    clip, srt = _make_clip(tmp_path), _make_srt(tmp_path)
    out = tmp_path / "burned2.mp4"
    VideoCompose().execute({
        "operation": "burn_subtitles", "input_path": str(clip), "subtitle_path": str(srt),
        "output_path": str(out),
        "subtitle_style": VideoCompose._resolve_subtitle_style(
            None, {"subtitles": {"font_size": 42, "color": "#111827", "position": "bottom-center"}}, None),
    })
    frame = tmp_path / "frame2.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1.0", "-i", str(out),
                    "-frames:v", "1", str(frame)], check=True, timeout=120)
    centre_band = [y for y in _ink_rows(frame) if 1080 * 0.35 <= y <= 1080 * 0.65]
    assert not centre_band, f"captions intrude into the centre band at rows {centre_band[:5]}"
