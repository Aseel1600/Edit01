# Dify Launcher

The **HTTP service Dify talks to.** The OpenMontage engine is not a service — it's an agent
that runs per job. This launcher starts/resumes agent runs and surfaces the three approval
gates so Dify can show them to the user and collect responses. Storage is **local** (a folder
per job); no S3/Postgres (Phase 5 deferred).

```
Dify ──HTTP──▶ Dify Launcher ──▶ runner ──▶ agent/pipeline ──▶ local artifacts
                    ▲                 │
                    └── awaiting_human at each gate ──┘
```

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| GET  | `/health` | liveness + which runner is active |
| POST | `/jobs` | start a run from `{brief, profile?, options?}` → stops at GATE 1 |
| GET  | `/jobs/{id}` | current `{status, stage, gate, question, artifacts}` |
| POST | `/jobs/{id}/respond` | `{decision: approve\|revise, answer?, stills?}` → resume to next gate |
| GET  | `/jobs/{id}/artifacts/{name}` | download a script / still / final.mp4 |

**Gate sequence** (matches `pipeline_defs/panda-video.yaml`):
`start → approve_script → approve_storyboard → approve_clips → approve_final → done`.
Branding is **not** a gate — it's an on-demand step after `approve_final`.

At the storyboard gate, Dify may pass user-supplied stills:
`POST /jobs/{id}/respond {"decision":"approve","stills":["/path/a.png","/path/b.png"]}`.

At the **clips** gate, every generated shot is reviewed together; revise specific shots:
`POST /jobs/{id}/respond {"decision":"revise","shots":[1,4]}` regenerates only those.

## Runners (env `DIFY_RUNNER`)
- **`mock`** (default) — no LLM, no Higgsfield. Fakes script + storyboard and REALLY renders a
  clean master via the folded `panda_render`. Lets you test the whole Dify handshake locally.
- **`claude`** — the EC2 path (skeleton in `runner.py`): invokes Claude Code headless against
  the engine repo, mirrors the agent's checkpoints into the job store. Wire this on the box
  where `claude` + OpenRouter + the Higgsfield MCP are available.

## Run it
```bash
pip install -r dify_launcher/requirements.txt
# local test (no server, no LLM): full gate flow + a real render
python dify_launcher/test_dify_flow.py
# serve for Dify to call:
DIFY_RUNNER=mock uvicorn dify_launcher.app:app --host 0.0.0.0 --port 8600
```

## Config (env)
- `DIFY_RUNNER` — `mock` (default) | `claude`
- `DIFY_DATA_DIR` — job storage root (default `./data`; `data/jobs/` is gitignored)
- `DIFY_TOKEN` — optional shared secret; if set, callers must send `X-Dify-Token`

## Connecting Dify
Point Dify's HTTP/tool nodes at this service's base URL:
1. **Start** → `POST /jobs` with the brief; show `question` + the `script` artifact.
2. On user approve/revise → `POST /jobs/{id}/respond`; repeat for storyboard, then final.
3. Render the `final` artifact inline; on approve the job is `done`.
4. (Later) a `POST /jobs/{id}/brand` step will apply Panda branding on request (panda_brand).
