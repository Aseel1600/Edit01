"""Artifact-schema drift contracts.

The canonical artifacts are the contract between pipeline stages, and every
schema in `schemas/artifacts/` sets `additionalProperties: false`. That makes
drift silent and expensive: `video_compose` never validates `edit_decisions`,
so a field the renderer happily consumes can be rejected much later by
`lib/checkpoint.py`, after the render already succeeded.

These tests round-trip representative artifacts — the shapes the director
skills actually tell the agent to write, and the shapes the Remotion
compositions actually read — through `validate_artifact()`, so the drift fails
here rather than at checkpoint time.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from schemas.artifacts import load_schema, validate_artifact
from tools.video.video_compose import VideoCompose

COMPOSER_DIR = PROJECT_ROOT / "remotion-composer"


# ---------------------------------------------------------------------------
# edit_decisions — the Remotion (templated) shape
# ---------------------------------------------------------------------------


def _remotion_edit_decisions() -> dict:
    """A composition exercising every field family the Explainer reads.

    Mirrors what `skills/pipelines/explainer/compose-director.md` instructs the
    agent to assemble: scene-type cuts, word-level captions, the Remotion audio
    shape, component overlays, and a playbook-derived theme.
    """
    return {
        "version": "1.0",
        "renderer_family": "explainer-data",
        "render_runtime": "remotion",
        "composition_mode": "templated",
        "playbook": "flat-motion-graphics",
        "theme": "flat-motion-graphics",
        "themeConfig": {
            "primaryColor": "#22D3EE",
            "backgroundColor": "#0F172A",
            "chartColors": ["#22D3EE", "#A78BFA"],
            "springConfig": {"damping": 12, "stiffness": 80, "mass": 1},
        },
        "delivery_promise": {
            "promise_type": "data_explainer",
            "motion_required": False,
            "tone_mode": "educational",
            "quality_floor": "presentable",
        },
        "cuts": [
            {
                "id": "cut-1",
                "source": "",
                "in_seconds": 0,
                "out_seconds": 4,
                "type": "hero_title",
                "text": "Vector Databases",
                "heroSubtitle": "Explained in 60 seconds",
                "animation": "zoom-in",
                "transition_out": "fade",
                "transition_duration": 0.4,
            },
            {
                "id": "cut-2",
                "source": "",
                "in_seconds": 4,
                "out_seconds": 9,
                "type": "text_card",
                "text": "Similarity, not equality",
                "fontSize": 96,
                "color": "#F8FAFC",
                "backgroundColor": "#0F172A",
                # Planning provenance carried from scene_plan — read back by
                # video_compose._pre_compose_validation for slideshow scoring.
                "shot_intent": "State the core reframe before any mechanism",
                "narrative_role": "deliver_payload",
                "information_role": "The one idea the viewer keeps",
                "hero_moment": True,
                "shot_language": {"shot_size": "medium", "camera_movement": "static"},
            },
            {
                "id": "cut-3",
                "source": "",
                "in_seconds": 9,
                "out_seconds": 14,
                "type": "stat_card",
                "stat": "4.8B",
                "subtitle": "Vectors indexed daily",
                "accentColor": "#A78BFA",
                "backgroundVideo": "assets/video/loop.mp4",
                "backgroundVideoStart": 2.5,
                "backgroundOverlay": 0.55,
            },
            {
                "id": "cut-4",
                "source": "",
                "in_seconds": 14,
                "out_seconds": 20,
                "type": "bar_chart",
                "chartData": [{"label": "2024", "value": 2.1}, {"label": "2025", "value": 3.5}],
                "chartColors": ["#22D3EE"],
                "chartAnimation": "grow",
                "showValues": True,
                "showGrid": True,
                "title": "Adoption",
            },
            {
                "id": "cut-5",
                "source": "",
                "in_seconds": 20,
                "out_seconds": 26,
                "type": "line_chart",
                "chartSeries": [{"name": "latency", "points": [{"x": 1, "y": 4}]}],
                "xLabel": "Index size",
                "yLabel": "ms",
                "showMarkers": True,
            },
            {
                "id": "cut-6",
                "source": "",
                "in_seconds": 26,
                "out_seconds": 31,
                "type": "pie_chart",
                "chartData": [{"label": "hits", "value": 82}],
                "donut": True,
                "centerLabel": "Recall",
                "centerValue": "82%",
                "showLegend": True,
            },
            {
                "id": "cut-7",
                "source": "",
                "in_seconds": 31,
                "out_seconds": 36,
                "type": "kpi_grid",
                "chartData": [{"label": "p95", "value": "18ms"}],
                "columns": 3,
            },
            {
                "id": "cut-8",
                "source": "",
                "in_seconds": 36,
                "out_seconds": 40,
                "type": "progress_bar",
                "progress": 0.82,
                "progressLabel": "Index rebuilt",
                "progressColor": "#22D3EE",
                "progressSegments": [{"label": "shard-1", "value": 0.4}],
            },
            {
                "id": "cut-9",
                "source": "",
                "in_seconds": 40,
                "out_seconds": 46,
                "type": "comparison",
                "leftLabel": "Keyword",
                "leftValue": "exact",
                "rightLabel": "Vector",
                "rightValue": "semantic",
                "title": "Two ways to search",
            },
            {
                "id": "cut-10",
                "source": "",
                "in_seconds": 46,
                "out_seconds": 51,
                "type": "callout",
                "text": "Embeddings are lossy — verify before you trust",
                "callout_type": "warning",
            },
            {
                "id": "cut-11",
                "source": "",
                "in_seconds": 51,
                "out_seconds": 58,
                "type": "terminal_scene",
                "steps": [{"kind": "cmd", "text": "pip install openmontage"}],
                "terminalTitle": "install",
                "prompt": "$",
                "accentColor": "#22D3EE",
            },
            {
                "id": "cut-12",
                "source": "",
                "in_seconds": 58,
                "out_seconds": 64,
                "type": "screenshot_scene",
                "backgroundImage": "screens/dashboard.png",
                "screenshotSteps": [{"kind": "cursor", "at": [0.5, 0.5]}],
                "screenshotSize": {"width": 2880, "height": 1800},
                "cursorStartAt": [0.1, 0.9],
            },
            {
                "id": "cut-13",
                "source": "",
                "in_seconds": 64,
                "out_seconds": 70,
                "type": "anime_scene",
                "images": ["assets/images/a.png", "assets/images/b.png"],
                "animation": "ken-burns",
                "particles": "fireflies",
                "particleColor": "#FDE68A",
                "particleCount": 20,
                "particleIntensity": 0.5,
                "vignette": True,
                "lightingFrom": "rgba(255,220,150,0.3)",
                "lightingTo": "transparent",
            },
            {
                # Plain media cut — no `type`, seeks into the source.
                "id": "cut-14",
                "source": "assets/video/broll.mp4",
                "in_seconds": 70,
                "out_seconds": 76,
                "source_in_seconds": 12.5,
                "speed": 1.0,
                "layer": "primary",
                "transform": {"scale": 1.0, "position": "center", "animation": "ken-burns-slow-zoom"},
                "reason": "Establishing shot under the closing narration",
            },
        ],
        "overlays": [
            {
                "type": "section_title",
                "in_seconds": 4,
                "out_seconds": 8,
                "text": "How it works",
                "position": "top-left",
                "accentColor": "#22D3EE",
            },
            {
                "type": "provider_chip",
                "in_seconds": 64,
                "out_seconds": 70,
                "providers": ["seedance", "veo"],
                "cycleSeconds": 2,
                "label": "Generated with",
            },
        ],
        "captions": [
            {"word": "Vector", "startMs": 0, "endMs": 340},
            {"word": "databases", "startMs": 340, "endMs": 820},
        ],
        "audio": {
            "narration": {"src": "assets/audio/narration.mp3", "volume": 1},
            "music": {
                "src": "assets/music/bed.mp3",
                "volume": 0.1,
                "fadeInSeconds": 2,
                "fadeOutSeconds": 3,
                "offsetSeconds": 55,
                "loop": False,
            },
        },
        "metadata": {"playbook": "flat-motion-graphics"},
    }


def _hyperframes_edit_decisions() -> dict:
    """The asset-id shape: HyperFrames / FFmpeg runtimes and documentary-montage."""
    return {
        "version": "1.0",
        "renderer_family": "documentary-montage",
        "render_runtime": "hyperframes",
        "cuts": [
            {
                "id": "cut_01",
                "source": "asset_slot_01",
                "in_seconds": 1.2,
                "out_seconds": 5.2,
                "layer": "primary",
                "type": "text_card",
                "text": "A minute in the rain",
                "caption": "opening plate",
                "transform": {"scale": 1.0, "position": "center"},
                "transition_in": "fade_in",
                "transition_out": "cut",
                "transition_duration": 0.8,
                "reason": "opening hero — raindrop on asphalt",
            }
        ],
        "overlays": [
            {
                "asset_id": "logo-lockup",
                "start_seconds": 80,
                "end_seconds": 84,
                "position": {"x": 100, "y": 900, "width": 320, "height": 80},
                "opacity": 0.9,
            }
        ],
        "audio": {
            "narration": {"segments": [{"asset_id": "narration-s1", "start_seconds": 0}]},
            "music": {
                "asset_id": "asset_music_bed",
                "volume": 0.7,
                "fade_in_seconds": 1.0,
                "fade_out_seconds": 4.0,
                "ducking": False,
            },
            "sfx": [{"asset_id": "sfx-thunder", "start_seconds": 12.0, "volume": 0.4}],
        },
        "subtitles": {
            "enabled": True,
            "style": "word-by-word",
            "source": "assets/subtitles.srt",
            "font": "Inter",
            "font_size": 48,
            "position": "bottom-center",
        },
        "end_tag": {
            "offset_seconds": 84.5,
            "notes": "Aligns tag fade-out with the final cut's fade-out.",
        },
        "metadata": {"pipeline": "documentary-montage"},
    }


def test_remotion_edit_decisions_round_trips():
    """A full templated-Remotion composition must survive validate_artifact()."""
    validate_artifact("edit_decisions", _remotion_edit_decisions())


def test_hyperframes_edit_decisions_round_trips():
    validate_artifact("edit_decisions", _hyperframes_edit_decisions())


@pytest.mark.parametrize("scene_type", sorted(VideoCompose._REMOTION_SCENE_TYPES))
def test_every_remotion_scene_type_is_accepted_on_a_cut(scene_type):
    """Every type the tool routes to Remotion must be expressible in the artifact.

    This is the exact bug class that made `type: "text_card"` invisible: the
    renderer dispatched on it, the tool branched on it, and the schema rejected
    it.
    """
    artifact = {
        "version": "1.0",
        "render_runtime": "remotion",
        "cuts": [{"id": "c1", "source": "", "in_seconds": 0, "out_seconds": 3, "type": scene_type}],
    }
    validate_artifact("edit_decisions", artifact)


def test_unknown_scene_type_is_still_rejected():
    """Widening the schema must not turn `type` into a free-for-all."""
    artifact = {
        "version": "1.0",
        "render_runtime": "remotion",
        "cuts": [{"id": "c1", "source": "", "in_seconds": 0, "out_seconds": 3, "type": "txt_card"}],
    }
    with pytest.raises(Exception):
        validate_artifact("edit_decisions", artifact)


# ---------------------------------------------------------------------------
# Scene-type registry: four sources that must agree
# ---------------------------------------------------------------------------


def _scene_types_from_explainer() -> set[str]:
    src = (COMPOSER_DIR / "src" / "Explainer.tsx").read_text(encoding="utf-8")
    return set(re.findall(r'cut\.type === "([a-z_]+)"', src))


def _scene_types_from_doc() -> set[str]:
    doc = (COMPOSER_DIR / "SCENE_TYPES.md").read_text(encoding="utf-8")
    # Only the "Cut types" table, which ends at the next `---` rule.
    section = doc.split("## Cut types (`cut.type`)", 1)[1].split("\n---", 1)[0]
    rows = set(re.findall(r"^\|\s*\*{0,2}`([a-z_]+)`\*{0,2}\s*\|", section, re.MULTILINE))
    return rows - {"type"}  # the table's own header cell


def _scene_types_from_schema() -> set[str]:
    return set(load_schema("edit_decisions")["$defs"]["scene_type"]["enum"])


def test_scene_type_registry_agrees_across_sources():
    """Explainer dispatch, SCENE_TYPES.md, the schema enum, and the Python set.

    If these four ever diverge, a scene type is either undocumented, unroutable,
    or unrepresentable in the artifact. Keeping them pinned together is what
    stops the drift from recurring.
    """
    from_code = _scene_types_from_explainer()
    from_doc = _scene_types_from_doc()
    from_schema = _scene_types_from_schema()
    from_tool = set(VideoCompose._REMOTION_SCENE_TYPES)

    assert from_code, "no `cut.type === ...` dispatch cases found in Explainer.tsx"
    assert from_doc == from_code, (
        "SCENE_TYPES.md and Explainer.tsx disagree; "
        f"doc-only={sorted(from_doc - from_code)} code-only={sorted(from_code - from_doc)}"
    )
    assert from_schema == from_code, (
        "edit_decisions.schema.json $defs.scene_type and Explainer.tsx disagree; "
        f"schema-only={sorted(from_schema - from_code)} code-only={sorted(from_code - from_schema)}"
    )
    assert from_tool == from_code, (
        "VideoCompose._REMOTION_SCENE_TYPES and Explainer.tsx disagree; "
        f"tool-only={sorted(from_tool - from_code)} code-only={sorted(from_code - from_tool)}"
    )


# ---------------------------------------------------------------------------
# The other canonical artifacts
# ---------------------------------------------------------------------------


def test_asset_manifest_allows_project_global_assets_without_a_scene():
    """Background music belongs to the video, not to a scene.

    `scene_id` used to be required on every asset, so the manifest the
    asset-director documents could never validate.
    """
    validate_artifact(
        "asset_manifest",
        {
            "version": "1.0",
            "assets": [
                {
                    "id": "narration-s1",
                    "type": "audio",
                    "subtype": "narration",
                    "path": "assets/narration/s1.mp3",
                    "source_tool": "tts_selector",
                    "scene_id": "scene-1",
                    "duration_seconds": 8.2,
                    "cost_usd": 0.003,
                },
                {
                    "id": "music-bg",
                    "type": "audio",
                    "subtype": "music",
                    "path": "assets/music/background.mp3",
                    "source_tool": "music_gen",
                    "duration_seconds": 62,
                    "cost_usd": 0.05,
                },
            ],
            "total_cost_usd": 0.053,
            "metadata": {"generation_summary": {"images_generated": 8}, "music_status": "generated"},
        },
    )


def test_render_report_records_the_runtime_that_ran():
    validate_artifact(
        "render_report",
        {
            "version": "1.0",
            "outputs": [
                {
                    "path": "renders/output.mp4",
                    "format": "mp4",
                    "codec": "h264",
                    "audio_codec": "aac",
                    "audio_channels": 2,
                    "resolution": "1920x1080",
                    "fps": 30,
                    "duration_seconds": 62.4,
                    "file_size_bytes": 47395635,
                    "platform_target": "youtube",
                }
            ],
            "render_time_seconds": 180,
            "render_grammar": "explainer-data",
            "render_runtime": "remotion",
            "composition_mode": "templated",
            "render_summary": {"total_cuts_rendered": 12, "subtitles_burned": True},
            "verification_notes": ["Duration within +0.2s of planned"],
        },
    )


def test_scene_plan_accepts_talking_head_overlay_scenes():
    validate_artifact(
        "scene_plan",
        {
            "version": "1.0",
            "scenes": [
                {
                    "id": "section_1",
                    "type": "talking_head",
                    "description": "Speaker introduces agentic AI",
                    "start_seconds": 0,
                    "end_seconds": 22,
                },
                {
                    "id": "overlay_1",
                    "type": "overlay",
                    "overlay_type": "text_card",
                    "description": "Define 'Agentic AI' while the speaker first says it",
                    "start_seconds": 22.0,
                    "end_seconds": 26.0,
                    "content": {"text": "Agentic AI", "subtext": "Acts autonomously toward goals"},
                    "position": "lower_third",
                },
            ],
        },
    )


def test_final_review_accepts_an_under_sampled_visual_spotcheck():
    """`_run_final_review` records under-sampling as an issue; it must validate.

    The schema demanded `frames_sampled >= 4`, so a partially-failed ffmpeg
    extraction produced a review the checkpoint writer then refused.
    """
    validate_artifact(
        "final_review",
        {
            "version": "1.0",
            "output_path": "renders/output.mp4",
            "status": "pass",
            "checks": {
                "technical_probe": {"valid_container": True, "has_audio": True},
                "visual_spotcheck": {
                    "frames_sampled": 2,
                    "frame_paths": ["/tmp/f0.png", "/tmp/f1.png"],
                    "issues": ["Only 2/4 frames extracted — some timestamps may be out of range"],
                },
                "audio_spotcheck": {"narration_present": True, "music_present": True},
                "promise_preservation": {"delivery_promise_honored": True, "render_runtime_used": "remotion"},
                "subtitle_check": {"subtitles_expected": True, "subtitles_present": True},
            },
            "issues_found": [],
            "recommended_action": "present_to_user",
        },
    )


# ---------------------------------------------------------------------------
# cuts -> CinematicRendererProps
# ---------------------------------------------------------------------------


def _cinematic_prop_names() -> dict[str, set[str]]:
    """Field names declared by remotion-composer/src/cinematic/types.ts.

    Parsed rather than hardcoded so the adapter's output is checked against the
    interfaces it actually has to satisfy.
    """
    src = (COMPOSER_DIR / "src" / "cinematic" / "types.ts").read_text(encoding="utf-8")
    blocks: dict[str, set[str]] = {}
    for name, body in re.findall(r"export interface (\w+)[^{]*\{(.*?)\n\}", src, re.DOTALL):
        blocks[name] = set(re.findall(r"^\s{2}(\w+)\??:", body, re.MULTILINE))
    return blocks


def _documentary_edit_decisions() -> dict:
    """The shape skills/pipelines/documentary-montage/edit-director.md emits."""
    return {
        "version": "1.0",
        "renderer_family": "documentary-montage",
        "render_runtime": "remotion",
        "cuts": [
            {
                "id": "cut_01",
                "source": "assets/video/rain.mp4",
                "in_seconds": 0,
                "out_seconds": 4.0,
                "source_in_seconds": 1.2,
                "transition_in": "fade_in",
                "transition_out": "cut",
                "transition_duration": 0.8,
                "reason": "opening hero",
            },
            {
                "id": "cut_02",
                "source": "assets/video/umbrella.mp4",
                "in_seconds": 4.0,
                "out_seconds": 7.5,
                "transition_in": "cut",
                "transition_out": "cut",
            },
            {
                "id": "cut_03",
                "source": "",
                "in_seconds": 7.5,
                "out_seconds": 12.0,
                "type": "hero_title",
                "text": "THE CITY KEEPS ITS OWN VIGIL.",
                "accentColor": "#86d8ff",
            },
        ],
        "audio": {
            "narration": {"src": "assets/audio/vo.mp3", "volume": 1},
            "music": {
                "asset_id": "asset_music_bed",
                "src": "assets/music/bed.mp3",
                "volume": 0.7,
                "fade_in_seconds": 1.0,
                "fade_out_seconds": 4.0,
            },
        },
        "captions": [{"word": "Rain", "startMs": 0, "endMs": 300}],
        "metadata": {"pipeline": "documentary-montage", "cinematic_tone": "void"},
    }


def test_cuts_adapt_to_cinematic_renderer_props():
    """documentary-montage must actually render, not crash on `props.scenes`."""
    props, error = VideoCompose._to_cinematic_props(_documentary_edit_decisions())
    assert error is None, error

    interfaces = _cinematic_prop_names()
    video_fields = interfaces["CinematicBaseScene"] | interfaces["CinematicVideoScene"]
    title_fields = interfaces["CinematicBaseScene"] | interfaces["CinematicTitleScene"]

    scenes = props["scenes"]
    assert [s["kind"] for s in scenes] == ["video", "video", "title"]

    # Timeline position and length, not in/out points.
    assert scenes[0]["startSeconds"] == 0 and scenes[0]["durationSeconds"] == 4.0
    assert scenes[1]["startSeconds"] == 4.0 and scenes[1]["durationSeconds"] == 3.5

    # source_in_seconds is a seek INTO the source -> trimBeforeSeconds.
    assert scenes[0]["trimBeforeSeconds"] == 1.2
    # "fade_in" over 0.8s at 30fps ramps; "cut" must not.
    assert scenes[0]["fadeInFrames"] == 24
    assert scenes[0]["fadeOutFrames"] == 0
    assert scenes[1]["fadeInFrames"] == 0

    assert scenes[2]["text"] == "THE CITY KEEPS ITS OWN VIGIL."
    assert scenes[2]["accent"] == "#86d8ff"

    for scene in scenes:
        allowed = title_fields if scene["kind"] == "title" else video_fields
        unknown = set(scene) - allowed
        assert not unknown, f"{scene['id']} carries fields the interface has no slot for: {unknown}"

    assert props["soundtrack"]["src"] == "assets/audio/vo.mp3"
    assert props["music"] == {
        "src": "assets/music/bed.mp3",
        "volume": 0.7,
        "fadeInSeconds": 1.0,
        "fadeOutSeconds": 4.0,
    }
    assert set(props["music"]) <= interfaces["CinematicSoundtrack"]
    assert props["captions"]["words"] == [{"word": "Rain", "startMs": 0, "endMs": 300}]
    assert props["renderer_family"] == "documentary-montage"


def test_cinematic_tone_only_applied_when_valid():
    ed = _documentary_edit_decisions()
    ed["metadata"]["cinematic_tone"] = "elegiac"  # a brief tone, not a CinematicTone
    props, error = VideoCompose._to_cinematic_props(ed)
    assert error is None
    assert all("tone" not in s for s in props["scenes"]), "invalid tone must not be passed through"


def test_cinematic_refuses_scene_types_it_cannot_render():
    """Dropping a chart cut would silently change the deliverable."""
    ed = _documentary_edit_decisions()
    ed["cuts"].append(
        {
            "id": "cut_04",
            "source": "",
            "in_seconds": 12.0,
            "out_seconds": 16.0,
            "type": "bar_chart",
            "chartData": [{"label": "2024", "value": 2.1}],
        }
    )
    props, error = VideoCompose._to_cinematic_props(ed)
    assert props is None
    assert "cut_04" in error and "bar_chart" in error
    assert "explainer-" in error, "the error should name the way out"


def test_audio_asset_ids_resolve_to_remotion_src():
    """The asset-id spelling had no resolver on the Remotion path — silent video."""
    lookup = {
        "music-bg": {"id": "music-bg", "path": "assets/music/bed.mp3"},
        "narration-s1": {"id": "narration-s1", "path": "assets/audio/s1.mp3"},
    }
    audio = {
        "music": {"asset_id": "music-bg", "volume": 0.7},
        "narration": {"segments": [{"asset_id": "narration-s1", "start_seconds": 0}]},
    }
    resolved, error = VideoCompose._resolve_audio_sources(audio, lookup)
    assert error is None
    assert resolved["music"]["src"] == "assets/music/bed.mp3"
    assert resolved["narration"]["src"] == "assets/audio/s1.mp3"
    # The original must be untouched — the FFmpeg/HyperFrames paths still read it.
    assert "src" not in audio["music"]


def test_remotion_render_routes_documentary_to_cinematic_props(tmp_path, monkeypatch):
    """End-to-end wiring: the props file handed to the CLI must be adapted.

    Covers the seam the unit test cannot — that _remotion_render picks
    CinematicRenderer for this family AND converts before writing props.
    """
    import shutil as _shutil

    monkeypatch.setattr(_shutil, "which", lambda name: f"/usr/bin/{name}")

    tool = VideoCompose()
    output_path = tmp_path / "renders" / "final.mp4"
    captured: dict = {}

    def fake_run_command(cmd, **kwargs):
        captured["cmd"] = cmd
        props_arg = next(a for a in cmd if a.startswith("--props="))
        captured["props"] = json.loads(Path(props_arg.split("=", 1)[1]).read_text())
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"fake-mp4")
        return None

    monkeypatch.setattr(tool, "run_command", fake_run_command)

    result = tool._remotion_render(
        {
            "edit_decisions": _documentary_edit_decisions(),
            "output_path": str(output_path),
        }
    )

    assert result.success, result.error
    assert captured["cmd"][4] == "CinematicRenderer"
    props = captured["props"]
    assert "scenes" in props and "cuts" not in props, "props were not adapted"
    assert props["scenes"][0]["kind"] == "video"
    assert props["soundtrack"]["src"] == "assets/audio/vo.mp3"


def test_multi_segment_narration_is_refused_not_truncated():
    lookup = {f"n{i}": {"id": f"n{i}", "path": f"a/{i}.mp3"} for i in range(3)}
    audio = {"narration": {"segments": [{"asset_id": f"n{i}", "start_seconds": i * 5} for i in range(3)]}}
    resolved, error = VideoCompose._resolve_audio_sources(audio, lookup)
    assert resolved is None
    assert "3 segments" in error and "audio_mixer" in error


# ---------------------------------------------------------------------------
# Remotion asset staging
# ---------------------------------------------------------------------------


def test_remotion_assets_are_staged_public_relative(tmp_path):
    """Assets must land under public/ and be referenced relative to it.

    `staticFile()` prefixes whatever it is given with the public URL, so an
    absolute path or a `file://` URI becomes `/public/Users/...` and 404s. The
    only reference form the components can resolve is public-relative.
    """
    import shutil

    src_a = tmp_path / "a"
    src_b = tmp_path / "b"
    src_a.mkdir()
    src_b.mkdir()
    # Same basename in two different directories — must not collide.
    (src_a / "shot.png").write_bytes(b"a")
    (src_b / "shot.png").write_bytes(b"b")
    (tmp_path / "narration.mp3").write_bytes(b"n")
    (tmp_path / "subs.srt").write_bytes(b"s")

    props = {
        "cuts": [
            {"id": "c1", "source": str(src_a / "shot.png"), "in_seconds": 0, "out_seconds": 2},
            {"id": "c2", "source": f"file://{src_b / 'shot.png'}", "in_seconds": 2, "out_seconds": 4},
            {
                "id": "c3",
                "source": "",
                "type": "anime_scene",
                "images": [str(src_a / "shot.png")],
                "in_seconds": 4,
                "out_seconds": 6,
            },
            {"id": "c4", "source": "https://example.com/x.mp4", "in_seconds": 6, "out_seconds": 8},
        ],
        "audio": {"narration": {"src": str(tmp_path / "narration.mp3"), "volume": 1}},
        # An .srt for the FFmpeg burn — Remotion never loads it, so it must be
        # left alone despite the key also being named "source".
        "subtitles": {"enabled": True, "source": str(tmp_path / "subs.srt")},
    }

    stage_dir = VideoCompose._stage_remotion_assets(
        props, COMPOSER_DIR, tmp_path / "renders" / "final.mp4"
    )
    try:
        public = COMPOSER_DIR / "public"
        sources = [c["source"] for c in props["cuts"]]

        assert not any(s.startswith(("file://", "/")) for s in sources[:3]), sources
        assert sources[0] != sources[1], "same-basename assets collided in public/"
        assert sources[3] == "https://example.com/x.mp4", "remote URLs must pass through"
        assert props["cuts"][2]["images"][0] == sources[0], "identical files copied twice"
        assert props["subtitles"]["source"] == str(tmp_path / "subs.srt")

        for rel in (sources[0], sources[1], props["audio"]["narration"]["src"]):
            assert (public / rel).is_file(), f"{rel} was not staged into public/"

        assert stage_dir is not None and stage_dir.is_relative_to(public)
    finally:
        if stage_dir is not None:
            shutil.rmtree(stage_dir, ignore_errors=True)
            try:
                stage_dir.parent.rmdir()  # leave public/ exactly as we found it
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Director-skill examples must be valid artifacts
# ---------------------------------------------------------------------------

# The canonical artifact each `<stage>-director.md` teaches the agent to emit.
# Only stages whose examples are complete artifacts (not fragments) are listed.
_DIRECTOR_ARTIFACTS = {
    "edit": "edit_decisions",
    "compose": "render_report",
    "assets": "asset_manifest",
}

_JSON_FENCE = re.compile(r"```json\s*\n(.*?)```", re.DOTALL)


def _complete_examples() -> list[tuple[Path, str, dict]]:
    """Every fenced JSON block in a director skill that is a whole artifact."""
    found: list[tuple[Path, str, dict]] = []
    for stage, artifact in _DIRECTOR_ARTIFACTS.items():
        for md in sorted((PROJECT_ROOT / "skills" / "pipelines").glob(f"*/{stage}-director.md")):
            for block in _JSON_FENCE.findall(md.read_text(encoding="utf-8")):
                try:
                    obj = json.loads(block)
                except json.JSONDecodeError:
                    continue  # fragments with <placeholders> are not parseable
                # A whole artifact carries the version marker; anything else is
                # an illustrative fragment and is out of scope here.
                if isinstance(obj, dict) and obj.get("version") == "1.0":
                    found.append((md.relative_to(PROJECT_ROOT), artifact, obj))
    return found


def test_director_skill_examples_are_valid_artifacts():
    """The JSON a director skill shows is the JSON the agent will copy.

    An example that cannot validate produces a stage that cannot checkpoint —
    which is how the render_report and documentary-montage edit_decisions
    examples silently rotted.
    """
    examples = _complete_examples()
    assert examples, "no complete artifact examples found in the director skills"

    failures = []
    for path, artifact, obj in examples:
        try:
            validate_artifact(artifact, obj)
        except Exception as exc:  # noqa: BLE001 — surfacing every failure at once
            failures.append(f"{path} ({artifact}): {str(exc).splitlines()[0]}")

    assert not failures, "director-skill examples do not match their schema:\n" + "\n".join(failures)
