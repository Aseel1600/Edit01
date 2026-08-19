---
name: bad-code-triage
description: Reproduce a defect, identify the source, apply the smallest justified repair, add a regression check, and verify. Use when debugging failures or unexpected behavior.
---

# bad-code-triage

```text
symptom
→ reproduce
→ identify source
→ smallest justified repair
→ regression test
→ verify
```

Avoid broad rewrites before reproducing the problem.

Do not edit product code until reproduction evidence exists, unless the user explicitly asked for an immediate guarded fix and the failure is already captured.
