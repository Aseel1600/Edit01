"""Compose provider that delegates the branded render to montage-svc.

THE HINGE. Used at the `compose` stage of the panda-video pipeline INSTEAD of upstream's
`video_compose`. It keeps ALL brand craft (panda logo, CJK captions, cards, grade) inside
montage-svc — nothing is ported into upstream `styles/`.

Flow:
  1. POST /media/import   each approved clip + voice/music file to montage-svc
  2. POST /compose        with the manifest (profile bgc/ugc, captions, cards, grade)
  3. poll  /jobs/{id}      until done
  4. return the final mp4 (downloaded to output_path) + provenance

montage-svc performs ZERO generation and holds NO generation keys. This tool only sends it
already-generated assets + layout instructions.

>>> SCAFFOLD <<< The manifest mapping (edit_decisions/asset_manifest -> montage-svc /compose
body) is stubbed with TODOs. Prove the round-trip against a running montage-svc first
(Phase 2), then fill in the real field mapping.

Env:
  MONTAGE_SVC_URL   base url, e.g. http://localhost:8501   (required)
  MONTAGE_SVC_TOKEN shared token sent as X-Panda-Token     (optional but recommended)
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolTier,
)

_POLL_INTERVAL_S = 3.0
_POLL_TIMEOUT_S = 900.0  # montage-svc minterpolate renders can be minutes-long


class MontageSvcCompose(BaseTool):
    name = "montage_svc_compose"
    version = "0.1.0"
    tier = ToolTier.COMPOSE if hasattr(ToolTier, "COMPOSE") else ToolTier.GENERATE  # TODO confirm tier enum
    capability = "video_compose"
    provider = "montage_svc"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.API

    dependencies = ["env:MONTAGE_SVC_URL"]
    install_instructions = (
        "Set MONTAGE_SVC_URL to a reachable montage-svc instance (e.g. http://localhost:8501). "
        "Optionally set MONTAGE_SVC_TOKEN for the X-Panda-Token shared secret. "
        "montage-svc is the render backend (github.com/Philipcyrus/Montage-render-service)."
    )

    capabilities = ["branded_compose"]
    best_for = [
        "final branded render delegated to montage-svc (logo, CJK captions, cards, grade)",
    ]
    not_good_for = ["any generation — montage-svc composes only"]
    fallback_tools = ["video_compose"]
    quality_score = 0.95

    input_schema = {
        "type": "object",
        "required": ["output_path"],
        "properties": {
            "profile": {"type": "string", "enum": ["bgc", "ugc"], "default": "bgc"},
            "clips": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Ordered local paths of approved clips.",
            },
            "audio": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Voice / music / sfx files to mix.",
            },
            "captions": {"type": "array", "description": "Caption entries (text + timing)."},
            "cards": {"type": "array", "description": "Card overlays (intro/step/outro)."},
            "grade": {"type": "string", "description": "Grade preset name (e.g. 'warm')."},
            "output_path": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=512, vram_mb=0, disk_mb=500, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=2, retryable_errors=["timeout", "network"])
    side_effects = ["POSTs assets to montage-svc", "writes final mp4 to output_path"]

    def _headers(self) -> dict[str, str]:
        tok = os.environ.get("MONTAGE_SVC_TOKEN")
        return {"X-Panda-Token": tok} if tok else {}

    def _base_url(self) -> str:
        url = os.environ.get("MONTAGE_SVC_URL")
        if not url:
            raise RuntimeError("MONTAGE_SVC_URL is not set")
        return url.rstrip("/")

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        try:
            import requests
        except Exception as e:  # noqa: BLE001
            return ToolResult(success=False, error=f"requests not available: {e}")

        try:
            base = self._base_url()
            headers = self._headers()

            # 1) import each media file -> montage-svc media_id
            # TODO: real mapping from asset_manifest/edit_decisions to clips + audio lists.
            media_ids: dict[str, str] = {}
            for path in list(inputs.get("clips", [])) + list(inputs.get("audio", [])):
                p = Path(path)
                if not p.is_file():
                    return ToolResult(success=False, error=f"asset not found: {path}")
                with p.open("rb") as fh:
                    r = requests.post(
                        f"{base}/media/import", headers=headers,
                        files={"file": (p.name, fh)}, timeout=180,
                    )
                r.raise_for_status()
                media_ids[str(path)] = r.json().get("media_id")  # TODO confirm response field

            # 2) build the compose manifest
            # TODO: translate captions/cards/grade/profile into montage-svc's /compose schema.
            manifest = {
                "profile": inputs.get("profile", "bgc"),
                "clips": [media_ids[c] for c in inputs.get("clips", [])],
                "audio": [media_ids[a] for a in inputs.get("audio", [])],
                "captions": inputs.get("captions", []),
                "cards": inputs.get("cards", []),
                "grade": inputs.get("grade"),
            }
            r = requests.post(f"{base}/compose", headers=headers, json=manifest, timeout=60)
            r.raise_for_status()
            job_id = r.json().get("job_id")  # TODO confirm field
            if not job_id:
                return ToolResult(success=False, error=f"no job_id from /compose: {r.text[:200]}")

            # 3) poll
            deadline = time.time() + _POLL_TIMEOUT_S
            final_url = None
            while time.time() < deadline:
                jr = requests.get(f"{base}/jobs/{job_id}", headers=headers, timeout=30)
                jr.raise_for_status()
                j = jr.json()
                status = j.get("status")
                if status in ("done", "completed", "succeeded"):   # TODO confirm terminal value
                    final_url = j.get("output_url") or j.get("url")  # TODO confirm field
                    break
                if status in ("failed", "error", "cancelled"):
                    return ToolResult(success=False, error=f"montage-svc job {job_id} {status}: {j}")
                time.sleep(_POLL_INTERVAL_S)
            if not final_url:
                return ToolResult(success=False, error=f"montage-svc job {job_id} timed out")

            # 4) download final
            output_path = Path(inputs["output_path"])
            output_path.parent.mkdir(parents=True, exist_ok=True)
            dl = requests.get(f"{base}{final_url}" if final_url.startswith("/") else final_url,
                              headers=headers, timeout=300)
            dl.raise_for_status()
            output_path.write_bytes(dl.content)
        except Exception as e:  # noqa: BLE001
            return ToolResult(success=False, error=f"montage_svc_compose failed: {e}")

        from tools.video._shared import probe_output

        probed = probe_output(output_path)
        return ToolResult(
            success=True,
            data={
                "provider": "montage_svc",
                "job_id": job_id,
                "profile": inputs.get("profile", "bgc"),
                "output": str(output_path),
                "output_path": str(output_path),
                "format": "mp4",
                **probed,
            },
            artifacts=[str(output_path)],
            duration_seconds=round(time.time() - start, 2),
        )
