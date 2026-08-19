---
name: verify
description: Run only the repository-relevant lint, typecheck, test, and build checks and report PASS/WARN/FAIL/NOT RUN/NOT APPLICABLE with real evidence.
---

# verify

Run only the checks relevant to the repository and change.

Do not fabricate command names.

Discover them from:

- package scripts
- build files
- CI
- README
- AGENTS.md
- existing test configuration

## Status vocabulary

```text
PASS
WARN
FAIL
NOT RUN
NOT APPLICABLE
```

Skipped layers must not be represented as passed.

## CLI

```bash
ark verify
```
