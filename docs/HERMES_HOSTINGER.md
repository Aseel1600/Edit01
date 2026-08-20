# Hermes Hostinger — local LM Studio + public API + YouTube

Wire a **free local** LM Studio server to a **public Hostinger domain**
(`hermestudios.com`) and optionally upload OpenMontage renders to YouTube.

This is not a video compose pipeline. Renders still come from `hermes-flywheel`
or a base OpenMontage pipeline.

```
Mac LM Studio  :1234/v1          (studio / fallback only)
      │
      │  optional Cloudflare Tunnel
      ▼
Hostinger VPS  services/hermes-api
      https://hermestudios.com
      │
      ▼
NVIDIA vLLM or hosted /v1        (infra/hermes-scale)
```

Scale templates (do not purchase from the agent): `infra/hermes-scale/`
Planning session: `cse_01PrUJjvaENr4zTMsM1UB4Bb`.

## Files
| Path | Role |
|------|------|
| `pipeline_defs/hermes-hostinger.yaml` | Manifest |
| `skills/pipelines/hermes-hostinger/` | Stage directors |
| `skills/creative/hermes-hostinger.md` | Driver skill |
| `.cursor/skills/hermes-hostinger-pipeline/` | Cursor skill |
| `tools/llm/lmstudio.py` | Local OpenAI-compatible client |
| `tools/publishers/youtube_upload.py` | YouTube CLI / tool |
| `tools/publishers/hostinger_deploy.py` | Scaffold + VPS gate |
| `services/hermes-api/` | FastAPI backend + landing page |
| `infra/hermes-scale/` | NVIDIA/AMD/hosted/Mac env + vLLM compose |
| `.github/workflows/deploy-hostinger.yml` | Hostinger VPS deploy |

## Run locally
```bash
python scripts/hermes_hostinger.py preflight
python scripts/hermes_hostinger.py serve
# http://127.0.0.1:8080/health
```

Start LM Studio's local server on port 1234 first if you want `/v1` to proxy.

## Deploy to Hostinger
1. `hermestudios.com` is already active — point its DNS (A/AAAA) at the VPS.
2. Add GitHub secrets `HOSTINGER_API_KEY`, `HERMES_API_KEY`, `LM_STUDIO_BASE_URL`
   and variable `HOSTINGER_VM_ID`.
3. Run the **Deploy Hermes API to Hostinger** workflow.

Do not buy a VPS or plan from the agent. Local `serve` is enough to verify.

## YouTube
```bash
python -m tools.publishers.youtube_upload --status
python -m tools.publishers.youtube_upload --file renders/final.mp4 --title "..." --dry-run
```
Default privacy is **unlisted**. Needs `YOUTUBE_CLIENT_SECRETS_FILE`.
