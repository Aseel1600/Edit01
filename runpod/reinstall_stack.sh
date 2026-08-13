#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Reinstall the Wan/Qwen KNOWN-GOOD stack after a RunPod volume resize (or a
# stop->start onto a new host) wipes the container disk. /workspace survives
# (hf_cache, partial downloads, scripts); torch/diffusers/transformers/ffmpeg
# do NOT. Order matters -- three dependency traps documented in prior runs:
#   1) plain torch cu128 can resolve 2.4.x (too old for diffusers-main flash
#      custom_op) -> --upgrade --force-reinstall to get 2.11.0+cu128
#   2) `transformers` unpinned grabs 5.x which breaks diffusers 0.40 -> pin <5
#   3) the torch force-reinstall breaks torchvision -> reinstall it after torch
# ---------------------------------------------------------------------------
set -e
export HF_HOME=/workspace/hf_cache

echo "=== torch 2.11 cu128 ==="
pip install --upgrade --force-reinstall torch --index-url https://download.pytorch.org/whl/cu128
echo "=== torchvision cu128 (after torch) ==="
pip install --force-reinstall torchvision --index-url https://download.pytorch.org/whl/cu128
echo "=== diffusers git main ==="
pip install --upgrade "git+https://github.com/huggingface/diffusers.git"
echo "=== transformers <5 ==="
pip install -U "transformers<5"
echo "=== support libs ==="
pip install -U accelerate sentencepiece safetensors imageio imageio-ffmpeg ftfy "huggingface_hub<1.0" pillow
echo "=== ffmpeg (apt) ==="
apt-get update -y >/dev/null 2>&1 && apt-get install -y ffmpeg >/dev/null 2>&1 || true

echo "=== VERIFY ==="
python - <<'PY'
import torch, diffusers, transformers
print("torch", torch.__version__, "| cuda", torch.cuda.is_available())
print("diffusers", diffusers.__version__, "| transformers", transformers.__version__)
assert transformers.__version__ < "5", "transformers 5.x breaks diffusers 0.40"
from diffusers import DiffusionPipeline
print("import OK")
PY
echo "stack reinstalled OK."
