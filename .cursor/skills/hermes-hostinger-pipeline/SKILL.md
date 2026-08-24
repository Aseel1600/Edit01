---
name: hermes-hostinger-pipeline
description: >-
  Run the Hermes Hostinger pipeline: scaffold the FastAPI gateway, point
  Hostinger DNS (A/@ and A/www) at the VPS, and publish hermestudios.com.
  Use when the user asks to create this pipeline skill, host via DNS, deploy
  to Hostinger, expose LM Studio, or mentions hermestudio.com / hermestudios.com.
---

# Hermes Hostinger Pipeline

Infrastructure + delivery. Not a video compose pipeline.

```
Clients → https://hermestudios.com (Caddy TLS on Hostinger VPS)
        → hermes-api :8080
        → INFERENCE_BASE_URL (vLLM / hosted /v1)
Mac LM Studio :1234 is studio fallback only
```

## Canonical domain

The user may write `hermestudio.com` or `@hermestudio.com`. That name is **not**
in the Hostinger portfolio. Map it to **`hermestudios.com`** (active). Do not
register or buy `hermestudio.com`.

| Domain | Role |
|--------|------|
| hermestudios.com | Canonical — DNS + TLS target |
| www.hermestudios.com | A record, same IPv4 |
| hermestudios.org | Active alias |
| hermestudios.online | Alias (hPanel may still say pending setup) |
| hermestudioos.com | Typo domain — alias only, never canonicalize |

Keep Hostinger nameservers. Do not move the zone to Cloudflare unless asked.

## First actions

1. Work in the OpenMontage repo. Read `pipeline_defs/hermes-hostinger.yaml`.
2. Read `skills/creative/hermes-hostinger.md`.
3. For each stage, read `skills/pipelines/hermes-hostinger/<stage>-director.md`
   before acting.
4. Use tools `lmstudio`, `hostinger_deploy`, `youtube_upload`, `export_bundle`.
   Do not write ad-hoc API clients.

Stage order:

`idea → preflight → tunnel → backend → dns → publish → verify`

## Operator checklist

```
Task Progress:
- [ ] Canonical domain locked to hermestudios.com
- [ ] Scaffold services/hermes-api (compose + Caddy TLS profile)
- [ ] Local /livez and /health succeed
- [ ] HERMES_API_KEY set before marking deployed
- [ ] Hostinger DNS A/@ and A/www point at VPS IPv4
- [ ] https://hermestudios.com/health returns ok
- [ ] Unauthenticated POST /v1/chat/completions returns 401
```

## Commands

```bash
python scripts/hermes_hostinger.py preflight
python scripts/hermes_hostinger.py serve
python scripts/hermes_hostinger.py deploy --domain hermestudios.com
python scripts/hermes_hostinger.py dns --domain hermestudios.com
python scripts/hermes_hostinger.py dns --apply --domain hermestudios.com --ipv4 <VPS_IPV4>
```

Local API: `http://127.0.0.1:8080/livez` and `/health`

## DNS (Hostinger zone)

Use `hostinger_deploy` — never raw curl with a pasted token in chat.

```
hostinger_deploy.execute({"action": "dns_status", "domain": "hermestudios.com"})
hostinger_deploy.execute({
  "action": "dns_apply",
  "domain": "hermestudios.com",
  "ipv4": "<VPS_IPV4>"
})
```

`dns_apply` PUTs **only** `A @` and `A www` with `overwrite: true` (replaces
matching name+type; leaves MX/TXT). Source the IPv4 from, in order:

1. `ipv4` argument
2. `HOSTINGER_VPS_IP`
3. Hostinger VPS API using `HOSTINGER_VM_ID`

Needs `HOSTINGER_API_KEY` (hPanel → API). If the key or IPv4 is missing, record
`deploy_report.dns.status = blocked` and continue local serve. Do not buy a VPS.

hPanel path if the API is unavailable: Domains → hermestudios.com → DNS / Manage
→ A `@` and A `www` → VPS public IPv4.

Payload details: [reference.md](reference.md)

## Backend

Scaffold and compose live in `services/hermes-api/`. Production TLS:

`COMPOSE_PROFILES=tls` (Caddy 80/443).

GitHub Actions: `.github/workflows/deploy-hostinger.yml`

Secrets/vars (user adds; do not purchase):

- `HOSTINGER_API_KEY`, `HOSTINGER_VM_ID`
- `HERMES_API_KEY`
- `INFERENCE_BASE_URL` / `INFERENCE_API_KEY` (preferred public path)
- `LM_STUDIO_BASE_URL` (tunnel URL if Mac is fallback)
- `HOSTINGER_VPS_IP` (optional if VM id can resolve it)

Scale configs: `infra/hermes-scale/`. Do not buy GPUs.

## Hard rules

- Do not expose `:1234` publicly.
- Do not pay for Hostinger, ngrok, domains, or cloud LLM without asking.
- Production `/v1/*` requires `HERMES_API_KEY`.
- Cloud agents cannot verify localhost; use the `lmstudio` tool on the Mac.
- Default YouTube privacy is unlisted.
- If hPanel shows a login wall, stop and ask the user to sign in. Do not
  guess passwords or complete OAuth for them.
