# Product brief

Durable product intent. Not a session log.

## Problem

AI coding assistants can write code, but they are not a video production studio. Users need an agent-first pipeline that turns a brief or reference video into a finished render with research, script, assets, edit, composition, quality gates, and cost control.

## Target users

The workstation owner (`suyaleo`) operating a local fork of OpenMontage in Cursor, plus future contributors who follow the same Agent contracts.

## Primary workflow

```text
rehydrate → pick pipeline → research/proposal → script → scene_plan → assets → edit → compose → self-review
```

Human approval gates stay at proposal, script, scene plan, generated assets, and publish.

## Desired final artifact / outcome

A local, Agent-managed checkout of `suyaleo/OpenMontage` that can resume from repository contracts, run OpenMontage pipelines through Cursor, and keep kit continuity without overwriting upstream agent files.

## Scope

- Fork and track `calesthio/OpenMontage` (`upstream`) from `suyaleo/OpenMontage` (`origin`)
- Keep upstream `AGENTS.md` / `AGENT_GUIDE.md` as the OpenMontage operating contract
- Add kit contracts only: BRIEF, DECISIONS, HANDOFF
- Optional later: Cursor adapter install, `make setup`, API keys, first pipeline run

## Non-goals

- Overwriting upstream `AGENTS.md` or `AGENT_GUIDE.md`
- Relicensing away from GNU AGPLv3
- Changing GitHub visibility without an explicit decision
- Running `make setup`, installing GPU extras, or spending cloud API credits without approval
- Treating this checkout as a clean-room original product

## Product constraints

- License is GNU AGPLv3. Network use and distribution require corresponding source.
- Python provides tools and persistence only. The agent is the orchestrator.
- Automate kit procedure, not decisions: no auto push, public-visibility change, license change, deploy, or overwrite.
- Secrets stay in `.env` (from `.env.example`). Do not commit keys.

## Acceptance direction

- Contracts exist and match live Git.
- Upstream OpenMontage instructions remain authoritative for production work.
- Setup and first render happen only after explicit approval.
