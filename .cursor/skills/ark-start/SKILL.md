---
name: ark-start
description: Starts Agent-managed work in the current workspace using agent-rules-kit without opening the kit repo. Use when the user starts work, creates a new project, applies the kit, clones a GitHub URL, wraps up, or says 작업 시작해 / 새 프로젝트로 시작해 / 가져와 / 여기까지 마무리해.
---

# ark-start

Workstation entry for any Cursor workspace. Do not open `~/Developer/agent-rules-kit` just to apply the kit.

## Kit location

```text
KIT=$HOME/Developer/agent-rules-kit
ARK=ark   # if missing: $KIT/bin/ark
```

Stay in the current workspace cwd.

## On work start

1. Run `$ARK` (same as `ark start`) in the current directory.
2. Follow the printed mode:

| Mode | Action |
|---|---|
| managed | Rehydrate from AGENTS / BRIEF / DECISIONS / HANDOFF + live Git. Skip doctor. |
| unmanaged | Init is dry-run only. Never `--apply` conflicts. If `SAFE_CREATE: yes`, ask once. |
| empty | Ask once before `git init` and contract creation. |

3. After contracts exist in **this** repo, dry-run then ask once to install the Cursor adapter here:

```bash
"$KIT/adapters/cursor/install/install.sh" . --apply
```

4. Continue work in this workspace. Do not hop back to the kit.

## External GitHub URL

Read-only audit first (license, scripts, submodules, install). Do not clone extras, install dependencies, or execute untrusted files until the user chooses Reference / Fork / Derivative.

## Wrap-up

Verify in this repo, update HANDOFF, then `ark checkpoint`. Automate procedure, not decisions (no auto push, public, license, deploy, or overwrite).
