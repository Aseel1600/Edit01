---
type: project
status: active
updated: 2026-04-08
---

# OpenMontage Project

## Role
Experimental media production backend for content and video workflows.

## Current Decision
Use OpenMontage as a specialized callable production system inside the larger content factory, not as the top-level orchestration layer.

## Best First Use Case
- long clip -> short explainer
- repurposed short-form content
- reference video -> derivative concept and draft production path

## Canonical Paths
- Windows: `C:\-PROJECT-FOLDERS-\OpenMontage`
- WSL: `/mnt/c/-PROJECT-FOLDERS-/OpenMontage`
- (corrected 2026-06-27 — old `...\Desktop\HUB\...` path was stale/nonexistent)

## Status
- Repo cloned
- WSL environment set up
- Base dependencies installed
- Extra source-ingest and analysis dependencies installed
- Contract tests passing
- Remotion render validated

## Runtime Config
- Runtime secrets live in repo-local `.env`
- Documentation and process notes live in the second brain
- Do not store real API keys in vault markdown

## Pilot Status (2026-06-27)
**v4 rendered.** `renders/forgotten-history-esb-b25_v4.mp4` — 1:29, 1080p. Adds: burned word-timed
**captions** (faster-whisper "base" transcribe of the Onyx VO → ASS, 82 cues), a **somber music bed**
(original FFmpeg-synthesized drone — zero licensing risk, mixed under VO via loudnorm I=-16:TP=-1.5
to avoid clipping; swappable by dropping a track in music_library/), and an **ESB-specific foggy cold
open** (pex-esb-fog, replacing the Brooklyn Bridge). Music boost initially clipped (0 dBFS) — fixed
with loudnorm remux. Below = v3 baseline.

**v3 rendered, end-to-end.** `renders/forgotten-history-esb-b25_v3.mp4` — 1:29, 1080p, 12 crossfading shots.
Onyx narration (Voicebox/Kokoro) + Pexels/B-25 real motion + crash stills with blurred-bg fill.
v3 added user-supplied press photos: **real Betty Lou Oliver (on crutches)**, her newspaper,
a high-res impact hole, and a stretcher casualty. Audio-cutoff finally fixed — root cause was an
afade starting at 87.9s that faded out the final word; now the fade lives only in a trailing pad.
NOTE: the user-supplied Betty Lou / stretcher / hole-hires images are AP/press (not PD) — carry
Content-ID risk on a monetized channel; user supplied them knowingly. Built with FFmpeg, not full
OM pipeline. Optional next: captions, music bed, ESB-specific cold open (still opens on Brooklyn Bridge).

## Next Practical Step
Run the **Forgotten History pilot** — the first real end-to-end job (defined 2026-06-27).

- Brief (runner copy, gitignored): `OpenMontage/projects/forgotten-history-esb-b25-pilot/BRIEF.md`
- Pipeline: `cinematic` (documentary montage), playbook `clean-professional`, ~2:00 / under 3:00.
- Topic (swappable): the B-25 bomber that hit the Empire State Building, July 28 1945 — picked
  because real 1945 newsreel footage exists AND period stills, exercising both visual paths.
- Core rule — **footage ladder**: (1) real archival motion footage → (2) real stock motion →
  (3) genuine period still animated via local WAN image-to-video / Remotion Ken Burns →
  (4) AI-generated only as last-resort gap fill. "Real place ⇒ real footage." Locks the channel
  to real video over static images.
- WAN i2v fallback = the same WAN models running in the WanGP UI (localhost:7862), called as a
  pipeline step via the `wan_video` tool — so WanGP and OpenMontage are complementary, not rivals.
- Preflight run 2026-06-27. Configured `.env` (repo-local, gitignored — NOT in vault):
  `PEXELS_API_KEY` + `FAL_KEY`. This lit up `pexels_video`/`pexels_image` (free real stock) and
  Fal's `kling_video`/`veo_video`/`minimax_video` (cloud image-to-video) + `flux_image`.
  Capability now: video_generation 4/14, image_generation 4/9, video_post 8/8, Piper TTS ✅.
- Two preflight realities: (1) OM has **no Archive.org/Wikimedia tool** — rung-1 archival footage
  is sourced manually into `assets/`. (2) OM's `wan_video` wants HF-Diffusers weights and can't
  reuse the local WanGP models, so pilot rung-3 still-animation uses **Fal Kling i2v** (integrated);
  WanGP stays the free/local i2v option for volume later.
- Pilot cost ≈ $0 free path (archival + Pexels + Ken Burns), or ~$1–3 if using Fal Kling i2v on stills.

## Related Notes
- `vault/hardware/openmontage.md`
- `vault/workflows/env-and-secrets-organization.md`
