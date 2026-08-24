# Tunnel Director — Hermes Hostinger

## When to Use
Decide how (or whether) the Mac LM Studio server becomes reachable from
the Hostinger backend. Local-only is a first-class outcome.

## Prerequisites
| Layer | Resource |
|-------|----------|
| Prior | `deploy_report` from preflight |
| Template | `services/hermes-api/cloudflared.yml.example` |

## Process

### Step 1: Choose a path
1. **Local-only** (default, free): Hermes API and LM Studio on the same
   Mac. `LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1`. Set
   `tunnel.local_only: true`.
2. **Named Cloudflare Tunnel** (free): `cloudflared` on the Mac points a
   hostname at `http://127.0.0.1:1234`. The VPS uses that HTTPS URL.
   Never skip the Hermes API auth layer.
3. **Paid ngrok / extra VPS**: **ask first**.

### Step 2: Hard rules
- Do not port-forward raw `:1234` to `0.0.0.0`.
- Do not put the LM Studio URL on the public landing page.
- Public clients talk only to `https://<domain>/v1/*` with a bearer key.

### Step 3: Update deploy_report.tunnel
Set `provider`, `public_url` (or omit), `status`, `local_only`.

### Step 4: Self-evaluate
| Criterion | Question |
|-----------|----------|
| Exposure | Is :1234 still loopback-only? |
| HTTPS | Is any public URL TLS? |

### Step 5: Submit
Checkpoint `tunnel` `awaiting_human`. **END YOUR TURN**.

## Common Pitfalls
- Advertising the tunnel URL as the product API (the Hostinger app is).
- Starting a paid tunnel without permission.
