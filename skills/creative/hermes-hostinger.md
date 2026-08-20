---
name: hermes-hostinger
description: >-
  Drive the Hermes Hostinger pipeline: local LM Studio (OpenAI-compatible
  :1234) as free inference, a public FastAPI backend on a Hostinger domain
  (hermestudios.com), and optional YouTube upload of OpenMontage renders.
  Use when the user mentions LM Studio, Hostinger, hermestudios, Qwen coder
  local server, exposing localhost:1234, or deploying the Hermes API.
---

# Hermes Hostinger — Driver Skill

Stand up the public Hermes API in front of local LM Studio. Do **not**
compose video here. Read `pipeline_defs/hermes-hostinger.yaml` and each
`skills/pipelines/hermes-hostinger/*-director.md` stage by stage.

```
Users → Hostinger Hermes API (hermestudios.com)
      → INFERENCE_BASE_URL (NVIDIA vLLM or hosted /v1)
Mac LM Studio :1234 is studio / fallback only (infra/hermes-scale)
Optional: export_bundle → youtube_upload
```

## Defaults (override only with user approval)
- Domain: `hermestudios.com`
- LM Studio: `http://127.0.0.1:1234/v1`
- Model: whatever `/v1/models` returns (often a Qwen coder 30B)
- YouTube privacy: unlisted
- Cost: $0 unless the user approves a paid tunnel/VPS/LLM

## Tool map
| Need | Tool |
|------|------|
| Ping / chat local server | `lmstudio` |
| Docker + Hostinger VPS | `hostinger_deploy` |
| YouTube | `youtube_upload` after `export_bundle` |
| Local API | `python scripts/hermes_hostinger.py serve` |

## Guardrails
- Never publish raw port 1234.
- Production requires `HERMES_API_KEY`.
- Never purchase Hostinger or API credits without asking.
- Cloud agents cannot reach the user's localhost — run health checks as
  local tools, not as assumed-success.

## Output
Public URL, health JSON, whether YouTube uploaded or skipped, and a
`deploy_report` in `projects/<id>/`.
