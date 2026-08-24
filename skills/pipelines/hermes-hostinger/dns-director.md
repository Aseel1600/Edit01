# DNS Director — Hermes Hostinger

## When to Use
Point the Hostinger DNS zone for the canonical domain at the VPS that
runs `hermes-api`. This is how the backend becomes reachable as
`https://hermestudios.com`.

## Prerequisites
| Layer | Resource |
|-------|----------|
| Tool | `hostinger_deploy` actions `dns_status`, `dns_apply` |
| Prior | `deploy_report` from backend (compose ready) |
| Domain | Canonical `hermestudios.com` (map `hermestudio.com` → this) |

## Process

### Step 1: Canonicalize
If the brief or user said `hermestudio.com`, rewrite to `hermestudios.com`.
Do not register the shorthand domain.

### Step 2: Read the zone
```
hostinger_deploy.execute({
  "action": "dns_status",
  "domain": "hermestudios.com"
})
```
Record current A/@, A/www, and whether `HOSTINGER_API_KEY` is present.

### Step 3: Resolve IPv4
Need the VPS public IPv4. Sources, in order: `ipv4` input,
`HOSTINGER_VPS_IP`, Hostinger VM details via `HOSTINGER_VM_ID`.
If none: `deploy_report.dns.status = blocked`, explain, **do not buy a VPS**.

### Step 4: Apply A records
When IPv4 and API key exist:
```
hostinger_deploy.execute({
  "action": "dns_apply",
  "domain": "hermestudios.com",
  "ipv4": "<VPS_IPV4>"
})
```
This updates **only** `A @` and `A www`. Leave MX/TXT alone.
Keep Hostinger nameservers.

If the API is missing, give the hPanel path:
Domains → hermestudios.com → DNS → A `@` + A `www` → VPS IPv4.

### Step 5: Self-evaluate
| Criterion | Question |
|-----------|----------|
| Apex | Does A/@ equal the VPS IPv4 (or blocked with a reason)? |
| www | Does A/www match apex? |
| Nameservers | Still Hostinger? |

### Step 6: Submit
Write `deploy_report.dns` and checkpoint `dns` `awaiting_human`.
**END YOUR TURN**.

## Common Pitfalls
- Treating `hermestudio.com` as a live zone (it is not).
- Zone reset (wipes email).
- Moving nameservers to Cloudflare without being asked.
- Claiming the domain is live after local `/health` only.
