#!/usr/bin/env python3
"""Local FLUX.2 [klein] 4B smoke test -- for a 12GB consumer GPU.

Apache 2.0 licensed, not gated, no HF_TOKEN needed. Distilled 4-step model
(guidance_scale=1.0, num_inference_steps=4 are BFL's reference settings) --
noticeably lower fidelity than FLUX.2 [dev], but free and fully local.

Usage:
    python test_flux2_klein_local.py "prompt" output.png [width] [height]

Defaults to 1536x2752 (vertical, matching the existing seeds/vert library and
TQS's primary Shorts format). Pass 2752 1536 explicitly for horizontal
(seeds/lf). Both confirmed clean at this size 2026-07-07 -- no duplication
or warping artifacts despite being just past FLUX.2-klein's stated "~4MP max"
guidance.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.base_tool import _load_dotenv  # noqa: E402

_load_dotenv()

import torch  # noqa: E402
from diffusers import Flux2KleinPipeline  # noqa: E402

MODEL_ID = "black-forest-labs/FLUX.2-klein-4B"


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python test_flux2_klein_local.py <prompt> <output_path> [width] [height]", file=sys.stderr)
        return 1

    prompt = sys.argv[1]
    output_path = Path(sys.argv[2])
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 1536
    height = int(sys.argv[4]) if len(sys.argv) > 4 else 2752
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading {MODEL_ID}...")
    start = time.time()
    pipe = Flux2KleinPipeline.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16)
    pipe.enable_model_cpu_offload()
    print(f"Loaded in {time.time() - start:.1f}s")

    print(f"Generating {width}x{height}: {prompt!r}")
    start = time.time()
    image = pipe(
        prompt=prompt,
        width=width,
        height=height,
        num_inference_steps=4,
        guidance_scale=1.0,
    ).images[0]
    print(f"Generated in {time.time() - start:.1f}s")

    image.save(output_path)
    print(f"Saved to {output_path} ({image.size[0]}x{image.size[1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
