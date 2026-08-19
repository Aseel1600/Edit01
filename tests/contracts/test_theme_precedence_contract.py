"""Contract tests for Engineering Revision 2D (E10 - theme precedence).

Legacy behaviour is unchanged: a recognised `theme`/`playbook` NAME wins and an
explicit `themeConfig` is ignored. The new opt-in `themeConfigWins: true` makes
the resolution order DEFAULT_THEME -> named preset -> themeConfig, merged
field by field.

`resolveTheme` is TypeScript, so behaviour is proven by rendering real frames
with the Revision 1 harness rather than by unit-testing the function directly.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest

from tests.lib.remotion_frames import (
    FIXTURE_DIR,
    FIXTURE_FRAMES,
    remotion_available,
    render_still,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
PRESET_GOLDENS = REPO_ROOT / "tests/fixtures/theme_contracts/goldens/presets"

# Palettes of the four built-in presets in remotion-composer/src/Root.tsx.
PRESETS = {
    "clean-professional":   {"backgroundColor": "#FFFFFF", "textColor": "#1F2937", "accentColor": "#F59E0B"},
    "flat-motion-graphics": {"backgroundColor": "#0F172A", "textColor": "#F8FAFC", "accentColor": "#EC4899"},
    "minimalist-diagram":   {"backgroundColor": "#FAFAFA", "textColor": "#1A1A2E", "accentColor": "#E94560"},
    "anime-ghibli":         {"backgroundColor": "#0A0A1A", "textColor": "#F0E6D3", "accentColor": "#FFB347"},
}

# Distinct from every preset background (clean-professional is #FFFFFF, so a
# near-white override could not prove "the override is NOT visible").
OVERRIDE_VIVID = {"backgroundColor": "#3B0764", "surfaceColor": "#3B0764", "textColor": "#FDE68A",
                  "accentColor": "#22D3EE"}

# A themeConfig that visibly differs from every preset above.
OVERRIDE = {
    "primaryColor": "#111827", "accentColor": "#2563EB", "backgroundColor": "#F9FAFB",
    "surfaceColor": "#F9FAFB", "textColor": "#111827", "mutedTextColor": "#6B7280",
    "headingFont": "Inter", "bodyFont": "Inter", "monoFont": "JetBrains Mono",
    "chartColors": ["#111827", "#2563EB", "#10B981", "#8B5CF6", "#EC4899", "#06B6D4"],
    "springConfig": {"damping": 20, "stiffness": 120, "mass": 1}, "transitionDuration": 0.4,
}

requires_remotion = pytest.mark.skipif(
    not remotion_available(), reason="remotion-composer node_modules or npx unavailable"
)


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    v = value.lstrip("#")
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _props(tmp_path: Path, name: str, **extra) -> Path:
    base = json.loads((FIXTURE_DIR / "components_dark.json").read_text(encoding="utf-8"))
    for key, value in list(extra.items()):
        if value is None:            # explicitly drop a key the fixture ships with
            base.pop(key, None)
            extra.pop(key)
    base.update(extra)
    path = tmp_path / f"{name}.json"
    path.write_text(json.dumps(base, indent=2), encoding="utf-8")
    return path


def _render(tmp_path: Path, name: str, frame_key: str = "hero", **extra) -> Path:
    return render_still(_props(tmp_path, name, **extra), FIXTURE_FRAMES[frame_key],
                        tmp_path / f"{name}_{frame_key}.png")


def _dominant_background(png: Path) -> tuple[int, int, int]:
    """Most common colour in the frame corners — the composition backdrop."""
    from PIL import Image
    with Image.open(png) as img:
        rgb = img.convert("RGB")
        w, h = rgb.size
        samples = [rgb.getpixel((x, y))
                   for x in range(5, w, max(1, w // 60))
                   for y in list(range(5, int(h * 0.18), 8)) + list(range(int(h * 0.85), h - 5, 8))]
    return Counter(samples).most_common(1)[0][0]


def _close(a: tuple[int, int, int], b: tuple[int, int, int], tol: int = 18) -> bool:
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Phase 4 - prove the current (legacy) defect
# ---------------------------------------------------------------------------

@requires_remotion
@pytest.mark.parametrize("preset", ["clean-professional", "flat-motion-graphics"])
def test_named_preset_currently_beats_themeconfig(tmp_path, preset):
    """Legacy: an explicit themeConfig is ignored when the name matches a preset.

    Covers one light preset and one dark preset.
    """
    with_config = _render(tmp_path, f"{preset}_ignored", theme=preset, themeConfig=OVERRIDE_VIVID)
    golden = PRESET_GOLDENS / f"{preset}_hero.png"
    assert _sha(with_config) == _sha(golden), (
        f"{preset}: supplying themeConfig changed the render without the opt-in"
    )
    assert not _close(_dominant_background(with_config), _hex_to_rgb(OVERRIDE_VIVID["backgroundColor"])), (
        "the override background must NOT be visible in legacy mode"
    )


@requires_remotion
def test_unknown_preset_name_lets_themeconfig_apply(tmp_path):
    """Why premium-minimalist worked: no matching preset -> themeConfig applies."""
    frame = _render(tmp_path, "unknown_name", theme="premium-minimalist", themeConfig=OVERRIDE)
    assert _close(_dominant_background(frame), _hex_to_rgb(OVERRIDE["backgroundColor"]))


@requires_remotion
def test_themeconfig_only_applies(tmp_path):
    frame = _render(tmp_path, "config_only", theme=None, playbook=None, themeConfig=OVERRIDE)
    assert _close(_dominant_background(frame), _hex_to_rgb(OVERRIDE["backgroundColor"]))


@requires_remotion
def test_no_theme_and_no_config_uses_default_theme(tmp_path):
    """DEFAULT_THEME is flat-motion-graphics."""
    frame = _render(tmp_path, "fallback", theme=None, playbook=None)
    assert _close(_dominant_background(frame), _hex_to_rgb(PRESETS["flat-motion-graphics"]["backgroundColor"]))


# ---------------------------------------------------------------------------
# Phase 6 - legacy goldens must not drift
# ---------------------------------------------------------------------------

@requires_remotion
@pytest.mark.parametrize("preset", sorted(PRESETS))
@pytest.mark.parametrize("frame_key", ["hero", "stat"])
def test_legacy_preset_goldens_are_byte_identical(tmp_path, preset, frame_key):
    """With the opt-in omitted every built-in preset renders exactly as before.

    The engineering record additionally verified all 4 frames x 4 presets
    (16/16 byte-identical); the suite checks the two most theme-sensitive
    frames per preset to keep runtime sane.
    """
    rendered = _render(tmp_path, f"{preset}_legacy", frame_key=frame_key, theme=preset)
    golden = PRESET_GOLDENS / f"{preset}_{frame_key}.png"
    assert golden.exists(), f"missing golden {golden}"
    assert _sha(rendered) == _sha(golden), f"legacy drift for {preset}/{frame_key}"


def test_golden_manifest_matches_stored_files():
    manifest = json.loads((PRESET_GOLDENS / "manifest.json").read_text(encoding="utf-8"))
    for preset, entry in manifest.items():
        for frame_key, digest in entry["frames"].items():
            assert _sha(PRESET_GOLDENS / f"{preset}_{frame_key}.png") == digest


# ---------------------------------------------------------------------------
# Phase 7 - opt-in behaviour
# ---------------------------------------------------------------------------

@requires_remotion
@pytest.mark.parametrize("preset", sorted(PRESETS))
def test_optin_lets_themeconfig_override_every_preset(tmp_path, preset):
    frame = _render(tmp_path, f"{preset}_optin", theme=preset,
                    themeConfig=OVERRIDE, themeConfigWins=True)
    assert _close(_dominant_background(frame), _hex_to_rgb(OVERRIDE["backgroundColor"])), (
        f"{preset}: opt-in did not apply the explicit background"
    )
    assert _sha(frame) != _sha(PRESET_GOLDENS / f"{preset}_hero.png")


@requires_remotion
def test_optin_applies_text_and_accent_colours(tmp_path):
    """Explicit text/accent must reach the components, not just the backdrop."""
    from PIL import Image
    frame = _render(tmp_path, "optin_colours", frame_key="stat", theme="flat-motion-graphics",
                    themeConfig=OVERRIDE, themeConfigWins=True)
    with Image.open(frame) as img:
        pixels = set(img.convert("RGB").getdata())
    assert _hex_to_rgb(OVERRIDE["accentColor"]) in pixels, "explicit accent colour not rendered"
    assert _hex_to_rgb(OVERRIDE["textColor"]) in pixels, "explicit text colour not rendered"


@requires_remotion
def test_partial_themeconfig_merges_field_by_field(tmp_path):
    """A partial override must keep the preset's other fields, not blank them."""
    partial = {"backgroundColor": "#F9FAFB", "surfaceColor": "#F9FAFB", "textColor": "#111827"}
    frame = _render(tmp_path, "partial_merge", frame_key="stat", theme="flat-motion-graphics",
                    themeConfig=partial, themeConfigWins=True)
    from PIL import Image
    with Image.open(frame) as img:
        pixels = set(img.convert("RGB").getdata())
    assert _close(_dominant_background(frame), _hex_to_rgb(partial["backgroundColor"]))
    # accentColor was NOT overridden -> the preset's accent must survive the merge
    assert _hex_to_rgb(PRESETS["flat-motion-graphics"]["accentColor"]) in pixels, (
        "partial themeConfig blanked a field it did not specify"
    )


@requires_remotion
def test_optin_without_themeconfig_is_a_no_op(tmp_path):
    frame = _render(tmp_path, "optin_noconfig", theme="minimalist-diagram", themeConfigWins=True)
    assert _sha(frame) == _sha(PRESET_GOLDENS / "minimalist-diagram_hero.png")


@requires_remotion
def test_revision_1_component_forwarding_still_works_under_optin(tmp_path):
    """Light-surface corrections from Revision 1 must apply to an opt-in light theme."""
    from tests.lib.remotion_frames import region_contrast
    frame = _render(tmp_path, "optin_rev1", frame_key="stat", theme="flat-motion-graphics",
                    themeConfig=OVERRIDE, themeConfigWins=True)
    result = region_contrast(frame, (0.35, 0.55, 0.65, 0.60))  # StatCard subtitle band
    assert result["ratio"] >= 4.5, f"StatCard subtitle contrast {result['ratio']:.2f}:1 under opt-in"


# ---------------------------------------------------------------------------
# Regression - million-billion-trillion must be unaffected
# ---------------------------------------------------------------------------

def test_million_billion_trillion_is_unaffected_by_e10():
    """Its playbook name is not a built-in preset, so precedence never applied.

    Validation-only: the composition props are local residue from the
    end-to-end validation run and are deliberately not shipped, so this check
    skips in a clean clone rather than failing.
    """
    props_path = REPO_ROOT / "remotion-composer/public/demo-props/million-billion-trillion.json"
    if not props_path.exists():
        pytest.skip(
            "optional local validation composition props "
            "(remotion-composer/public/demo-props/million-billion-trillion.json) are not present "
            "in a clean clone; this check only runs where the validation run was performed"
        )
    props = json.loads(props_path.read_text(encoding="utf-8"))
    assert props.get("theme") == "premium-minimalist"
    assert props["theme"] not in PRESETS, "premium-minimalist must not be a built-in preset"
    assert "themeConfig" in props
    assert "themeConfigWins" not in props, "the regression project must not opt in"


def test_local_demo_props_carry_no_conflicting_theme_config():
    """No shipped demo supplies BOTH a built-in preset name and a themeConfig."""
    conflicts = []
    for path in sorted((REPO_ROOT / "remotion-composer/public/demo-props").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        name = data.get("theme") or data.get("playbook")
        if name in PRESETS and "themeConfig" in data:
            conflicts.append(path.name)
    assert conflicts == [], f"these demos would change if the default flipped: {conflicts}"


def test_no_theme_test_depends_on_the_gitignored_project():
    """Clean-clone guard: this suite must not read the gitignored project tree.

    The needle is assembled at runtime so this guard does not match itself.
    """
    forbidden = "projects/" + "million-billion-trillion"
    source = Path(__file__).read_text(encoding="utf-8")
    assert forbidden not in source
