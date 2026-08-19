---
name: checkpoint
description: Update docs/continuity/HANDOFF.md from actual Git and verification state before context compaction, session end, or provider transition.
---

# checkpoint

Update the current handoff from actual repository state.

## Inputs

- current goal
- Git branch / status / diff
- verified work
- decisions
- risks
- exact next actions

## Template

Use `project/templates/docs/continuity/HANDOFF.md`.

## Rules

- concise, current slice only
- no transcripts, secrets, tokens, passwords, or giant logs
- do not guess progress
- write `HANDOFF.md` before context loss or provider switch

The `<!-- ark:git-state -->` block is a checkpoint snapshot (time, branch, HEAD, short status). It is not a declaration of live HEAD. Live `git status` / `git log` / `git diff` take precedence on rehydrate.

## CLI

```bash
ark checkpoint
```
