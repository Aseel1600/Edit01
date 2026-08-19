# Composition Contracts — Subtitles, Themes, Slideshow Risk

Reference for three contracts that sit between the governed artifacts and the
renderers. Written after the post-validation engineering revisions; evidence in
`engineering/post-validation-2026-08-19/`.

---

## 1. Subtitle contract

Canonical subtitle settings live on `edit_decisions.subtitles` (schema:
`schemas/artifacts/edit_decisions.schema.json`). `video_compose` translates them
into an ASS `force_style` string for the FFmpeg `subtitles` filter.

### Canonical fields

| Field | Type | Meaning | Maps to |
|---|---|---|---|
| `enabled` | boolean | burn subtitles at all | — |
| `style` | string | **display** style: `sentence`, `word-by-word`, `karaoke` | nothing visual — it is not a style map |
| `source` | string | path to the subtitle file | filter input |
| `font` | string | font family | `FontName` |
| `font_size` | integer | **video pixels** at the output height | `FontSize` (converted, see below) |
| `color` | string | text colour, `#RRGGBB` or `&HAABBGGRR` | `PrimaryColour` |
| `outline_color` | string | outline colour, hex or ASS | `OutlineColour` |
| `background` | string | caption box colour, `#RRGGBB` or `#RRGGBBAA` | `BackColour` + `BorderStyle=3` |
| `position` | enum | `top-center` \| `center` \| `bottom-center` | `Alignment` 8 / 5 / 2 |
| `vertical_margin` | integer | **video pixels** from the aligned edge | `MarginV` (converted) |
| `max_words_per_line` | integer | cue-splitting hint | carried to caption tools |

`style` is a display-style **string**. Styling belongs in the sibling fields.

### PlayRes-aware sizing (why pixels ≠ ASS units)

FFmpeg converts SRT to ASS on a fixed script canvas — its generated header reads
`PlayResX: 384 / PlayResY: 288` — and libass scales that canvas to the frame. An
ASS `FontSize` of *N* therefore renders at `N × video_height / 288` pixels.

Canonical sizes are expressed in video pixels and converted:

```
ass_units = canonical_px × 288 / video_height
```

`video_compose` probes the real output height, so 42 px looks the same at
1080p (`FontSize=11.2`), 720p (`16.8`) and 2160p (`5.6`). The same conversion
applies to `vertical_margin`.

> **Do not treat raw ASS `MarginV`/`FontSize` as frame pixels.** On a 1080-line
> frame, `MarginV=160` is ~600 px from the edge, not 160 px.

### Colour conversion

ASS orders bytes `&HAABBGGRR` (alpha-blue-green-red) and treats alpha as
*transparency* — the inverse of CSS. `#111827` becomes `&H00271811`;
`#00000088` (53 % opaque) becomes `&H77000000`. Values already written as `&H…`
pass through untouched.

### Precedence

```
defaults  →  style playbook  →  canonical subtitles fields  →  explicit native/ASS override
```

Native keys (`ass_font_size`, `primary_color`, `back_color`, `alignment`,
`margin_v`, `border_style`, `outline_width`, `shadow`, `bold`) always win, so a
caller that already speaks ASS is never overwritten by a higher-level field.
Omitting every canonical field reproduces the historical default exactly:

```
FontName=Inter,FontSize=28,Bold=1,BorderStyle=1,Outline=2,Shadow=0,MarginV=40,Alignment=2
```

---

## 2. Theme precedence

`remotion-composer/src/Root.tsx` → `resolveTheme` resolves a composition theme
from three inputs: a preset **name** (`theme` / `playbook`), an explicit
**`themeConfig`** object, and `DEFAULT_THEME`.

### Legacy (default)

A recognised preset name wins and an explicit `themeConfig` is ignored.
Built-in presets: `clean-professional`, `flat-motion-graphics`,
`minimalist-diagram`, `anime-ghibli`. A name with no matching preset falls
through to `themeConfig`, then to `DEFAULT_THEME`.

### Opt-in — `themeConfigWins: true`

Set the composition prop to make the explicit config the final override:

```
DEFAULT_THEME  →  named preset  →  themeConfig
```

Merging is field-level, so a partial `themeConfig` refines a preset instead of
replacing it — unspecified fields keep the preset's values.

This exists for **playbook-derived theme customisation**: `video_compose`
builds a `themeConfig` from the style playbook's own palette, and without the
opt-in that config is discarded whenever the playbook name happens to match a
built-in preset.

```json
{ "theme": "clean-professional", "themeConfig": { "accentColor": "#2563EB" }, "themeConfigWins": true }
```

Legacy precedence remains the default. Whether it changes in a future release
has not been decided.

---

## 3. Slideshow risk

`lib/slideshow_risk.py` scores a plan across six dimensions and returns
`strong` / `acceptable` / `revise` / `fail`.

- **Canonical representation: `scene_plan.scenes`.** Every dimension reads
  scene_plan fields (`shot_intent`, `narrative_role`, `information_role`,
  `hero_moment`, `shot_language`). `edit_decisions.cuts` cannot carry them
  (`additionalProperties: false`), so scoring from cuts is information-poor and
  reports materially higher risk for the same production — it is a diagnostic
  fallback only.
- **Default enforcement: report-only.** A `fail` verdict is reported as a
  warning and does not stop compose. `VideoCompose.last_slideshow_risk` records
  the score, verdict, scene representation and any scorer exception.
- **Blocking is opt-in and not recommended yet.**
  `OPENMONTAGE_SLIDESHOW_RISK_ENFORCEMENT=block` restores the blocking branch,
  but the thresholds have not been calibrated against real productions and the
  scorer has known false positives on annotation-sparse plans. See the follow-up
  record before enabling it.
