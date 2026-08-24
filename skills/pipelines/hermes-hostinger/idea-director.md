# Idea Director — Hermes Hostinger

## When to Use
Lock the public domain, local inference target, auth model, and whether this
run also uploads to YouTube. No servers are started here.

## Prerequisites
| Layer | Resource |
|-------|----------|
| Schema | `schemas/artifacts/brief.schema.json`, `decision_log.schema.json` |
| Manifest metadata | `primary_domain`, `lm_studio.default_base_url` |

## Process

### Step 1: Domain
Recommend **`hermestudios.com`** (active, already resolvable). Aliases:
`hermestudios.online` (pending hPanel setup), `hermestudios.org` (active),
`hermestudioos.com` (typo domain — do not make it canonical). Record the choice in `decision_log`
(`category: "pipeline_selection"`, subject: "Public Hermes domain").

### Step 2: Inference
Default: LM Studio OpenAI-compatible `http://127.0.0.1:1234/v1`, model
`qwen/qwen3-coder-30b` (or whatever `/v1/models` reports later). This is
**local and free**. Cloud LLM fallbacks cost money — ask first.
Log as `category: "provider_selection"`, subject: "Inference backend".

### Step 3: Auth
Production public API **must** require `HERMES_API_KEY`. LM Studio itself
may have auth off locally; the Hostinger gateway supplies the lock.

### Step 4: YouTube scope
Ask whether this run uploads a render. Default privacy: **unlisted**.
Skip is a valid choice — record it.

This pipeline does **not** pick `render_runtime` or HyperFrames. Video
composition, if any, already happened in another pipeline.

### Step 5: Write the brief
Fill `brief` using the video-brief schema as a delivery brief:
- `title`: Hermes API on the chosen domain
- `hook`: local Qwen / LM Studio, public Hostinger gateway
- `target_platform`: `youtube` if uploading, else `generic`
- `target_duration_seconds`: 1 (schema minimum; this is not a video)
- `key_points`: domain, base URL, auth, YouTube yes/no

### Step 6: Self-evaluate
| Criterion | Question |
|-----------|----------|
| Domain | Is the canonical host explicit? |
| Cost | Did we avoid paid inference/tunnel without approval? |
| Auth | Is production locked behind a key? |

### Step 7: Submit
Checkpoint `idea` as `awaiting_human`. **END YOUR TURN**.

## Common Pitfalls
- Using the misspelled `hermestudioos.com` as the primary host.
- Planning to expose port 1234 on the public internet.
