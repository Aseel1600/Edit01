# Hermes Hostinger — reference

## Domains
| Domain | Role |
|--------|------|
| hermestudios.com | Canonical (active, in use for the deploy) |
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
| `HOSTINGER_API_KEY` | hPanel API token |
| `HOSTINGER_VM_ID` | VPS id for `hostinger/deploy-on-vps` |
| `YOUTUBE_CLIENT_SECRETS_FILE` | OAuth client JSON |
| `YOUTUBE_PRIVACY` | Default `unlisted` |

## Public routes
| Method | Path | Auth |
|--------|------|------|
| GET | `/` | no |
| GET | `/health` | no |
| GET | `/v1/models` | bearer |
| POST | `/v1/chat/completions` | bearer |
| POST | `/api/youtube/upload` | bearer |

## DNS (hermestudios.com)
Point A/AAAA at the Hostinger VPS public IP after Docker is listening on
80/443. Keep Hostinger nameservers unless the user moves DNS.
`hermestudios.online` remains pending setup in hPanel; wire it as an alias
once its DNS is configured.

## Local LM Studio
Developer → Local Server → Start. OpenAI base URL `/v1`. Idle TTL and
parallel slots are LM Studio UI settings, not OpenMontage config.
