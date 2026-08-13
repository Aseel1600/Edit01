#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Install Qwen-Image (text-to-image) on a RunPod pod.
# Qwen/Qwen-Image is Apache 2.0 and NOT gated -> no HF token required.
#
# Assumes the pod already has the Wan-2.2 KNOWN-GOOD stack:
#   torch 2.11.0+cu128 / diffusers 0.40.0.dev0 (git main) / transformers 4.57.x
# QwenImagePipeline ships in diffusers>=0.35; the Qwen2.5-VL text encoder needs
# transformers>=4.49 (4.57 is fine). If a fresh pod, run runpod/setup.sh first.
#
# Disk: bf16 weights ~55-60GB. Land them on the PERSISTENT volume, not the
# ~20GB ephemeral container disk. Bump the volume to >=260GB or evict a cached
# video model (Wan-14B ~40GB / Wan2.2-5B 32GB) if `df` shows it's tight.
# ---------------------------------------------------------------------------
set -euo pipefail

export HF_HOME=/workspace/hf_cache
export HF_HUB_DISABLE_XET=1   # Xet fast-download backend is flaky on these pods

echo "=== free space on the persistent volume ==="
df -h /workspace | tail -1

echo "=== verifying the diffusers/transformers/torch stack ==="
python - <<'PY'
import torch, diffusers, transformers
print("torch      ", torch.__version__, "| cuda:", torch.cuda.is_available())
print("diffusers  ", diffusers.__version__)
print("transformers", transformers.__version__)
assert transformers.__version__ < "5", "transformers 5.x breaks diffusers 0.40 (see runpod notes) -- pin <5"
from diffusers import DiffusionPipeline  # QwenImagePipeline resolved by model_index
print("import OK")
PY

echo "=== pre-downloading Qwen/Qwen-Image weights (~55-60GB bf16) ==="
python - <<'PY'
import os
from huggingface_hub import snapshot_download
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
path = snapshot_download(
    "Qwen/Qwen-Image",
    cache_dir=os.path.join(os.environ["HF_HOME"], "hub"),
)
print("downloaded ->", path)
PY

echo "=== done. volume after download ==="
df -h /workspace | tail -1
echo "Next: python runpod/qwen_gen.py \"<prompt>\" out.png --w 1328 --h 1328   (add --offload on a 24GB 4090)"
