#!/usr/bin/env python3
"""Quick FLUX.2-dev smoke test on a rented GPU pod.

Not wired into the tools/ framework yet -- this is a standalone script to
confirm the model loads and generates before deciding whether to build a
proper FluxImage tool (mirroring wan_video.py / hunyuan_video.py).

Usage:
    python3 runpod/test_flux2.py "your prompt here" /workspace/out/test.png [model_id]

model_id defaults to the pre-quantized 4-bit variant (diffusers/FLUX.2-dev-bnb-4bit),
which fits a 24GB card. The full black-forest-labs/FLUX.2-dev checkpoint is a 32B
model (up to ~80GB in bf16) and will not fit even with CPU offload.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.base_tool import _load_dotenv  # noqa: E402  (triggers .env loading, sets HF_TOKEN)

_load_dotenv()

import torch  # noqa: E402
from diffusers import Flux2Pipeline, Flux2Transformer2DModel  # noqa: E402
from transformers import Mistral3ForConditionalGeneration  # noqa: E402

DEFAULT_MODEL = "diffusers/FLUX.2-dev-bnb-4bit"


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python3 test_flux2.py <prompt> <output_path> [model_id]", file=sys.stderr)
        return 1

    prompt = sys.argv[1]
    output_path = Path(sys.argv[2])
    model_id = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_MODEL
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading {model_id}...")
    start = time.time()
    # Load the two big quantized sub-models onto CPU explicitly first --
    # Flux2Pipeline.from_pretrained() alone tries to place them on GPU during
    # load (before enable_model_cpu_offload() ever runs), which OOMs a 24GB
    # card. Confirmed on a RunPod RTX 4090 2026-07-07.
    transformer = Flux2Transformer2DModel.from_pretrained(
        model_id, subfolder="transformer", torch_dtype=torch.bfloat16, device_map="cpu"
    )
    text_encoder = Mistral3ForConditionalGeneration.from_pretrained(
        model_id, subfolder="text_encoder", torch_dtype=torch.bfloat16, device_map="cpu"
    )
    pipe = Flux2Pipeline.from_pretrained(
        model_id, transformer=transformer, text_encoder=text_encoder, torch_dtype=torch.bfloat16
    )
    pipe.enable_model_cpu_offload()
    print(f"Loaded in {time.time() - start:.1f}s")

    print(f"Generating: {prompt!r}")
    start = time.time()
    image = pipe(prompt=prompt, num_inference_steps=28, guidance_scale=4.0).images[0]
    print(f"Generated in {time.time() - start:.1f}s")

    image.save(output_path)
    print(f"Saved to {output_path} ({image.size[0]}x{image.size[1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
