# Decisions

Durable approved decisions. Do not repeat Git commit history.

## D-20260820-01 — Fork adoption of OpenMontage

Date: 2026-08-20
Status: active

### Context

The workspace `/Users/macbook/Developer/open-montage` was empty. The user asked to apply `ark start` to https://github.com/calesthio/OpenMontage and then chose Fork after a read-only audit.

### Decision

Fork the public upstream to `suyaleo/OpenMontage` and clone it into this workspace. Keep `origin` as the fork and `upstream` as `calesthio/OpenMontage`. Visibility stays PUBLIC because GitHub inherited it from the public source.

### Alternatives rejected

- Reference-only (no working clone)
- Derivative without a GitHub fork relationship

### Consequences

This is a fork, not an original product. AGPLv3 still applies. Do not change visibility, license, or remotes without an explicit human decision.

## D-20260820-02 — Keep upstream AGENTS.md; add kit contracts only

Date: 2026-08-20
Status: active

### Context

`ark init` dry-run was `SAFE_CREATE: no` because `AGENTS.md` already exists. That file is OpenMontage's pointer to `AGENT_GUIDE.md`, not a kit template.

### Decision

Never overwrite `AGENTS.md`. Create only the missing kit contracts: `docs/product/BRIEF.md`, `docs/decisions/DECISIONS.md`, and `docs/continuity/HANDOFF.md`. For OpenMontage production work, `AGENT_GUIDE.md` remains mandatory.

### Alternatives rejected

- Overwriting `AGENTS.md` with the kit template
- Leaving the checkout unmanaged with no continuity files

### Consequences

Kit rehydrate uses BRIEF / DECISIONS / HANDOFF plus live Git. Pipeline routing still starts from `AGENT_GUIDE.md`.

## D-20260820-03 — Install Cursor adapter beside OpenMontage rules

Date: 2026-08-20
Status: active

### Context

Contracts existed. The user approved installing the kit Cursor adapter. Upstream already had `.cursor/rules/openmontage.mdc` and `.cursor/commands/*`.

### Decision

Install the adapter into this repo. Add kit rules, agents, hooks, and skills. Do not overwrite `openmontage.mdc` or existing commands.

### Alternatives rejected

- Skipping the adapter
- Replacing OpenMontage `.cursor` files

### Consequences

Both stacks coexist. Adapter source of truth remains `~/Developer/agent-rules-kit/adapters/cursor/`. Re-run the installer after kit changes; do not edit generated `.cursor` kit files here.

## D-20260820-04 — Run make setup

Date: 2026-08-20
Status: active

### Context

The user approved `make setup`. System Python was 3.9.6; FFmpeg 9.0.1 and Node v24.19.0 were already present. `uv` was available.

### Decision

Run `make setup` in this checkout. Use `uv` to create `.venv` with CPython 3.10.21. Install `requirements.txt`, `remotion-composer` npm deps, `piper-tts`, warm HyperFrames via npx, and copy `.env.example` to `.env`.

### Alternatives rejected

- `make install-gpu` (not requested; needs NVIDIA GPU)
- Filling API keys
- `npm audit fix` for the Remotion high-severity advisory

### Consequences

Local zero-key path is available. `.env` and `.venv` are gitignored. Do not commit secrets.

## D-20260820-05 — Grok/GPT providers use workstation OAuth, not API keys

Date: 2026-08-20
Status: active

### Context

The user asked to connect Grok and GPT providers with the existing Grok/GPT OAuth connectors so OpenMontage does not need `XAI_API_KEY` or `OPENAI_API_KEY`. Cursor already had `grok-media-mcp` and `gpt-media-mcp` installed and signed in on macOS Keychain.

### Decision

Keep the connectors at the workstation MCP. Do not copy tokens into `.env`. OpenMontage tools read the same Keychain items:

- `grok_image` / `grok_video` → `com.cursor.grok-media-mcp`
- `openai_image` → `com.cursor.gpt-media-mcp` (ChatGPT/Codex image path)

Sora (`sora_video`) and OpenAI TTS (`openai_tts`) stay API-key-only. GPT OAuth does not cover those APIs.

### Alternatives rejected

- Writing OAuth tokens into `.env`
- Treating Codex OAuth as an OpenAI platform API key
- Installing Hermes or Codex as a coding runtime

### Consequences

Grok image/video and GPT Image 2 consume subscription quota, not billed API keys. HTTP 403 means the account lacks entitlement; do not retry. Codex image generation is best-effort.
