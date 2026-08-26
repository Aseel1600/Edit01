# OpenMontage runner deployment

The runner is a loopback-only bridge for the Hub. It does not expose Backlot
and it does not start, shell out to, or otherwise bypass the OpenMontage
pipeline/approval protocol.

Install the unit and its root-readable token file:

```bash
install -d -m 0700 /etc/openmontage
install -m 0600 /dev/null /etc/openmontage/runner.env
# Add exactly: OPENMONTAGE_RUNNER_TOKEN=<long random value>
install -m 0644 deploy/systemd/openmontage-runner.service /etc/systemd/system/openmontage-runner.service
systemctl daemon-reload
systemctl enable --now openmontage-runner.service
```

The Hub runner client sends that value as `Authorization: Bearer …` over its
local service boundary. Do not put it in the Hub repository, browser code, or
OpenMontage project directories. Confirm the listener stays local with
`ss -ltnp | grep 4751`; the expected bind is `127.0.0.1:4751`.

The three authenticated operations are:

- `POST /api/v1/runs` — initialize one fixed-root project workspace.
- `GET /api/v1/runs/{project_id}` — derive checkpoint/render status.
- `POST /api/v1/runs/{project_id}/cancel` — record a cooperative cancellation
  request; it never kills a process or invokes a shell.

`GET /api/v1/health` is intentionally unauthenticated only for local service
supervision; it exposes no run data.
