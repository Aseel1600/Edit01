---
name: hermes-hostinger-pipeline
description: >-
  Run the Hermes Hostinger skill workflow: LM Studio local OpenAI-compatible
  inference on port 1234, Hostinger-domain FastAPI backend for hermestudios.com,
  optional YouTube uploader CLI, and GitHub Actions VPS deploy. Use when the
  user asks to create this pipeline skill, expose LM Studio, deploy to Hostinger,
  or wire YouTube upload to OpenMontage.
---

# Hermes Hostinger Pipeline

## When to use
User wants local LM Studio (Qwen coder) + a public backend on Hostinger
domains (`hermestudios.com` canonical, `hermestudios.online`/`.org` aliases) + optional YouTube upload.

## First actions
1. Read `pipeline_defs/hermes-hostinger.yaml`.
2. Read `skills/creative/hermes-hostinger.md`.
3. For each stage, read `skills/pipelines/hermes-hostinger/<stage>-director.md`
   before doing that stage's work.
4. Use tools `lmstudio`, `hostinger_deploy`, `youtube_upload`, `export_bundle`.
   Do not write ad-hoc API clients.

## Architecture
```
Clients → https://hermestudios.com (Hostinger hermes-api)
        → INFERENCE_BASE_URL (NVIDIA vLLM / hosted)
Mac LM Studio :1234 is studio fallback only (infra/hermes-scale)
```

Video production stays on the Mac via OpenMontage pipelines. The VPS is
an API gateway + landing page, not a GPU renderer.

## Commands
```bash
python scripts/hermes_hostinger.py preflight
python scripts/hermes_hostinger.py serve
python -m tools.publishers.youtube_upload --help
```

Local API: `http://127.0.0.1:8080/health`

## Deploy
GitHub Actions: `.github/workflows/deploy-hostinger.yml`

Secrets/vars (user must add; do not buy a VPS):
- `HOSTINGER_API_KEY`
- `HOSTINGER_VM_ID`
- `HERMES_API_KEY`
- `INFERENCE_BASE_URL` (vLLM or hosted `/v1`; preferred for public traffic)
- `INFERENCE_API_KEY`
- `LM_STUDIO_BASE_URL` (tunnel URL if using the Mac as fallback)

Scale configs: `infra/hermes-scale/` (NVIDIA default). Do not buy GPUs from the agent.

## Hard rules
- Do not expose `:1234` publicly.
- Do not pay for Hostinger, ngrok, or cloud LLM without asking.
- Cloud agents cannot verify localhost; use the `lmstudio` tool on the Mac.
- Default YouTube privacy is unlisted.

## Extra reference
See [reference.md](reference.md) for env vars, routes, and DNS notes.
