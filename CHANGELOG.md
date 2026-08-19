# Changelog

All notable changes to OpenMontage are recorded here.

This file starts with the post-validation engineering release below; earlier
history lives in the git log.

## [Unreleased] — Composition contract repairs (post-validation Revisions 1–2D)

Component versions in this entry: `video_compose` 0.1.0 → **0.2.0**,
`composition_validator` 0.1.0 → **0.2.0**, `remotion-composer` 1.0.0 → **1.1.0**.
Artifact schema versions are unchanged (all additions are optional fields).

All items were found by an end-to-end zero-cost production validation and fixed
under staged review; evidence lives in `engineering/post-validation-2026-08-19/`.

### Fixed

- **StatCard was unreadable on light playbooks.** `Explainer` never forwarded a
  text colour, so the subtitle fell back to `#FFFFFF`. Theme text colour is now
  forwarded on light surfaces.
- **KPIGrid could not show exact values.** Counters were rounded to integers and
  values ≥ 1000 were abbreviated ("31.7K"), with no way to opt out.
- **HeroTitle / SectionTitle / StatReveal ignored the theme.** Near-white text
  and a dark scrim were hard-coded, failing contrast on light playbooks.
- **ComparisonCard per-side colours were dropped.** `cut.leftColor` /
  `cut.rightColor` were never forwarded, so component defaults always won.
- **Overlay timing errors surfaced only mid-render.** Wrong keys produced
  `The "from" prop of a sequence must be finite, but got NaN` after bundling;
  `composition_validator` now rejects them first and names the supported keys.
- **Canonical subtitle fields never reached the renderer.** `color`,
  `position` and `font_size` were silently dropped, and hex colours were emitted
  where ASS requires `&HAABBGGRR`.
- **`subtitles.style: "sentence"` crashed compose.** The schema types `style` as
  a display-style string, but the resolver called `.items()` on it
  (`AttributeError: 'str' object has no attribute 'items'`).
- **Subtitle sizing ignored the libass canvas.** `font_size` was passed straight
  through as an ASS unit; ffmpeg renders SRT on a 384×288 script canvas, so a
  requested 42 px rendered roughly 3.75× too large. Sizes are now converted
  against the real output height.
- **Slideshow-risk scoring never ran.** `_pre_compose_validation` passed the
  scene_plan *artifact* where the scorer expected the scenes *list*; iterating
  the dict raised `'str' object has no attribute 'get'`, which a bare `except`
  swallowed as a log line. Input is normalised and failures are now reported.
- **Playbook-derived subtitle colours were emitted as raw hex** and therefore
  ignored by libass.

### Added

- **`edit_decisions.templated`** (optional) — records the composition-props file
  that produced a render (`composition_props_path`, optional
  `composition_props_sha256`, `composition_id`), so a templated run is auditable
  without duplicating Remotion scene props into `cuts`.
- **`edit_decisions.subtitles.vertical_margin`** (optional, integer, video-space
  pixels) — canonical control over caption distance from the aligned edge,
  converted to ASS `MarginV` against the output height. Follows the
  `video_stitch.pip_margin` contract.
- **KPIGrid `decimals` / `abbreviate`** (optional, per-metric or grid-wide) —
  render `11.6 days`, `31.7 years`, `31,700 years` exactly. Defaults reproduce
  the previous output.
- **Optional theme-colour props** on `HeroTitle`, `SectionTitle` and
  `StatReveal`, defaulting to the previous constants.
- **`themeConfigWins`** (optional composition prop) — opt in to explicit
  `themeConfig` overriding a named preset, merged field by field.
- **Slideshow-risk diagnostics** — score, verdict, scene representation and any
  scorer exception are recorded on `VideoCompose.last_slideshow_risk`, and
  `OPENMONTAGE_SLIDESHOW_RISK_ENFORCEMENT` selects `report_only` (default) or
  `block`.

### Changed — behaviour

**Canonical subtitle fields and playbook-driven subtitle colours that were
previously ignored are now applied correctly, so rendered captions may change
appearance.** A project that declared `color`, `position` or `font_size` under
`edit_decisions.subtitles`, or that relied on a style playbook while burning
subtitles, will see captions that finally match its declaration.

Compatibility verified by the regression suite: the default subtitle style is
byte-identical to before, callers that pass explicit native/ASS overrides are
unaffected, and dark-theme component rendering is byte-identical across all four
built-in presets.

### Not enabled by default

- **Slideshow-risk blocking is NOT enabled.** The restored scorer is
  report-only; a `fail` verdict warns and does not stop compose. Enabling
  `OPENMONTAGE_SLIDESHOW_RISK_ENFORCEMENT=block` is not recommended until the
  calibration work in the follow-up record is done.
- **`themeConfigWins` is NOT the default.** A recognised preset name still wins
  unless a composition opts in; existing preset-named projects are unchanged.
