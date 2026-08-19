# Follow-up engineering items

Found during the post-validation revisions (1 → 2D) and deliberately **not**
fixed there. None blocks the accepted release; each is scoped so it can be
picked up independently.

---

## F1 — `styles/anime-ghibli.yaml` fails playbook schema validation

**Problem.** The playbook declares `overlays.section_title`, which
`schemas/styles/playbook.schema.json` does not permit (`overlays` allows only
`stat_card`, `key_term`, `code_block`, `additionalProperties: false`).
`load_playbook` therefore raises, `_build_theme_from_playbook` returns nothing,
and the playbook can never contribute a `themeConfig`.

**Evidence.** `engineering/post-validation-2026-08-19/E10_PLAYBOOK_DIVERGENCE.json`
records `anime-ghibli` as `playbook_loadable: false`; the validation error names
`section_title` explicitly.

**Risk.** Low today (the built-in preset silently covers it), but it makes
`anime-ghibli` the one playbook whose YAML palette is unreachable, and it would
become visible the moment theme precedence flips (F5).

**Recommended next action.** Decide whether `section_title` is a legitimate
overlay style; if so add it to `playbook.schema.json` (additive), otherwise
correct the YAML. Add a test that every file in `styles/*.yaml` loads.

---

## F2 — Slideshow-risk typography dimension uses the wrong vocabulary

**Problem.** `_score_typography` counts scene types `text_card`, `stat_card`,
`kpi_grid` — those are **Remotion cut-type** names. `scene_plan.type` is a
different enum (`talking_head`, `broll`, `animation`, `character_scene`,
`diagram`, `text_card`, `transition`, `generated`, `screen_recording`), and only
`text_card` overlaps. On the canonical representation the dimension therefore
under-counts text-first productions.

**Evidence.** `E6_ANALYSIS.json`: the same five-scene production scores
`typography_overreliance` 1.0 from `scene_plan` but 4.0 from the composition
props, where the real cut types are visible. Four of its five scenes are text
cards.

**Risk.** A genuine false negative in the dimension that exists to catch
"animated slides" — and it would matter much more if enforcement were enabled.

**Recommended next action.** Score typography from the scene's declared
`animation_mode`/component mapping, or map scene_plan types to a text-first
predicate; then re-baseline the dimension against F3's dataset.

---

## F3 — No calibration dataset or expected verdicts for slideshow risk

**Problem.** The scorer's bands (`< 2.0` strong, `< 3.0` acceptable, `< 4.0`
revise, `>= 4.0` fail) have never been validated against real productions,
because the check never executed (the crash fixed in Revision 2B). Only two
local productions exist to score, and `tests/eval/golden_scenarios/` declares no
`expected_slideshow_verdict` for any scenario.

**Evidence.** `E6_ANALYSIS.json` project sweep (n = 2);
`bench_runner.py` supports `expected_slideshow_verdict`, but
`talking_head_basic.json` leaves it unset.

**Risk.** Thresholds are unproven, and two of six dimensions
(`decorative_visuals`, `weak_shot_intent` — 10 of 30 points) key on *optional*
scene_plan annotations, so the score partly measures artifact completeness
rather than slideshow-ness.

**Recommended next action.** Score ≥ 10 real productions in report-only mode,
record verdict vs. human judgement, then set `expected_slideshow_verdict` on the
golden scenarios and recalibrate the bands.

---

## F4 — Possible human-gated slideshow-risk enforcement

**Problem.** Enforcement is currently binary in code: report-only, or block
compose outright. A blocking gate on an uncalibrated check with known false
positives would have stopped a production that passed end-to-end validation.

**Evidence.** The frozen regression project scores `0.67 / strong` from its
scene_plan but `3.42 / revise` from composition props; under the old blocking
branch a `fail` from the cuts shape would have blocked a good render.

**Risk.** Enabling `block` prematurely stops legitimate work; leaving it purely
advisory means the signal is easy to ignore.

**Recommended next action.** After F2 and F3, route the verdict into the
reviewer/checkpoint surface (where a human already approves `assets`) rather
than into `_pre_compose_validation`. Treat automatic blocking as a later,
separate decision.

---

## F5 — Possible default flip for `themeConfig` precedence

**Problem.** A recognised preset name still beats an explicit `themeConfig`
unless a composition opts in with `themeConfigWins`. That contradicts the intent
recorded in `video_compose.py` ("every video gets a unique visual identity
derived from its production decisions — not picked from a preset menu").

**Evidence.** `E10_PROJECT_SWEEP.json`: no shipped demo would change (the three
preset-named demos carry no `themeConfig`). `E10_PLAYBOOK_DIVERGENCE.json`: the
three loadable preset-named playbooks differ from their preset in exactly one
field, `surfaceColor`, because the YAML has no `surface` key and the loader
falls back to `background`.

**Risk.** Flipping the default is a visible change for any third-party project
that supplies both a preset name and a `themeConfig`. Classified per preset as
*minor* (clean-professional, flat-motion-graphics, minimalist-diagram) and *no
visible change* (anime-ghibli, whose playbook cannot load — see F1).

**Recommended next action.** Fix F1, consider adding an explicit `surface` key
to the three playbook YAMLs so the flip is intentional rather than a fallback
artefact, then flip the default in a minor release with the preset goldens
re-captured. Do not flip before that.
