# OmniRoute-Backed Cloud Provider Adapter for OpenMontage

**Status:** plan only — no implementation. Written to satisfy
`docs/HUB-STUDIO-CUTOVER-SPEC.md`'s "Minimum OpenMontage-owned implementation"
item 4: *"Add an OmniRoute-backed provider adapter and make cloud generation
depend on it. Keep Remotion/FFmpeg/HyperFrames local rendering direct."*

---

## Requirement recap (from the cutover spec)

- The Hub must not mount OpenMontage's `.env` or call individual media
  providers directly. Provider selection happens only inside the OpenMontage
  pipeline, after proposal selection.
- "OpenMontage's non-Twilio/non-ElevenLabs AI calls must use the
  already-established OmniRoute routing policy rather than create a second
  provider-key surface." Twilio and ElevenLabs are explicitly carved out and
  keep their current direct-key path (`ELEVENLABS_API_KEY` in `.env`).
- Kie remains an OmniRoute-backed provider and model catalog, including image
  generation — it is not being retired, only re-routed.
- Acceptance evidence requires: "A cloud generation request has an OmniRoute
  trace and no direct OpenMontage provider key in the deployed runner
  environment."

## What was confirmed on this box (2026-08-26)

- OmniRoute is reachable at `http://127.0.0.1:20128`, loopback-only, health at
  `GET /api/monitoring/health` (confirmed `"status":"healthy"`, version
  `3.8.49`).
- It exposes an OpenAI-compatible surface: `GET /v1/models` (catalog, not live
  capability — see gotcha below) and a completions path shaped
  `/v1/providers/{provider_id}/chat/completions` per the documented Hermes
  consumer contract (`/root/.hermes/specs/omniroute/v1/hermes-consumer-contract.json`).
- Credential handling in the established pattern: a bearer token resolved
  **at request time** from Infisical (`HERMES_OMNIROUTE_CONSUMER_API_KEY` under
  `/nodes/livewell`), held in process memory only — never written to a
  persistent env file, never logged, never placed in argv.
- **Gotcha (do not re-trip this):** `/v1/models` reflects OmniRoute's
  *configured* catalog, not live per-provider capability. An adapter must not
  infer "Kie image generation is available" from a model ID appearing in that
  list; it must treat a real dispatch (or a documented, versioned capability
  endpoint if OmniRoute exposes one) as the source of truth, and must handle a
  configured-but-unavailable model as a normal runtime failure, not a bug.
- What is **not yet confirmed** on this box: the exact request/response shape
  OmniRoute uses for *media* (image/video) generation as opposed to chat/text
  completions. The one written contract found (`hermes-consumer-contract.json`)
  documents an `openai_compatible` chat-completions transport used today for
  LLM routing (Kimi, Claude, Codex, DeepSeek, xAI, etc.). Whether Kie's image
  models ride the same `/v1/providers/{provider_id}/chat/completions` shape
  (e.g., as a multimodal/tool-call response) or a distinct OmniRoute route is
  an open question — **the implementer must confirm this against the live
  OmniRoute API and/or OmniRoute's own docs before writing the HTTP layer**,
  not assume either shape. This plan is written so that confirmation is the
  first implementation step, isolated behind one client class.

## Design

### Architecture

```
OpenMontage pipeline agent
    |
    v
image_selector / video_selector / tts_selector  (existing selectors)
    |
    v
omniroute_image / omniroute_video / (omniroute_kie_* as needed)   (new tools)
    |
    v
lib/providers/omniroute_client.py   (new shared client)
    |
    v
OmniRoute  http://127.0.0.1:20128   (loopback, OpenAI-compatible, no direct
                                      provider key held by OpenMontage)
```

Remotion/FFmpeg/HyperFrames composition and local rendering (`hyperframes_compose`,
`video_compose`, `remotion_caption_burn`, etc.) are untouched — they already run
direct/local and the spec explicitly says to keep them that way.

### New files

```
lib/
  providers/
    omniroute_client.py     # shared client: health check, auth, dispatch, error mapping
    omniroute_models.py      # typed request/response dataclasses per confirmed shape
tools/
  graphics/
    omniroute_image.py       # capability="image_generation", provider="omniroute"
  video/
    omniroute_video.py       # capability="video_generation", provider="omniroute"
docs/
  OMNIROUTE-ADAPTER-PLAN.md  # this file
tests/
  contracts/
    test_omniroute_tools.py  # tool-contract tests against a stubbed OmniRoute
```

`lib/providers/__init__.py` already exists (currently empty) — this is where
the shared client lands, following the same "shared client + thin BaseTool
subclasses" split used by `tools/_comfyui/client.py` (see
`docs/comfyui-adapter-plan.md`).

Kie-specific dispatch, if it turns out to need its own request shape distinct
from a generic "omniroute image/video" tool, becomes `tools/graphics/omniroute_kie_image.py`
/ `tools/video/omniroute_kie_video.py` reusing the same shared client — kept as
a fork point rather than assumed up front, since the exact Kie routing shape
through OmniRoute is the open question above.

### Shared client: `lib/providers/omniroute_client.py`

```python
class OmniRouteError(Exception):
    """Raised on a non-2xx OmniRoute response or a health/version mismatch."""

class OmniRouteClient:
    """Thin client for OpenMontage's OmniRoute-backed cloud generation calls."""

    def __init__(self, base_url: str | None = None):
        # Loopback default; never accept a non-loopback override in production
        # config the way the runner's host bind is hardcoded to 127.0.0.1.
        self.base_url = base_url or os.environ.get(
            "OPENMONTAGE_OMNIROUTE_URL", "http://127.0.0.1:20128"
        )

    def _token(self) -> str:
        """Resolve the bearer token at call time. Same pattern as the Hermes
        consumer contract: Infisical read at request time, held in memory
        only, never persisted to .env or logs. No fallback to a static env
        var checked into .env.example."""

    def health(self) -> dict:
        """GET /api/monitoring/health. Raise OmniRouteError unless status is
        'healthy'. Callers (get_status()/dry_run()) use this, not a bare
        socket check, so a degraded-but-listening OmniRoute reports
        DEGRADED/UNAVAILABLE correctly instead of AVAILABLE."""

    def generate_image(self, *, prompt: str, model: str, **params) -> dict:
        """Dispatch one image generation request. Request/response shape is
        the confirmed-first-step above — implemented only after that shape is
        verified live, not guessed."""

    def generate_video(self, *, prompt: str, model: str, **params) -> dict:
        """Same contract as generate_image for video models."""
```

Design choices carried over deliberately from the runner and ComfyUI adapter
precedent:

- **No direct provider key ever held by this client or its tools.** `dependencies`
  on the new `BaseTool` subclasses declare no `env:<PROVIDER>_API_KEY` entries;
  the only environment dependency is whatever names the OmniRoute consumer
  token (resolved via the vault rail, per `AGENTS.md` — "Use Infisical/vault
  rails for secrets; do not create ad-hoc env copies").
- **Loopback-only, matching the runner's own posture.** `runner/__main__.py`
  hardcodes `host="127.0.0.1"`; this client's default `base_url` follows the
  same convention and is not meant to be pointed at a non-loopback address in
  the deployed config.
- **Health is a distinct call from dispatch**, so `get_status()` can report
  `DEGRADED` (OmniRoute up, provider circuit open / model exhausted) versus
  `UNAVAILABLE` (OmniRoute unreachable) versus `AVAILABLE`, the same
  three-state contract every other `BaseTool` already exposes.
- **Errors carry an OmniRoute trace id** (whatever correlation id the response
  includes) into `ToolResult.data`, both so operators can find the call in
  OmniRoute's own logs and so the cutover's acceptance evidence
  ("a cloud generation request has an OmniRoute trace") is satisfiable without
  extra plumbing.

### Tool specifications

#### `omniroute_image` — Image generation

| Field | Value |
|-------|-------|
| capability | `image_generation` |
| provider | `omniroute` |
| runtime | `API` |
| tier | `GENERATE` |
| stability | `EXPERIMENTAL` (until the live request shape is confirmed and one real generation has round-tripped) |
| dependencies | none of the `env:*` kind — only requires OmniRoute reachability + vault-resolved token |
| fallback_tools | existing direct-key tools (`flux_image`, `openai_image`, `kling_official_image`, etc.) stay as-is and as fallback; nothing about them changes in this plan |
| cost | reported from OmniRoute's own response if it returns metered cost; otherwise `estimate_cost()` uses the same per-model cost table `tools/cost_tracker.py` already loads |

#### `omniroute_video` — Video generation

Same shape as above, `capability="video_generation"`.

**`execute()` flow (both tools), matching the existing `BaseTool` contract:**

1. `client.health()` — fail fast with a clear `ToolResult(success=False, ...)`
   if OmniRoute itself is down, rather than letting a raw connection error
   surface.
2. Build the provider-specific request body per the confirmed shape.
3. `client.generate_image(...)` / `client.generate_video(...)`.
4. Download/save the returned artifact into the caller-provided `output_path`
   (same convention every other generation tool in `tools/video/` and
   `tools/graphics/` already follows).
5. Return `ToolResult` with `model`, `cost_usd`, and the OmniRoute trace id in
   `data`.

### Registry and selector integration

No changes needed beyond adding the two files under `tools/graphics/` and
`tools/video/` — `tool_registry.discover()` already walks those packages via
`pkgutil.walk_packages`, and `image_selector`/`video_selector` already pick up
any tool through `registry.get_by_capability(...)`. This mirrors exactly what
`docs/comfyui-adapter-plan.md` did for its own registry/selector section — no
new integration surface is being invented here.

### Configuration

```bash
# .env — OpenMontage-side, no provider key added here
OPENMONTAGE_OMNIROUTE_URL=http://127.0.0.1:20128   # optional; this is the default
```

No `OMNIROUTE_API_KEY`-shaped entry belongs in `.env` or `.env.example`: the
token is vault-resolved at request time, exactly like the Hermes consumer
contract's `HERMES_OMNIROUTE_CONSUMER_API_KEY` binding. If OpenMontage's
process identity needs its own distinct Infisical secret (rather than reusing
the Hermes one), that is a vault-provisioning decision for whoever owns the
Infisical rail on this box, not something this adapter should invent an ad-hoc
copy of.

### What this deliberately does not change

- Twilio and ElevenLabs keep their current direct-key path — the spec
  excludes them by name.
- Kie stays a real provider/model catalog; this plan does not remove or
  duplicate `docs/PROVIDERS.md`'s Kie entry, it only adds the routing layer in
  front of dispatch for calls the cutover spec scopes to OmniRoute.
- Remotion/FFmpeg/HyperFrames local rendering is untouched.
- No other existing direct-key tool (`kling_video`, `fal_elevenlabs_music`,
  `runway_video`, etc.) is modified, deprecated, or rewired by this plan. They
  remain available as fallback tools exactly as they are today.

## Implementation scope (estimate)

| Component | Files | Estimated size |
|-----------|-------|-----------------|
| Shared client | `lib/providers/omniroute_client.py` | ~150 lines |
| Typed request/response models | `lib/providers/omniroute_models.py` | ~60 lines |
| Image tool | `tools/graphics/omniroute_image.py` | ~120 lines |
| Video tool | `tools/video/omniroute_video.py` | ~130 lines |
| Tests (stubbed OmniRoute) | `tests/contracts/test_omniroute_tools.py` | ~150 lines |
| Docs | `docs/OMNIROUTE-ADAPTER-PLAN.md` | this file |

No changes to: `base_tool.py`, `runner/server.py`, any pipeline definition,
Backlot, or any existing direct-key provider tool.

## Open questions to resolve before writing code

1. **Confirm the live media-generation request/response shape against
   OmniRoute itself** (or its docs) before writing `omniroute_client.py`'s
   `generate_image`/`generate_video` bodies — do not assume the chat-completions
   shape carries over to image/video without checking.
2. **Confirm which Infisical secret path/name OpenMontage should read** for its
   own OmniRoute consumer token — reuse `HERMES_OMNIROUTE_CONSUMER_API_KEY`
   under `/nodes/livewell`, or provision a distinct OpenMontage-scoped secret.
   This is a vault-ownership call, not an OpenMontage code decision.
3. **Confirm whether OmniRoute reports metered cost per call** (so
   `estimate_cost()`/`ToolResult.cost_usd` can use the authoritative number)
   or whether OpenMontage's own per-model cost table remains the source of
   truth for budget governance.
4. **EXPERIMENTAL → BETA promotion criteria**: same convention as every other
   tool here — promote once one real generation has round-tripped end-to-end
   and been reviewed, not on code completion alone.
