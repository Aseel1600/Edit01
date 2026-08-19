"""Contract tests for Engineering Revision 2B (E6 - slideshow risk restoration).

Revision 2B restores the scorer that was silently disabled by a shape mismatch
and runs it in REPORT-ONLY mode: the original blocking branch is preserved but
only executes when OPENMONTAGE_SLIDESHOW_RISK_ENFORCEMENT=block.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lib.slideshow_risk import score_slideshow_risk
from tools.video.video_compose import VideoCompose

REPO_ROOT = Path(__file__).resolve().parents[2]
# Committed fixtures: `projects/` is gitignored, so the tests must never read
# the local validation project or they fail in a clean clone.
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "slideshow_risk"
V = VideoCompose


def _scene(**over):
    base = {
        "id": "s1", "type": "animation", "description": "a distinct establishing beat",
        "shot_language": {"shot_size": "wide", "camera_movement": "static"},
        "shot_intent": "establish the subject", "narrative_role": "establish_context",
        "information_role": "context", "hero_moment": False,
    }
    base.update(over)
    return base


STRONG_SCENES = [
    _scene(id="s1", description="wide establishing valley at dawn"),
    _scene(id="s2", type="broll", description="close detail of moving water",
           shot_language={"shot_size": "close_up", "camera_movement": "dolly_in"},
           shot_intent="reveal texture", hero_moment=True),
    _scene(id="s3", type="diagram", description="layered build of the mechanism",
           shot_language={"shot_size": "medium", "camera_movement": "static"},
           shot_intent="explain the parts"),
    _scene(id="s4", type="generated", description="transformation across materials",
           shot_language={"shot_size": "medium_wide", "camera_movement": "tracking_left"},
           shot_intent="show change over time"),
]

SLIDESHOW_SCENES = [
    {"id": f"s{i}", "type": "text_card", "description": "text card", "shot_language": {}}
    for i in range(1, 6)
]


# ---------------------------------------------------------------------------
# Input handling (Phase 3)
# ---------------------------------------------------------------------------

def test_artifact_dict_is_normalised_not_iterated():
    """The regression: iterating the artifact yielded str keys."""
    artifact = {"version": "1.0", "style_playbook": "premium-minimalist",
                "scenes": STRONG_SCENES, "metadata": {}}
    scenes, source = V._normalize_scene_plan(artifact)
    assert scenes == STRONG_SCENES and source == "scene_plan"
    assert all(isinstance(s, dict) for s in scenes), "dictionary keys must never be treated as scenes"


def test_plain_list_is_preserved():
    scenes, source = V._normalize_scene_plan(STRONG_SCENES)
    assert scenes is STRONG_SCENES and source == "scene_plan"


@pytest.mark.parametrize("empty", [None, {}, {"scenes": []}, []])
def test_empty_inputs_are_handled(empty):
    scenes, source = V._normalize_scene_plan(empty)
    assert scenes == [] and source in {"none", "scene_plan"}


@pytest.mark.parametrize("bad", ["nope", 7, 1.5, object()])
def test_invalid_types_are_reported_not_iterated(bad):
    scenes, source = V._normalize_scene_plan(bad)
    assert scenes == [] and source == "invalid"


def test_dict_with_non_list_scenes_is_invalid():
    scenes, source = V._normalize_scene_plan({"scenes": "sc1,sc2"})
    assert scenes == [] and source == "invalid"


def test_artifact_dict_no_longer_raises_in_scorer():
    """End-to-end guard for 'str' object has no attribute 'get'."""
    artifact = {"version": "1.0", "scenes": STRONG_SCENES}
    scenes, _ = V._normalize_scene_plan(artifact)
    result = score_slideshow_risk(scenes, {}, "animation-first", "remotion")
    assert result["verdict"] in {"strong", "acceptable", "revise", "fail"}


# ---------------------------------------------------------------------------
# Scoring determinism and equivalence
# ---------------------------------------------------------------------------

def test_list_and_artifact_forms_score_identically():
    artifact = {"version": "1.0", "scenes": STRONG_SCENES}
    a = score_slideshow_risk(V._normalize_scene_plan(artifact)[0], {}, "animation-first", "remotion")
    b = score_slideshow_risk(V._normalize_scene_plan(STRONG_SCENES)[0], {}, "animation-first", "remotion")
    assert a["average"] == b["average"] and a["verdict"] == b["verdict"]


def test_scoring_is_deterministic():
    runs = {score_slideshow_risk(STRONG_SCENES, {}, "animation-first", "remotion")["average"] for _ in range(3)}
    assert len(runs) == 1


def test_slideshow_fixture_scores_worse_than_strong_fixture():
    strong = score_slideshow_risk(STRONG_SCENES, {}, "animation-first", "remotion")["average"]
    slides = score_slideshow_risk(SLIDESHOW_SCENES, {}, "animation-first", "remotion")["average"]
    assert slides > strong, f"slideshow fixture {slides} should out-risk strong fixture {strong}"


def test_canonical_regression_project_scores_strong():
    """The frozen PASS production must not be flagged from its scene_plan.

    Reads the committed fixture copy, not the gitignored validation project.
    """
    sp = json.loads((FIXTURES / "scene_plan.json").read_text(encoding="utf-8"))
    ed = json.loads((FIXTURES / "edit_decisions.json").read_text(encoding="utf-8"))
    scenes, source = V._normalize_scene_plan(sp)
    risk = score_slideshow_risk(scenes, ed, ed["renderer_family"], ed["render_runtime"])
    assert source == "scene_plan"
    assert risk["verdict"] == "strong" and risk["average"] == pytest.approx(0.67, abs=0.01)


def test_cuts_representation_scores_materially_higher():
    """Documents why the fallback shape must not drive enforcement."""
    ed = json.loads((FIXTURES / "edit_decisions.json").read_text(encoding="utf-8"))
    sp = json.loads((FIXTURES / "scene_plan.json").read_text(encoding="utf-8"))
    cuts_scenes = [{
        "type": c.get("type", ""), "description": c.get("reason", ""),
        "shot_language": c.get("shot_language", {}), "shot_intent": c.get("shot_intent"),
        "narrative_role": c.get("narrative_role"), "information_role": c.get("information_role"),
        "hero_moment": c.get("hero_moment", False),
    } for c in ed["cuts"]]
    from_cuts = score_slideshow_risk(cuts_scenes, ed, ed["renderer_family"], ed["render_runtime"])
    from_plan = score_slideshow_risk(sp["scenes"], ed, ed["renderer_family"], ed["render_runtime"])
    assert from_cuts["average"] > from_plan["average"]
    # the gap is concentrated in the dimensions cuts structurally cannot carry
    for dim in ("decorative_visuals", "weak_shot_intent"):
        assert from_cuts["dimensions"][dim]["score"] > from_plan["dimensions"][dim]["score"]


# ---------------------------------------------------------------------------
# Enforcement mode (Phase 5)
# ---------------------------------------------------------------------------

def test_default_enforcement_is_report_only(monkeypatch):
    monkeypatch.delenv(V.SLIDESHOW_RISK_ENFORCEMENT_ENV, raising=False)
    assert V.slideshow_risk_enforcement() == "report_only"


@pytest.mark.parametrize("value", ["block", "BLOCK", " block "])
def test_enforcement_can_be_opted_into(monkeypatch, value):
    monkeypatch.setenv(V.SLIDESHOW_RISK_ENFORCEMENT_ENV, value)
    assert V.slideshow_risk_enforcement() == "block"


@pytest.mark.parametrize("value", ["", "warn", "report_only", "true"])
def test_unknown_enforcement_values_stay_report_only(monkeypatch, value):
    monkeypatch.setenv(V.SLIDESHOW_RISK_ENFORCEMENT_ENV, value)
    assert V.slideshow_risk_enforcement() == "report_only"


def _validate(scene_plan, cuts=None, family="animation-first"):
    tool = VideoCompose()
    ed = {"version": "1.0", "render_runtime": "remotion", "renderer_family": family,
          "cuts": cuts or [{"id": "c1", "source": "", "in_seconds": 0, "out_seconds": 2}],
          "metadata": {"delivery_promise": {"promise_type": "data_explainer", "motion_required": False,
                                             "tone_mode": "educational", "quality_floor": "presentable"}}}
    return tool, tool._pre_compose_validation(ed, ed["cuts"], scene_plan)


def test_fail_verdict_does_not_block_in_report_only(monkeypatch):
    monkeypatch.delenv(V.SLIDESHOW_RISK_ENFORCEMENT_ENV, raising=False)
    fail_scenes = [{"id": f"s{i}", "type": "text_card", "description": "same", "shot_language": {}}
                   for i in range(6)]
    tool, blocked = _validate({"version": "1.0", "scenes": fail_scenes}, family="cinematic-trailer")
    assert tool.last_slideshow_risk["verdict"] == "fail", tool.last_slideshow_risk
    assert blocked is None, "report-only mode must never block the render"
    assert tool.last_slideshow_risk["enforcement"] == "report_only"


def test_fail_verdict_blocks_only_when_opted_in(monkeypatch):
    """The original blocking branch is preserved, not deleted."""
    monkeypatch.setenv(V.SLIDESHOW_RISK_ENFORCEMENT_ENV, "block")
    fail_scenes = [{"id": f"s{i}", "type": "text_card", "description": "same", "shot_language": {}}
                   for i in range(6)]
    tool, blocked = _validate({"version": "1.0", "scenes": fail_scenes}, family="cinematic-trailer")
    assert tool.last_slideshow_risk["verdict"] == "fail"
    assert blocked is not None and blocked.success is False
    assert "Slideshow risk" in (blocked.error or "")


@pytest.mark.parametrize("scenes", [STRONG_SCENES, SLIDESHOW_SCENES])
def test_strong_and_revise_never_block(monkeypatch, scenes):
    monkeypatch.delenv(V.SLIDESHOW_RISK_ENFORCEMENT_ENV, raising=False)
    tool, blocked = _validate({"version": "1.0", "scenes": scenes})
    assert tool.last_slideshow_risk["verdict"] != "fail" or blocked is None
    assert blocked is None


def test_scene_source_is_recorded(monkeypatch):
    monkeypatch.delenv(V.SLIDESHOW_RISK_ENFORCEMENT_ENV, raising=False)
    tool, _ = _validate({"version": "1.0", "scenes": STRONG_SCENES})
    assert tool.last_slideshow_risk["scene_source"] == "scene_plan"
    assert tool.last_slideshow_risk["scene_count"] == len(STRONG_SCENES)


# ---------------------------------------------------------------------------
# Exception visibility (Phase 4)
# ---------------------------------------------------------------------------

def test_scorer_exception_is_visible_and_non_blocking(monkeypatch, caplog):
    monkeypatch.delenv(V.SLIDESHOW_RISK_ENFORCEMENT_ENV, raising=False)
    import lib.slideshow_risk as risk_mod

    def boom(*_a, **_k):
        raise RuntimeError("scorer exploded")

    monkeypatch.setattr(risk_mod, "score_slideshow_risk", boom)
    with caplog.at_level("WARNING"):
        tool, blocked = _validate({"version": "1.0", "scenes": STRONG_SCENES})
    assert blocked is None, "a broken scorer must not block the render in report-only mode"
    assert tool.last_slideshow_risk["error"].startswith("RuntimeError: scorer exploded")
    assert tool.last_slideshow_risk["scene_source"] == "scene_plan"
    assert any("slideshow risk failed" in r.message.lower() or "RuntimeError" in r.getMessage()
               for r in caplog.records), "the failure must be logged, not swallowed"


def test_invalid_scene_plan_type_warns_and_falls_back(monkeypatch, caplog):
    monkeypatch.delenv(V.SLIDESHOW_RISK_ENFORCEMENT_ENV, raising=False)
    with caplog.at_level("WARNING"):
        tool, blocked = _validate("not-a-scene-plan")
    assert blocked is None
    assert any("unusable type" in r.getMessage() for r in caplog.records)
    assert tool.last_slideshow_risk["scene_source"] == "cuts"


# ---------------------------------------------------------------------------
# Fixture integrity - the scores above are only meaningful if the committed
# fixtures stay schema-valid and self-describing.
# ---------------------------------------------------------------------------

def test_fixtures_are_committed_and_schema_valid():
    from schemas.artifacts import validate_artifact

    for name, artifact in (("scene_plan", "scene_plan.json"), ("edit_decisions", "edit_decisions.json")):
        path = FIXTURES / artifact
        assert path.exists(), f"missing committed fixture {path}"
        data = json.loads(path.read_text(encoding="utf-8"))
        validate_artifact(name, data)
        assert "fixture_provenance" in data["metadata"], "fixture must record where it came from"


def test_no_slideshow_test_reads_the_gitignored_project():
    """Guard against the clean-clone defect returning.

    The needle is assembled at runtime so this guard does not match itself.
    """
    forbidden = "projects/" + "million-billion-trillion"
    source = Path(__file__).read_text(encoding="utf-8")
    assert forbidden not in source, (
        "this suite must read committed fixtures, never the gitignored validation project"
    )
    assert FIXTURES.is_relative_to(REPO_ROOT / "tests" / "fixtures"), (
        "fixtures must resolve inside the committed tests/fixtures tree"
    )
