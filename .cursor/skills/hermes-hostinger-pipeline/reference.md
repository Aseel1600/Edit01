# Hermes Hostinger — reference

## Domains
| Domain | Role |
|--------|------|
| hermestudios.com | Canonical (active, DNS + TLS target) |
| hermestudio.com | User shorthand — map to hermestudios.com; not in portfolio; do not buy |
| hermestudios.online | Alias (hPanel: pending setup) |
| hermestudios.org | Active alias |
| hermestudioos.com | Typo domain — do not canonicalize |

## Environment
| Variable | Purpose |
|----------|---------|
| `LM_STUDIO_BASE_URL` | Default `http://127.0.0.1:1234/v1` (studio fallback) |
| `INFERENCE_BASE_URL` | Production NVIDIA/hosted OpenAI-compatible `/v1` |
| `INFERENCE_API_KEY` | Upstream vLLM or vendor key |
| `INFERENCE_BACKEND` | `vllm` / `hosted` / `lm_studio` |
| `INFERENCE_MODEL` | Served model id |
| `HERMES_MAX_INFLIGHT` | Gateway concurrency cap (default 32) |
| `LM_STUDIO_API_KEY` | Optional; LM Studio often ignores it |
| `LM_STUDIO_MODEL` | Override loaded model id |
| `HERMES_API_KEY` | Required in production for `/v1/*` |
| `PUBLIC_DOMAIN` | `hermestudios.com` |
| `HOSTINGER_API_KEY` | hPanel API token (Bearer) |
| `HOSTINGER_VM_ID` | VPS id for deploy-on-vps and IP lookup |
| `HOSTINGER_VPS_IP` | Public IPv4 for DNS A records |
| `YOUTUBE_CLIENT_SECRETS_FILE` | OAuth client JSON |
| `YOUTUBE_PRIVACY` | Default `unlisted` |

## Public routes
| Method | Path | Auth |
|--------|------|------|
| GET | `/` | no |
| GET | `/livez` | no |
| GET | `/readyz` | no (503 if production key missing) |
| GET | `/health` | no |
| GET | `/v1/models` | bearer |
| POST | `/v1/chat/completions` | bearer |
| POST | `/api/youtube/upload` | bearer |

## Hostinger DNS API

Base: `https://developers.hostinger.com`

| Action | Method | Path |
|--------|--------|------|
| List records | GET | `/api/dns/v1/zones/{domain}` |
| Apply A records | PUT | `/api/dns/v1/zones/{domain}` |
| Validate | POST | `/api/dns/v1/zones/{domain}/validate` |
| VM details | GET | `/api/vps/v1/virtual-machines/{id}` |

Auth: `Authorization: Bearer $HOSTINGER_API_KEY`

`dns_apply` body (`overwrite: true` replaces matching name+type only):

```json
{
  "overwrite": true,
  "zone": [
    {
      "name": "@",
      "type": "A",
      "ttl": 300,
      "records": [{ "content": "<VPS_IPV4>" }]
    },
    {
      "name": "www",
      "type": "A",
      "ttl": 300,
      "records": [{ "content": "<VPS_IPV4>" }]
    }
  ]
}
```

Do not call zone reset. Do not purchase a VM from the agent.

Until Caddy (`COMPOSE_PROFILES=tls`) listens on 80/443, the API is on `:8080`.

## Local LM Studio
Developer → Local Server → Start. OpenAI base URL `/v1`. Idle TTL and
parallel slots are LM Studio UI settings, not OpenMontage config.
