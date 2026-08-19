---
name: project-start
description: Initialize or reconcile project continuity files (AGENTS.md, BRIEF, DECISIONS, HANDOFF) with dry-run default and no silent overwrites. Use when starting a repository, running ark init, or installing missing Agent contracts.
---

# project-start

Generalization of former `studio-start`.

## Behavior

```text
inspect
→ dry-run
→ report planned changes/conflicts
→ explicit apply
→ validate
```

Default is **dry-run**. `--apply` is required to write files.

Create only missing files. Never overwrite conflicts silently.

Status vocabulary:

```text
CREATE     destination missing
UNCHANGED  destination identical to template
CONFLICT   destination exists and differs; left untouched
```

Do not automatically:

- commit
- push
- create a public repository
- change license
- install a CI runner
- deploy
- change remote URL

Do not infer a license.

## Files

From `project/templates/`:

- `AGENTS.md`
- `docs/product/BRIEF.md`
- `docs/decisions/DECISIONS.md`
- `docs/continuity/HANDOFF.md`

## CLI

```bash
ark init .
ark init . --apply
```

## Stop condition

Print planned actions, conflicts, and created files. Exit non-zero if apply was requested and a write failed. Leave existing conflicting files untouched.
