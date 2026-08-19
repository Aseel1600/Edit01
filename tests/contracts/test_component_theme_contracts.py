"""Contract tests for post-validation Engineering Revision 1.

Covers:
  E1 StatCard light-theme colour forwarding
  E2 KPIGrid exact numeric formatting (opt-in, additive)
  E3 theme-aware HeroTitle / SectionTitle / StatReveal on light surfaces
  E4 ComparisonCard explicit colour forwarding
  E7 overlay timing validation before Remotion renders
  E8 optional templated composition-props provenance pointer

Render-based checks drive the real Remotion CLI (already installed) and measure
the resulting PNGs with Pillow. No JS test runner is introduced.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from schemas.artifacts import validate_artifact
from tests.lib.remotion_frames import (
    CAPABILITY_FRAMES,
    FIXTURE_DIR,
    FIXTURE_FRAMES,
    GOLDEN_DIR,
    images_identical,
    ink_extent,
    region_contrast,
    remotion_available,
    render_still,
)
from tools.analysis.composition_validator import CompositionValidator

REPO_ROOT = Path(__file__).resolve().parents[2]

# WCAG AA for large text; the premium-minimalist playbook states 4.5:1 for all text.
MIN_CONTRAST = 4.5

# Normalised crop regions, measured from real renders of the fixtures.
REGIONS = {
    "hero_title": (0.55, 0.41, 0.78, 0.52),
    "hero_subtitle": (0.30, 0.52, 0.70, 0.56),
    "stat_subtitle": (0.35, 0.55, 0.65, 0.60),
    "section_title": (0.03, 0.05, 0.45, 0.16),
    "stat_reveal_label": (0.85, 0.89, 0.99, 0.94),
    "kpi_values": (0.06, 0.50, 0.94, 0.60),
}

requires_remotion = pytest.mark.skipif(
    not remotion_available(), reason="remotion-composer node_modules or npx unavailable"
)


@pytest.fixture(scope="module")
def light_frames(tmp_path_factory) -> dict[str, Path]:
    out = tmp_path_factory.mktemp("light_frames")
    props = FIXTURE_DIR / "components_light.json"
    return {name: render_still(props, frame, out / f"light_{name}.png")
            for name, frame in FIXTURE_FRAMES.items()}


@pytest.fixture(scope="module")
def dark_frames(tmp_path_factory) -> dict[str, Path]:
    out = tmp_path_factory.mktemp("dark_frames")
    props = FIXTURE_DIR / "components_dark.json"
    return {name: render_still(props, frame, out / f"dark_{name}.png")
            for name, frame in FIXTURE_FRAMES.items()}


@pytest.fixture(scope="module")
def capability_frames(tmp_path_factory) -> dict[str, Path]:
    out = tmp_path_factory.mktemp("capability_frames")
    props = FIXTURE_DIR / "components_capability.json"
    return {name: render_still(props, frame, out / f"cap_{name}.png")
            for name, frame in CAPABILITY_FRAMES.items()}


# ---------------------------------------------------------------------------
# E1 / E3 - light-theme readability
# ---------------------------------------------------------------------------

@requires_remotion
def test_e1_statcard_subtitle_readable_on_light_theme(light_frames):
    """StatCard's subtitle must not fall back to white on a light playbook."""
    result = region_contrast(light_frames["stat"], REGIONS["stat_subtitle"])
    assert result["ratio"] >= MIN_CONTRAST, (
        f"StatCard subtitle contrast {result['ratio']:.2f}:1 below {MIN_CONTRAST}:1 "
        f"(ink {result['ink']} on {result['background']})"
    )


@requires_remotion
@pytest.mark.parametrize(
    ("frame_key", "region_key"),
    [("hero", "hero_title"), ("hero", "hero_subtitle"),
     ("stat", "section_title"), ("comparison", "stat_reveal_label")],
)
def test_e3_overlay_components_readable_on_light_theme(light_frames, frame_key, region_key):
    """HeroTitle, SectionTitle and StatReveal must be readable on light surfaces."""
    result = region_contrast(light_frames[frame_key], REGIONS[region_key])
    assert result["ratio"] >= MIN_CONTRAST, (
        f"{region_key} contrast {result['ratio']:.2f}:1 below {MIN_CONTRAST}:1 "
        f"(ink {result['ink']} on {result['background']})"
    )


# ---------------------------------------------------------------------------
# Dark-theme regression - the whole point of the light-only forwarding
# ---------------------------------------------------------------------------

@requires_remotion
@pytest.mark.parametrize("name", sorted(FIXTURE_FRAMES))
def test_dark_theme_output_unchanged(dark_frames, name):
    """Dark themes must render byte-identically to the pre-fix goldens."""
    golden = GOLDEN_DIR / "dark" / f"dark_{name}.png"
    assert golden.exists(), f"missing golden {golden}"
    assert images_identical(dark_frames[name], golden), (
        f"dark-theme regression in '{name}': render differs from the pre-fix golden"
    )


# ---------------------------------------------------------------------------
# E2 - KPIGrid exact numeric formatting
# ---------------------------------------------------------------------------

@requires_remotion
def test_e2_exact_formatting_changes_output(capability_frames, dark_frames):
    """decimals/abbreviate must actually reach the renderer."""
    assert not images_identical(capability_frames["kpi_exact"], dark_frames["kpi"])


@requires_remotion
def test_e2_exact_values_are_wider_than_abbreviated(capability_frames, light_frames):
    """'31,700 years' occupies more horizontal space than '31.7K years'."""
    exact = ink_extent(capability_frames["kpi_exact"], REGIONS["kpi_values"])
    legacy = ink_extent(light_frames["kpi"], REGIONS["kpi_values"])
    assert exact > legacy, (
        f"exact-format ink extent {exact}px is not wider than legacy {legacy}px — "
        "abbreviation may still be applied"
    )


@requires_remotion
def test_e2_default_path_is_legacy(dark_frames):
    """Metrics without decimals/abbreviate keep today's rounded/abbreviated output."""
    golden = GOLDEN_DIR / "dark" / "dark_kpi.png"
    assert images_identical(dark_frames["kpi"], golden)


def test_e2_fixture_declares_exact_formatting():
    """Guard the fixture contract the render tests rely on."""
    cap = json.loads((FIXTURE_DIR / "components_capability.json").read_text(encoding="utf-8"))
    metrics = cap["cuts"][0]["chartData"]
    assert [m["value"] for m in metrics] == [11.6, 31.7, 31700]
    assert all(m["abbreviate"] is False for m in metrics)
    assert [m["decimals"] for m in metrics] == [1, 1, 0]


# ---------------------------------------------------------------------------
# E4 - ComparisonCard colour forwarding
# ---------------------------------------------------------------------------

@requires_remotion
def test_e4_explicit_colours_are_rendered(capability_frames):
    """Explicit leftColor/rightColor must appear in the rendered values."""
    from PIL import Image

    with Image.open(capability_frames["cmp_explicit"]) as img:
        pixels = set(img.convert("RGB").getdata())
    assert (37, 99, 235) in pixels, "explicit rightColor #2563EB not found in the render"
    assert (107, 114, 128) in pixels, "explicit leftColor #6B7280 not found in the render"


@requires_remotion
def test_e4_omitted_colours_preserve_defaults(dark_frames):
    """A comparison cut without colours must keep ComparisonCard's defaults."""
    from PIL import Image

    with Image.open(dark_frames["comparison"]) as img:
        pixels = set(img.convert("RGB").getdata())
    assert (16, 185, 129) in pixels, "default rightColor #10B981 missing — defaults were changed"


# ---------------------------------------------------------------------------
# E7 - overlay timing validation before render
# ---------------------------------------------------------------------------

def _validate_composition(tmp_path: Path, composition: dict):
    path = tmp_path / "composition.json"
    path.write_text(json.dumps(composition), encoding="utf-8")
    return CompositionValidator().execute(
        {"composition_path": str(path), "assets_root": str(tmp_path)}
    )


def _base_composition(overlays: list[dict]) -> dict:
    return {
        "cuts": [{"id": "c1", "source": "", "type": "text_card", "text": "hi",
                  "in_seconds": 0, "out_seconds": 2}],
        "overlays": overlays,
    }


def test_e7_wrong_timing_keys_fail_with_guidance(tmp_path):
    result = _validate_composition(tmp_path, _base_composition(
        [{"type": "section_title", "text": "label", "start_seconds": 0.5, "end_seconds": 1.5}]
    ))
    assert result.data["valid"] is False
    joined = " ".join(result.data["errors"])
    assert "start_seconds" in joined and "in_seconds" in joined and "out_seconds" in joined


def test_e7_out_not_greater_than_in_fails(tmp_path):
    result = _validate_composition(tmp_path, _base_composition(
        [{"type": "section_title", "text": "label", "in_seconds": 2.0, "out_seconds": 2.0}]
    ))
    assert result.data["valid"] is False
    assert any("greater than" in e for e in result.data["errors"])


@pytest.mark.parametrize("bad", [None, float("nan"), float("inf"), "1.5"])
def test_e7_non_finite_timing_fails(tmp_path, bad):
    result = _validate_composition(tmp_path, _base_composition(
        [{"type": "section_title", "text": "label", "in_seconds": 0.0, "out_seconds": bad}]
    ))
    assert result.data["valid"] is False


def test_e7_unknown_type_and_missing_text_fail(tmp_path):
    result = _validate_composition(tmp_path, _base_composition(
        [{"type": "mystery_overlay", "in_seconds": 0.0, "out_seconds": 1.0},
         {"type": "section_title", "in_seconds": 0.0, "out_seconds": 1.0}]
    ))
    assert result.data["valid"] is False
    joined = " ".join(result.data["errors"])
    assert "unknown overlay type" in joined and "requires 'text'" in joined


def test_e7_valid_overlay_passes(tmp_path):
    result = _validate_composition(tmp_path, _base_composition(
        [{"type": "section_title", "text": "label", "in_seconds": 0.2, "out_seconds": 1.8}]
    ))
    assert result.data["valid"] is True, result.data["errors"]


def test_e7_no_overlays_still_valid(tmp_path):
    result = _validate_composition(tmp_path, _base_composition([]))
    assert result.data["valid"] is True, result.data["errors"]


def test_e7_frozen_baseline_composition_still_validates():
    """The frozen PASS baseline must keep validating after the new checks."""
    baseline = REPO_ROOT / "engineering/post-validation-2026-08-19/baseline/composition_props_baseline.json"
    if not baseline.exists():
        pytest.skip("baseline record not present")
    result = CompositionValidator().execute({
        "composition_path": str(baseline),
        "assets_root": str(REPO_ROOT / "remotion-composer/public"),
    })
    assert result.data["valid"] is True, result.data["errors"]


# ---------------------------------------------------------------------------
# E8 - templated composition-props provenance
# ---------------------------------------------------------------------------

def _minimal_edit_decisions(**extra) -> dict:
    base = {
        "version": "1.0",
        "render_runtime": "remotion",
        "cuts": [{"id": "sc1", "source": "", "in_seconds": 0, "out_seconds": 2}],
    }
    base.update(extra)
    return base


def test_e8_legacy_artifact_without_pointer_remains_valid():
    validate_artifact("edit_decisions", _minimal_edit_decisions())


def test_e8_templated_pointer_validates():
    validate_artifact("edit_decisions", _minimal_edit_decisions(
        composition_mode="templated",
        templated={
            "composition_props_path": "remotion-composer/public/demo-props/x.json",
            "composition_props_sha256": "a" * 64,
            "composition_id": "Explainer",
        },
    ))


def test_e8_pointer_requires_path():
    with pytest.raises(Exception):
        validate_artifact("edit_decisions", _minimal_edit_decisions(templated={"composition_id": "Explainer"}))


def test_e8_pointer_rejects_unknown_fields_and_bad_sha():
    with pytest.raises(Exception):
        validate_artifact("edit_decisions", _minimal_edit_decisions(
            templated={"composition_props_path": "x.json", "unexpected": 1}))
    with pytest.raises(Exception):
        validate_artifact("edit_decisions", _minimal_edit_decisions(
            templated={"composition_props_path": "x.json", "composition_props_sha256": "not-a-sha"}))


def test_e8_cuts_remain_strict():
    """The fix must NOT open cuts[] up to component props."""
    with pytest.raises(Exception):
        validate_artifact("edit_decisions", _minimal_edit_decisions(
            cuts=[{"id": "sc1", "source": "", "in_seconds": 0, "out_seconds": 2,
                   "type": "stat_card", "stat": "11.6 days"}]))


def test_e8_recorded_sha256_matches_referenced_file():
    """Provenance is only useful if the recorded digest matches the file."""
    props = REPO_ROOT / "engineering/post-validation-2026-08-19/baseline/composition_props_baseline.json"
    if not props.exists():
        pytest.skip("baseline record not present")
    digest = hashlib.sha256(props.read_bytes()).hexdigest()
    artifact = _minimal_edit_decisions(
        composition_mode="templated",
        templated={"composition_props_path": str(props.relative_to(REPO_ROOT)).replace("\\", "/"),
                   "composition_props_sha256": digest},
    )
    validate_artifact("edit_decisions", artifact)
    referenced = REPO_ROOT / artifact["templated"]["composition_props_path"]
    assert referenced.exists()
    assert hashlib.sha256(referenced.read_bytes()).hexdigest() == artifact["templated"]["composition_props_sha256"]
