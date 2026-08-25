# Hub Studio → OpenMontage cutover

**Status:** implementation-ready design; no Hub code has been changed by this
document.  **Owner:** the Hub publisher owns the implementation and release.

## Intent

Replace the existing single-asset, Kie-only Studio generation path with
OpenMontage production runs while preserving the Hub as the authenticated,
manager-only cockpit and the source of record for the user's request history.
OpenMontage owns pipeline execution, artifacts, review state, and rendering.

This is a cutover of the **Generate** workflow, not a deletion of the existing
media library.  Historical `studio_generations` and `generated_audio` records
remain readable during and after the cutover.

## Current boundary (verified 2026-08-25)

| Concern | Existing Hub boundary | Cutover boundary |
| --- | --- | --- |
| UI / auth | `/studio/generate` and `/studio/media`, manager+ | Hub stays the cockpit and auth authority |
| submission | `POST /api/v1/studio/generate` | New OpenMontage-run submission endpoint |
| generation | `routers/studio_generate.py` calls `acall_kie_async()` inline | OpenMontage pipeline runs asynchronously |
| history | `studio_generations`, `generated_audio` | Existing rows remain legacy history; a new run table links to an OpenMontage project |
| assets/renders | Kie result URLs and legacy `/root/livewell-media*` stores | `/root/openmontage/projects/<project-id>/` canonical run artifacts |
| production board | none | Backlot at loopback `127.0.0.1:4750` |

The old implementation is deliberately not removed in the first release:
`/root/dev/app_fastapi/routers/studio_generate.py` and
`/root/dev/app_fastapi/routers/media_studio.py` are still the only callers of
the legacy Kie dispatcher and library.  The historical media directories are
dormant and are not a current runnable engine.

## Target shape

```text
Hub manager UI
  -> Hub API (session/role/audit + durable run record)
  -> OpenMontage runner adapter (local, authenticated service boundary)
  -> OpenMontage project workspace + Backlot
  -> Hub polls/receives normalized run status and serves approved artifact links
```

The Hub must not mount OpenMontage's `.env` or call individual media providers.
Provider selection occurs only inside the OpenMontage pipeline after proposal
selection.  OpenMontage's non-Twilio/non-ElevenLabs AI calls must use the
already-established OmniRoute routing policy rather than create a second
provider-key surface.  This needs a dedicated OpenMontage provider adapter;
do not silently reuse the current local `.env` provider keys in production.

## Minimum Hub-owned implementation

1. Add `openmontage_runs` through the next append-only Hub migration. Required
   columns: `id`, `project_id` (unique), `requested_by`, `pipeline_type`,
   `title`, `brief_json`, `status`, `current_stage`, `backlot_url`,
   `render_url`, `error`, `created_at`, `updated_at`, `completed_at`.
2. Add `POST /api/v1/studio/openmontage/runs` (manager+) which validates a
   pipeline, creates the Hub row, then asks the runner to initialize the
   matching OpenMontage project.  Return `202` with the Hub run id and the
   Backlot project URL; do not perform a video generation inline.
3. Add `GET /api/v1/studio/openmontage/runs/{id}` and a paginated list endpoint.
   They return normalized status only; Hub reads no arbitrary files from the
   OpenMontage filesystem.
4. Add a Hub-owned background reconciler/webhook consumer that ingests a
   narrow runner status payload (`project_id`, stage, status, approved render
   path, error).  It must reject paths outside the configured OpenMontage
   export root.
5. Add `/studio/openmontage` as the new manager-only entry.  It submits a
   brief, shows pipeline/stage status, and links to the project Backlot view.
   Leave `/studio/generate` and `/studio/media` visible as **Legacy Generate**
   and **Legacy Media** until cutover evidence is complete.

## Minimum OpenMontage-owned implementation

1. Keep Backlot loopback-only. It is an observer, not the authorization layer.
2. Add a small runner API/service with exactly three authenticated operations:
   `create_run`, `get_run_status`, and `cancel_run`.  It initializes projects
   using `lib.checkpoint.init_project`; it never accepts an arbitrary output
   directory or shell command.
3. Make pipeline stages resume from checkpoints. A run reaches generation only
   after the normal proposal/approval process; the service cannot bypass those
   rules.
4. Add an OmniRoute-backed provider adapter and make cloud generation depend
   on it. Keep Remotion/FFmpeg/HyperFrames local rendering direct.
5. Export only approved final artifacts through one configured export root and
   return relative artifact identifiers to Hub, never host filesystem paths.

## Exact Hub implementation locations

| Purpose | Owner-scoped target |
| --- | --- |
| routes | `app_fastapi/routers/studio_openmontage.py` (new) and registration in `app_fastapi/main.py` |
| request/response models | `app_fastapi/schemas/openmontage.py` (new) |
| persistence | next `M####` in `app_fastapi/db_migrations.py` |
| runner client | `app_fastapi/services/openmontage/client.py` (new) |
| async reconciliation | `app_fastapi/workers/tasks/openmontage.py` plus `workers/cron.py` |
| UI | `frontend/src/routes/studio/openmontage/+page.svelte` and generated API schema/client |
| navigation | `app_fastapi/nav_manifest.py`; retain legacy links during transition |
| tests | focused FastAPI router/client/worker tests plus page test |

## Release sequence

1. Deploy the runner and prove a local Remotion run and Backlot status read.
2. Deploy Hub read/write run records and the new page with the legacy routes
   unchanged.  Prove create → project initialized → status visible.
3. Enable one non-paid/local pipeline end-to-end, then one OmniRoute-routed
   cloud asset path with explicit user approval.
4. Mark the Kie Generate entry legacy only after production proof.  Do not
   migrate or delete historical rows; add a legacy badge and redirect new
   multi-asset work to OpenMontage.
5. Only after a separate retention/export receipt, archive the dormant legacy
   media stores and remove the Kie-only dispatcher.  That is a later Hub
   publisher task, not an OpenMontage deployment action.

## Acceptance evidence

- Manager-authenticated Hub request creates one `openmontage_runs` row and one
  matching OpenMontage `projects/<project_id>/project.json`.
- Backlot reports the same project and status; a valid completed local render
  is available through the Hub run detail.
- A cloud generation request has an OmniRoute trace and no direct OpenMontage
  provider key in the deployed runner environment.
- Legacy `/studio/generate` history remains readable; no historical media is
  deleted during the release.
