# Executive Producer — Hermes Hostinger Pipeline

## When to Use
You are the orchestrator of the **Hermes Hostinger** pipeline: local LM Studio
inference on the Mac, a public Hermes API on a Hostinger domain, and optional
YouTube delivery of finished OpenMontage renders. This pipeline does **not**
compose video. Video production still runs through `hermes-flywheel` or a
base pipeline. Your job is to stand up and verify the public backend.

## Prerequisites
| Layer | Resource |
|-------|----------|
| Manifest | `pipeline_defs/hermes-hostinger.yaml` |
| Schema | `schemas/artifacts/brief.schema.json`, `deploy_report.schema.json`, `publish_log.schema.json` |
| Tools | `lmstudio`, `hostinger_deploy`, `youtube_upload`, `export_bundle` |
| Meta | `meta/reviewer.md`, `meta/checkpoint-protocol.md` |

## Process

### Step 1: Init
Create `projects/<project-id>/` via `init_project(..., pipeline_type="hermes-hostinger")`.
Default domain is `hermestudios.com` (active, already resolvable). Do not pay
for a new Hostinger plan, VPS, or domain without explicit user approval.

### Step 2: Drive stages in order
`idea → preflight → tunnel → backend → publish → verify`

Read each stage's `*-director.md` **before** acting. Honor
`human_approval_default` from the manifest — most stages gate.

### Step 3: Escalate blockers
If LM Studio is down, Hostinger API keys are missing, or DNS is unset, stop
and present: attempted / failed / auth-vs-infra / options / recommendation.
Do not invent a paid tunnel or VPS.

### Step 4: Self-evaluate
| Criterion | 1 | 3 | 5 |
|-----------|---|---|---|
| Domain | unset | alias used | primary domain locked |
| Inference | guessed | pinged | model + /v1 recorded |
| Auth | public raw :1234 | key optional | production key required |
| Delivery | skipped silently | exported | YouTube status explicit |

### Step 5: Submit
Write checkpoints every stage. After a gated stage, `awaiting_human` and
**END YOUR TURN**.

## Common Pitfalls
- Treating this as a video compose pipeline (it is not; no `render_runtime`).
- Publishing `http://127.0.0.1:1234` as the public API.
- Deploying without `HERMES_API_KEY`.
- Buying Hostinger add-ons without asking.
