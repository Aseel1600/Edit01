---
name: rehydrate
description: Resume a session by reading AGENTS.md, BRIEF, DECISIONS, HANDOFF, and Git state, then returning a concise resume report before editing.
---

# rehydrate

Read, in order:

1. `AGENTS.md`
2. `docs/product/BRIEF.md`
3. `docs/decisions/DECISIONS.md`
4. `docs/continuity/HANDOFF.md`
5. Git status / log / diff
6. target files that will be modified

Return a concise resume report before editing.

Do not trust previous Agent memory.

## CLI

```bash
ark rehydrate
```
