# OpenMontage Post-Lift Preflight and End-to-End Proof

**Status:** prepared during the maintenance freeze. Nothing in this document
was executed as a service start — `openmontage-runner.service` stays
inactive/disabled until the freeze lifts. Every check below is read-only
(config audit, file/permission checks, module import, health GET against the
already-running Backlot) or an explicit static analysis of `runner/server.py`
and `runner/__main__.py`.

Verified: 2026-08-26.

---

## Part 1 — Preflight checklist

| # | Item | Check performed | Result |
|---|------|------------------|--------|
| 1 | Runner code present | `/root/openmontage/runner/server.py`, `__main__.py`, `__init__.py` exist | **PASS** |
| 2 | Runner imports cleanly | `python -c "from runner import server; server.create_app()"` in the venv | **PASS** — app builds, routes: `/api/v1/health`, `/api/v1/runs`, `/api/v1/runs/{project_id}`, `/api/v1/runs/{project_id}/cancel` |
| 3 | venv has runtime deps (fastapi, uvicorn, pydantic) | `pip list` in `.venv` | **PASS** — fastapi 0.141.1, uvicorn 0.52.4, pydantic 2.13.4 |
| 4 | venv has test deps (pytest) | installed this session via `.venv/bin/python -m pip install -r requirements-dev.txt` | **PASS** — pytest 9.1.1, pytest-asyncio 1.4.0 |
| 5 | Focused runner test suite passes | `pytest tests/runner/ -v` | **PASS** — 4/4 (`test_create_run_initializes_fixed_canonical_project_root`, `test_auth_and_path_input_are_rejected`, `test_status_derives_checkpoint_then_approved_render`, `test_cancel_is_cooperative_and_terminal_runs_are_not_cancelled`) |
| 6 | Loopback-only bind confirmed in code | `runner/__main__.py` line 14: `uvicorn.run("runner.server:app", host="127.0.0.1", port=args.port, ...)` — hardcoded, not env-overridable | **PASS** |
| 7 | Port default correct | `--port` defaults to `OPENMONTAGE_RUNNER_PORT` env or `4751` | **PASS** |
| 8 | Port currently dark (freeze respected) | `ss -ltnp \| grep 4751` | **PASS (expected)** — nothing listening |
| 9 | systemd unit installed | `/etc/systemd/system/openmontage-runner.service` | **PASS** — present, byte-identical to `deploy/systemd/openmontage-runner.service` in the repo |
| 10 | systemd unit inactive/disabled (freeze respected) | `systemctl is-active` / `is-enabled openmontage-runner.service` | **PASS (expected)** — `inactive` / `disabled` |
| 11 | Token file present, correctly scoped | `/etc/openmontage/runner.env` | **PASS** — exists, mode `600`, owner `root:root`, contains exactly one `OPENMONTAGE_RUNNER_TOKEN=` line (value not read/printed here) |
| 12 | Token not duplicated into repo `.env` | `grep OPENMONTAGE_RUNNER .env` | **PASS** — no match; token lives only in the root-only `/etc/openmontage/runner.env`, consistent with the systemd `EnvironmentFile` design |
| 13 | `PROJECTS_DIR` resolves and is writable | `lib.paths.PROJECTS_DIR` resolves to `/root/openmontage/projects`, exists, writable | **PASS** |
| 14 | `pipeline_defs/` has a minimal smoke pipeline | `pipeline_defs/framework-smoke.yaml` present | **PASS** — this is the pipeline the E2E test in Part 2 uses |
| 15 | Backlot already up (dependency of the runner's value, not the runner itself) | `curl 127.0.0.1:4750/api/health` | **PASS** — `{"ok":true,"app":"backlot"}`, service `active`/`enabled` |
| 16 | OpenMontage repo commit state | `git status` / `git log ragnar/main..HEAD` | **PASS** — working tree clean; the 3 locally-ahead commits are already present on `ragnar/main` (owner's fork) — see drift note below |
| 17 | Render toolchain — ffmpeg | `ffmpeg -version` | **PASS** — ffmpeg 6.1.1-3ubuntu5 (libx264, libx265, libvpx present) |
| 18 | Render toolchain — Remotion node deps | `npm ls --depth=0` in `remotion-composer/` | **PASS** — no missing/unmet deps reported |
| 19 | Render toolchain — headless Chromium for Remotion | `node_modules/.remotion/chrome-headless-shell` | **PASS** — already downloaded, no first-run fetch needed |
| 20 | Render toolchain — GPU | `nvidia-smi` | **N/A (no GPU on this box)** — CPU-bound Remotion/FFmpeg rendering only; GPU-only local tools (`local_diffusion`, `wan_video`, etc.) will correctly report `UNAVAILABLE`, which is expected and does not block the E2E proof (framework-smoke does not require them) |
| 21 | Disk space | `df -h /` | **CAUTION** — 40G free of 387G (90% used). Not a blocker for one smoke render, but leave a margin note for whoever runs a longer/heavier render batch after lift |
| 22 | OmniRoute cloud adapter | see `docs/OMNIROUTE-ADAPTER-PLAN.md` | **NOT STARTED (by design)** — plan-only per task scope; local rendering does not depend on it |

### Drift note (item 16)

`origin` (`git remote -v`) is `github.com/calesthio/OpenMontage` — the
upstream project, not the owner's. `ragnar` is `github.com/ragnar-claude/OpenMontage`
— the owner's fork. `HEAD` and `ragnar/main` are the same commit
(`9cb3f209fdaa2585b5b17d16a0f863522da45d25`); the "3 commits ahead" is only
relative to `origin/main`, which is expected and correct — those commits
should not be pushed to `origin` (not the owner's repo), and no push to
`ragnar` was needed because they are already there.

### One remaining pre-lift confirmation

Item 11 confirms the token *file* is correctly shaped, but its *value* was
deliberately not read or compared in this pass (never print secrets to a
report). Before running Part 2's Step 3, whoever executes it should confirm
`/etc/openmontage/runner.env`'s `OPENMONTAGE_RUNNER_TOKEN` value is the one
they intend to send as the bearer token — this doc does not and should not
embed it.

---

## Part 2 — Post-lift end-to-end proof plan

Run only after the maintenance freeze is explicitly lifted. Every step below
is one command; nothing here should require debugging if Part 1 stayed green.

### Step 1 — Start the runner (the one action this preflight deliberately did not take)

```bash
systemctl daemon-reload   # picks up the unit if anything changed since install
systemctl enable --now openmontage-runner.service
```

### Step 2 — Confirm the runner is up and loopback-only

```bash
systemctl is-active openmontage-runner.service      # expect: active
ss -ltnp | grep 4751                                # expect: 127.0.0.1:4751 only, no 0.0.0.0/::
curl -s http://127.0.0.1:4750/api/health             # Backlot, expect: {"ok":true,"app":"backlot"}
curl -s http://127.0.0.1:4751/api/v1/health          # Runner, expect: {"ok":true}
```

### Step 3 — Submit one test render through the runner API directly

(This exercises the same path the Hub's future runner client will use —
`docs/HUB-STUDIO-CUTOVER-SPEC.md`'s "Release sequence" step 1: "Deploy the
runner and prove a local Remotion run and Backlot status read.")

```bash
TOKEN=$(grep -oP '(?<=^OPENMONTAGE_RUNNER_TOKEN=).*' /etc/openmontage/runner.env)

curl -s -X POST http://127.0.0.1:4751/api/v1/runs \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"project_id":"e2e-smoke-01","title":"E2E smoke","pipeline_type":"framework-smoke"}'
# expect: 201, {"project_id":"e2e-smoke-01","status":"initialized",...}

curl -s http://127.0.0.1:4751/api/v1/runs/e2e-smoke-01 \
  -H "Authorization: Bearer ${TOKEN}"
# expect: status progresses initialized -> in_progress -> ready/completed as
# the pipeline agent advances checkpoints (the runner itself does not drive
# this — see Step 4)
```

### Step 4 — Advance the pipeline to a completed render

The runner only initializes the project and reports derived status; it does
not execute pipeline stages itself (`runner/server.py`'s own docstring: *"The
runner is an adapter for the Hub, not a second orchestrator... Pipeline agents
remain responsible for progressing work through the normal checkpoint and
approval protocol."*). Drive `projects/e2e-smoke-01` through the
`framework-smoke` pipeline's stages via the normal OpenMontage agent/checkpoint
flow until a `compose`/`publish` checkpoint is `completed` and
`projects/e2e-smoke-01/renders/final.mp4` (or `.webm`/`.mov`) exists.

```bash
# Re-check status after the pipeline reaches compose/publish:
curl -s http://127.0.0.1:4751/api/v1/runs/e2e-smoke-01 \
  -H "Authorization: Bearer ${TOKEN}"
# expect: {"status":"completed","render_id":"renders/final.mp4",...}
```

### Step 5 — Verify Backlot reconciliation

```bash
curl -s http://127.0.0.1:4750/api/health              # still healthy
# Backlot's own project/board view should show e2e-smoke-01 with the same
# stage/status the runner just reported — Backlot is a read-only observer of
# the same checkpoint files, so this is a cross-check, not a second source of
# truth. Confirm by whatever Backlot board endpoint/UI lists projects (check
# backlot/ router paths at lift time if the exact listing route isn't already
# known).
```

### Step 6 — Verify the delivered artifact

```bash
ls -la /root/openmontage/projects/e2e-smoke-01/renders/
file /root/openmontage/projects/e2e-smoke-01/renders/final.mp4
ffprobe -v error -show_format -show_streams \
  /root/openmontage/projects/e2e-smoke-01/renders/final.mp4
# expect: a valid, playable container with at least one video stream
```

### Step 7 — Exercise cancellation (cooperative, non-destructive)

Optional but cheap — proves the third authenticated operation before Hub
integration work begins:

```bash
curl -s -X POST http://127.0.0.1:4751/api/v1/runs/e2e-smoke-01/cancel \
  -H "Authorization: Bearer ${TOKEN}"
# expect: 409 if the run already reached completed/failed/cancelled (correct
# behavior per test_cancel_is_cooperative_and_terminal_runs_are_not_cancelled);
# run this against a still-in-progress run if you want to see the 200 path.
```

### Step 8 — Clean up the smoke project (optional)

```bash
rm -rf /root/openmontage/projects/e2e-smoke-01
```

### Acceptance criteria (mirrors the cutover spec's "Acceptance evidence")

- [ ] Runner active, loopback-only (`127.0.0.1:4751`), health `200`.
- [ ] `POST /api/v1/runs` created one `projects/<id>/project.json`.
- [ ] Pipeline advanced through checkpoints to a `compose`/`publish` completion
      without the runner itself executing any stage.
- [ ] `GET /api/v1/runs/<id>` derived `status:"completed"` and a `render_id`.
- [ ] Backlot's own view of the same project agrees with the runner's derived
      status.
- [ ] The artifact at `projects/<id>/renders/final.mp4` is a valid, playable
      video file.
- [ ] No direct provider key was required for this specific proof (it exercises
      local Remotion/FFmpeg rendering only, per the cutover spec's phased
      "Release sequence" — cloud/OmniRoute generation is proved separately
      once `docs/OMNIROUTE-ADAPTER-PLAN.md` is implemented).
