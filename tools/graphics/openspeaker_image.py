"""OpenSpeaker image generation tool (api.ai33.pro Imagen API).

One key fronts many models — gpt-image-2, gemini-3.x, recraft-v4.1,
bytedance-seedream-*, flux-2-pro, krea-2-*, runway-gen4-image, and others.
List what the account can use with GET /v1i/models.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Optional

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)
from tools.openspeaker_client import (
    OpenSpeakerError,
    api_key,
    download,
    poll_task,
    request,
    safe_media_path,
)

DEFAULT_MODEL = "gpt-image-2"

# Reference uploads are restricted to real image types so a path that slips
# through cannot ship arbitrary file contents to the provider.
ALLOWED_REFERENCE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}

# Populated on first use from GET /v1i/models; see OpenSpeakerImage._model_spec.
_MODEL_CACHE: Optional[dict[str, dict[str, Any]]] = None


class OpenSpeakerImage(BaseTool):
    name = "openspeaker_image"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "image_generation"
    provider = "openspeaker"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.ASYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.API

    dependencies = ["requests"]
    install_instructions = (
        "Set the OPENSPEAKER_API_KEY environment variable in .env:\n"
        "  OPENSPEAKER_API_KEY=your_key_here\n"
        "Optionally set OPENSPEAKER_IMAGE_MODEL (default gpt-image-2).\n"
        "List available models with GET https://api.ai33.pro/v1i/models\n"
        "See docs/openspeaker-api.md"
    )
    fallback = None
    fallback_tools = ["flux_image", "openai_image", "recraft_image"]
    agent_skills = ["flux-best-practices", "visual-style"]

    _MODEL_CACHE: Optional[dict[str, dict[str, Any]]] = None

    capabilities = [
        "text_to_image",
        "image_to_image",
        "reference_images",
        "multi_model_routing",
    ]
    supports = {
        "reference_images": True,
        "aspect_ratio_control": True,
        "resolution_control": True,
        "offline": False,
        "batch": True,
    }
    best_for = [
        "one key across many frontier image models (GPT Image, Gemini, Seedream, FLUX, Recraft)",
        "brand and marketing stills where accurate on-image text matters (recraft-v4.1)",
        "reference-image-driven consistency across a scene set",
    ]
    not_good_for = [
        "offline generation",
        "guaranteed-deterministic reruns",
    ]

    input_schema = {
        "type": "object",
        "required": ["prompt"],
        "properties": {
            "prompt": {"type": "string", "description": "Image prompt."},
            "model_id": {
                "type": "string",
                "description": "Model id from GET /v1i/models. Defaults to OPENSPEAKER_IMAGE_MODEL.",
            },
            "model": {"type": "string", "description": "Alias for model_id."},
            "generations_count": {"type": "integer", "default": 1, "minimum": 1, "maximum": 4},
            "aspect_ratio": {"type": "string", "description": "e.g. 16:9, 9:16, 1:1."},
            "resolution": {"type": "string", "description": "e.g. 1K, 2K, 4K (model dependent)."},
            "quality": {"type": "string", "description": "low|medium|high, where the model supports it."},
            "model_parameters": {
                "type": "object",
                "description": "Raw passthrough; merged over aspect_ratio/resolution/quality.",
            },
            "reference_images": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "Local paths uploaded as `assets`. Reference them in the prompt "
                    "as @img1, @img2 — the count must match."
                ),
            },
            "output_path": {"type": "string"},
            "timeout_seconds": {"type": "integer", "default": 600},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=200, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=3, retryable_errors=["rate_limit", "timeout", "server_busy"])
    idempotency_key_fields = ["prompt", "model_id", "aspect_ratio", "resolution"]
    side_effects = ["writes image file(s) to output_path", "calls OpenSpeaker API", "consumes credits"]
    user_visible_verification = [
        "Open the generated image and check composition, on-image text spelling, and brand safety",
    ]

    def get_status(self) -> ToolStatus:
        return ToolStatus.AVAILABLE if api_key() else ToolStatus.UNAVAILABLE

    def get_info(self) -> dict[str, Any]:
        info = super().get_info() if hasattr(super(), "get_info") else {}
        info.update(
            {
                "default_model": self._default_model(),
                "model_discovery": "GET /v1i/models",
                "price_check": "POST /v1i/task/price",
            }
        )
        return info

    @staticmethod
    def _default_model() -> str:
        return (os.environ.get("OPENSPEAKER_IMAGE_MODEL") or "").strip() or DEFAULT_MODEL

    def list_models(self) -> list[dict[str, Any]]:
        """Live model catalogue. Useful for the agent at proposal time."""
        payload = request("GET", "/v1i/models", timeout=30)
        return payload.get("models", [])

    @classmethod
    def _model_spec(cls, model_id: str) -> dict[str, Any]:
        """Return the catalogue entry for a model, cached for the process.

        Model capabilities vary a lot (gemini-3.1-flash-lite-image is 1K-only,
        gpt-image-2 goes to 4K, krea-* take no resolution at all). Fetching the
        spec lets the tool drop parameters a model cannot accept instead of
        failing the whole generation on an HTTP 400.
        """
        if cls._MODEL_CACHE is None:
            try:
                payload = request("GET", "/v1i/models", timeout=30)
                cls._MODEL_CACHE = {
                    m["model_id"]: m for m in payload.get("models", []) if m.get("model_id")
                }
            except OpenSpeakerError:
                cls._MODEL_CACHE = {}
        return cls._MODEL_CACHE.get(model_id, {})

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        # Billed in credits, not USD; actual credit_cost comes back on the task.
        return 0.0

    def _build_model_parameters(
        self, inputs: dict[str, Any], model_id: str
    ) -> tuple[dict[str, Any], list[str]]:
        """Assemble model_parameters, dropping values this model rejects.

        Returns (params, notes) where notes records every adjustment so the
        agent sees what was changed rather than silently getting a different
        image than it asked for.
        """
        params: dict[str, Any] = {}
        notes: list[str] = []
        spec = self._model_spec(model_id)

        aspect = inputs.get("aspect_ratio") or os.environ.get("OPENSPEAKER_IMAGE_ASPECT_RATIO")
        if aspect and str(aspect).strip():
            aspect = str(aspect).strip()
            allowed = spec.get("aspect_ratios")
            if allowed and aspect not in allowed:
                fallback = spec.get("default_aspect_ratio")
                notes.append(
                    f"aspect_ratio {aspect!r} unsupported by {model_id} "
                    f"(allowed: {allowed}); used {fallback!r}"
                )
                aspect = fallback
            if aspect:
                params["aspect_ratio"] = aspect

        resolution = inputs.get("resolution") or os.environ.get("OPENSPEAKER_IMAGE_RESOLUTION")
        if resolution and str(resolution).strip():
            # The API expects "2K"/"4K" uppercase; .env may hold "2k".
            value = str(resolution).strip()
            value = value.upper() if value.lower().endswith("k") else value
            allowed = spec.get("resolutions")
            if allowed is None and spec:
                notes.append(f"{model_id} takes no resolution parameter; dropped {value!r}")
                value = None
            elif allowed and value not in allowed:
                fallback = spec.get("default_resolution") or allowed[-1]
                notes.append(
                    f"resolution {value!r} unsupported by {model_id} "
                    f"(allowed: {allowed}); used {fallback!r}"
                )
                value = fallback
            if value:
                params["resolution"] = value

        quality = inputs.get("quality")
        if quality:
            allowed = spec.get("qualities")
            if allowed and quality not in allowed:
                notes.append(f"quality {quality!r} unsupported by {model_id}; dropped")
            else:
                params["quality"] = quality

        params.update(inputs.get("model_parameters") or {})
        return params, notes

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        open_files: list = []
        try:
            result = self._generate(inputs, open_files)
        except OpenSpeakerError as exc:
            return ToolResult(success=False, error=f"OpenSpeaker image generation failed: {exc}")
        except Exception as exc:  # noqa: BLE001 - surfaced to the agent as a tool error
            return ToolResult(success=False, error=f"OpenSpeaker image generation failed: {exc}")
        finally:
            for handle in open_files:
                try:
                    handle.close()
                except Exception:  # noqa: BLE001 - cleanup must never mask the real error
                    pass
        result.duration_seconds = round(time.time() - start, 2)
        return result

    def _generate(self, inputs: dict[str, Any], open_files: list) -> ToolResult:
        prompt = inputs["prompt"]
        model_id = (inputs.get("model_id") or inputs.get("model") or self._default_model()).strip()
        count = int(inputs.get("generations_count", 1))
        model_parameters, param_notes = self._build_model_parameters(inputs, model_id)

        form: list[tuple[str, Any]] = [
            ("prompt", (None, prompt)),
            ("model_id", (None, model_id)),
            ("generations_count", (None, str(count))),
        ]
        if model_parameters:
            form.append(("model_parameters", (None, json.dumps(model_parameters))))

        # Reference images are read off local disk and uploaded to a third-party
        # API. That makes this the one input in this tool that can exfiltrate
        # file contents, so it is constrained twice: the path must resolve
        # inside the workspace, and it must actually be an image. Without both,
        # a poisoned scene_plan could name ".env" or a private key and ship it.
        references = inputs.get("reference_images") or []
        for ref in references:
            ref_path = safe_media_path(ref, must_exist=True)
            if ref_path.suffix.lower() not in ALLOWED_REFERENCE_SUFFIXES:
                raise OpenSpeakerError(
                    f"reference image must be one of "
                    f"{sorted(ALLOWED_REFERENCE_SUFFIXES)}, got {ref_path.suffix!r}: {ref_path.name}"
                )
            handle = open(ref_path, "rb")
            open_files.append(handle)
            form.append(("assets", (ref_path.name, handle)))

        created = request("POST", "/v1i/task/generate-image", files=form, timeout=120)
        task_id = created.get("task_id")
        if not task_id:
            raise OpenSpeakerError(f"No task_id in create response: {created}")

        task = poll_task(task_id, timeout_seconds=int(inputs.get("timeout_seconds", 600)))
        urls = self._extract_image_urls(task)
        if not urls:
            raise OpenSpeakerError(
                f"Task {task_id} finished without image urls: {task.get('metadata')}"
            )

        output_path = safe_media_path(inputs.get("output_path") or f"openspeaker_image_{task_id}.png")
        written: list[str] = []
        for index, url in enumerate(urls[:count]):
            target = (
                output_path
                if index == 0
                else output_path.with_name(f"{output_path.stem}_{index + 1}{output_path.suffix}")
            )
            download(url, target)
            written.append(str(target))

        return ToolResult(
            success=True,
            data={
                "provider": self.provider,
                "model_id": model_id,
                "model_parameters": model_parameters,
                "parameter_adjustments": param_notes,
                "task_id": task_id,
                "credit_cost": task.get("credit_cost"),
                "generations": len(written),
                "prompt": prompt,
                "output": written[0],
                "outputs": written,
            },
            artifacts=written,
            model=model_id,
        )

    # Observed shape (2026-08): metadata.result_images[] = [{id, width, height,
    # imageUrl, mimeType, previewUrl}]. Note imageUrl is camelCase — the older
    # snake_case spellings are kept as fallbacks in case the API varies.
    _URL_KEYS = ("imageUrl", "image_url", "url", "outputUrl", "output_url")

    @classmethod
    def _extract_image_urls(cls, task: dict[str, Any]) -> list[str]:
        """Pull full-resolution image urls out of the task metadata.

        `previewUrl` is deliberately not used as a primary source — it is a
        downscaled proxy, and silently shipping previews as final assets would
        be a quality regression nobody would notice until render.
        """
        metadata = task.get("metadata") or {}
        candidates: list[str] = []

        for key in ("result_images", "image_urls", "all_image_urls", "images", "urls"):
            value = metadata.get(key)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        candidates.append(item)
                    elif isinstance(item, dict):
                        url = next(
                            (item[k] for k in cls._URL_KEYS if isinstance(item.get(k), str)),
                            None,
                        )
                        if url:
                            candidates.append(url)

        for key in ("image_url", "url", "output_url"):
            value = metadata.get(key)
            if isinstance(value, str):
                candidates.append(value)

        result = metadata.get("imagen_result") or metadata.get("result") or {}
        if isinstance(result, dict):
            for item in result.get("images", []) or []:
                if isinstance(item, dict):
                    url = next(
                        (item[k] for k in cls._URL_KEYS if isinstance(item.get(k), str)), None
                    )
                    if url:
                        candidates.append(url)
                elif isinstance(item, str):
                    candidates.append(item)

        seen: set[str] = set()
        ordered: list[str] = []
        for url in candidates:
            if url not in seen:
                seen.add(url)
                ordered.append(url)
        return ordered
