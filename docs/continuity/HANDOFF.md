# HANDOFF

## Objective

Ship the OAuth + kit-contract work to `suyaleo/OpenMontage` main and open the local studio so the owner can start a real production.

## Current State

Local checkout is `/Users/macbook/Developer/open-montage`. Live Git outranks the snapshot below.

- Fork origin: https://github.com/suyaleo/OpenMontage
- Upstream remains `calesthio/OpenMontage` (no upstream PR unless asked)
- Grok/GPT OAuth live smoke passed
- `.env` stays local and gitignored; no tokens committed
- Backlot is the local use surface (`python -m backlot open`)

## Decisions This Slice

- D-20260820-05 Grok/GPT providers use workstation OAuth, not API keys
- Commit and merge to the fork `main` on explicit user request
- Do not open a PR against upstream in this slice

## Files Changed

- OAuth wiring, kit contracts, Cursor adapter files, tests, HANDOFF

## Verification Evidence

```text
pytest oauth/openai/grok quality: 16 passed
live oauth smoke: grok_image + openai_image wrote projects/oauth-smoke/*.png
```

## Risks / Blockers

- This is a local studio, not a hosted SaaS deploy.
- Sora and OpenAI TTS still need `OPENAI_API_KEY`.
- Grok HTTP 403 is an entitlement failure; do not retry.

## Next Exact Actions

1. Open Backlot library and keep the local venv active.
2. On a video request, read `AGENT_GUIDE.md`, run preflight, pick a pipeline.
3. Do not PR upstream unless the user asks.

## Resume Point

Fork main should hold the OAuth + kit work. Real use starts in this workspace with Backlot open and `AGENT_GUIDE.md`.

<!-- ark:git-state -->
Checkpoint captured: 2026-08-20T03:49:00+09:00
Branch at checkpoint: main
HEAD at checkpoint: 1bab711
<!-- /ark:git-state -->
