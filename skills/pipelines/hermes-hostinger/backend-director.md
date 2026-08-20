# Backend Director — Hermes Hostinger

## When to Use
Build and deploy the Hermes API (`services/hermes-api`) to the Hostinger
domain, or run it locally when VPS credentials are missing.

## Prerequisites
| Layer | Resource |
|-------|----------|
| Tool | `hostinger_deploy` |
| Code | `services/hermes-api/` |
| Workflow | `.github/workflows/deploy-hostinger.yml` |
| Prior | `deploy_report` with tunnel decision |

## Process

### Step 1: Scaffold
```
hostinger_deploy.execute({
  "action": "scaffold",
  "domain": "<brief domain>"
})
```
Confirm `docker-compose.yml` and `Dockerfile` exist under
`services/hermes-api/`.

### Step 2: Production env
Required on the VPS:
- `HERMES_API_KEY` (non-empty)
- `INFERENCE_BASE_URL` (NVIDIA vLLM or hosted API) **or** `LM_STUDIO_BASE_URL` (tunnel/studio fallback)
- `PUBLIC_DOMAIN` (e.g. `hermestudios.com`)
- Scale templates: `infra/hermes-scale/` (NVIDIA default; do not buy GPUs from the agent)

Refuse to mark `deployed: true` if the production key is empty.

### Step 3: Deploy
If `HOSTINGER_API_KEY` and `HOSTINGER_VM_ID` are set:
```
hostinger_deploy.execute({"action": "deploy", "domain": "..."})
```
Else run locally:
```
hostinger_deploy.execute({"action": "serve_local"})
```
and tell the user the GitHub Action path
(`.github/workflows/deploy-hostinger.yml` + hPanel API key + VM id).
Do not subscribe to a new VPS.

### Step 4: DNS
Domain `hermestudios.com` is active: point A/AAAA at the VPS, or CNAME
if Hostinger documents that for the site. Record the intended URL on
`deploy_report.backend.url`.

### Step 5: Self-evaluate
| Criterion | Question |
|-----------|----------|
| Auth | Is HERMES_API_KEY required in production? |
| Compose | Does `docker compose config` succeed? |

### Step 6: Submit
Checkpoint `backend` `awaiting_human`. **END YOUR TURN**.

## Common Pitfalls
- Pushing an image that still proxies with auth disabled.
- Deploying the whole OpenMontage GPU stack to a tiny VPS (API-only).
