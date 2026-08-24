# Publish Director — Hermes Hostinger

## When to Use
Package a finished render (if any) and optionally upload it to YouTube.
Always emit a `publish_log`, even when YouTube is skipped.

## Prerequisites
| Layer | Resource |
|-------|----------|
| Tools | `export_bundle` (required), `youtube_upload` (optional) |
| Schema | `schemas/artifacts/publish_log.schema.json` |
| Prior | `deploy_report`; optional `render_report` / video path from another project |

## Process

### Step 1: Export
If a video path exists, run `export_bundle` with title/description/tags
from the brief. Platform label: `youtube` or `local`.

### Step 2: Upload or skip
- Skip: add a `publish_log` entry `status: "draft"` with
  `error: "youtube skipped by brief"` (or similar).
- Upload: `youtube_upload.execute({...})` default privacy **unlisted**.
  Confirm the user owns the channel. Never upload private source footage
  marked confidential.

### Step 3: Domain announcement
You may include `https://<domain>/health` in the YouTube description.
Never include LM Studio loopback URLs, API keys, or tunnel tokens.

### Step 4: Self-evaluate
| Criterion | Question |
|-----------|----------|
| Privacy | Unlisted unless the user asked for public? |
| Secrets | Description free of keys and :1234? |

### Step 5: Submit
Checkpoint `publish` `awaiting_human`. **END YOUR TURN**.

## Common Pitfalls
- Uploading before the user approved the render in the *other* pipeline.
- Using `public` as the silent default.
