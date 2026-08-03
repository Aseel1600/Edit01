# Deploying the Panda launcher on EC2

Get the launcher running on the box and reachable at `dev.om.mvnoc.ai`, so Dify can call it.
The launcher is the API front door; it drives the OpenMontage agent through the 4 gates.

## Steps (on the EC2 box)
```bash
# 1) clone the fork (permanent path — NOT /tmp)
sudo mkdir -p /opt/panda && sudo chown "$USER" /opt/panda
git clone https://github.com/Philipcyrus/OpenMontage-private.git /opt/panda/OpenMontage-prod
cd /opt/panda/OpenMontage-prod
git checkout panda-video-scaffold

# 2) install (system deps + venv + launcher deps + smoke test)
bash deploy/install.sh

# 3) configure env
nano .env          # set DIFY_TOKEN (long random), DIFY_RUNNER=mock, DIFY_DATA_DIR=/opt/panda/data

# 4) run as a service
sudo cp deploy/panda-launcher.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now panda-launcher
systemctl status panda-launcher --no-pager

# 5) reverse proxy — add deploy/nginx-panda.conf to your nginx (subpath or subdomain),
#    then: sudo nginx -t && sudo systemctl reload nginx

# 6) verify it's live
curl -s -H "X-Dify-Token: <token>" https://dev.om.mvnoc.ai/panda/health
#   -> {"status":"ok","runner":"mock"}
```

## Then connect Dify
Point Dify at the base URL and follow `dify_launcher/DIFY_INTEGRATION.md`:
- subpath  → `BASE_URL = https://dev.om.mvnoc.ai/panda`
- subdomain→ `BASE_URL = https://panda.om.mvnoc.ai`

## Two things to know
1. **Runner:** `DIFY_RUNNER=mock` proves the whole Dify handshake (fakes script/gen, but
   REALLY renders a clean video). Switch to `claude` only after the real `ClaudeCodeRunner`
   + Claude Code + OpenRouter + the Higgsfield MCP are wired on the box.
2. **Storage:** local under `DIFY_DATA_DIR` (default `./data`). Artifacts + job state live
   there; `data/jobs/` is gitignored. Swap for S3 later (Phase 5) with no API change.

## Files here
| file | purpose |
|---|---|
| `install.sh` | system deps + venv + launcher deps + import/render smoke test |
| `panda-launcher.service` | systemd unit (uvicorn on 127.0.0.1:8600) |
| `nginx-panda.conf` | reverse-proxy block (subpath or subdomain) |
| `requirements-launcher.txt` | minimal deps for launcher + render (mock) |
