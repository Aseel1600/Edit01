---
name: repo-audit
description: Produce a factual evidence-based audit of repository identity, Git state, runtime, package manager, tests, and external assumptions before material changes.
---

# repo-audit

Before material changes, determine from the repository:

- identity (name, remotes, visibility if known)
- branch / status / existing user changes
- runtime
- package manager
- build / test commands
- database and migration system
- auth
- storage
- deployment assumptions
- external providers

## Rules

- Output must be factual and evidence-based.
- Cite the file or command that established each fact.
- Mark unknowns as unknown. Do not guess.
- Do not modify files.
