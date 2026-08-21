# Verify Director — Hermes Hostinger

## When to Use
Prove the public (or local) Hermes API is up, TLS is sane, and chat
completions are not open to the world.

## Prerequisites
| Layer | Resource |
|-------|----------|
| Tools | `hostinger_deploy` action `health_public`, `lmstudio` |
| Prior | `deploy_report`, `publish_log` |

## Process

### Step 1: Health
```
hostinger_deploy.execute({
  "action": "health_public",
  "url": "https://<domain>/health"
})
```
For local-only, hit `http://127.0.0.1:8080/health`. Map `hermestudio.com`
to `https://hermestudios.com`.

### Step 2: Auth probe
POST `/v1/chat/completions` **without** a bearer token. Production must
return 401. If it returns 200, that is a **critical** finding — do not
mark `healthy`.

### Step 3: Optional LM Studio
If the API is on the same machine, `lmstudio` health should still pass.

### Step 4: Write final deploy_report
`status: healthy` only if health 200 **and** unauthenticated chat is
rejected (or local-only was explicit in the brief). Otherwise `degraded`
or `blocked`.

### Step 5: Self-evaluate
| Criterion | Question |
|-----------|----------|
| Public health | /health JSON includes `ok: true`? |
| Lock | Unauthenticated /v1 rejected? |

### Step 6: Submit
Checkpoint `verify` `awaiting_human`. Present the public URL. **END YOUR TURN**.

## Common Pitfalls
- Calling local /health and claiming the Hostinger domain is live.
- Skipping the unauthenticated chat probe.
