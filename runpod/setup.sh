#!/usr/bin/env bash
# OpenMontage - RunPod GPU pod bootstrap
#
# Run this ONCE inside a freshly started RunPod pod (SSH or the web terminal),
# after selecting a RunPod PyTorch 2.x template (CUDA 12.1+, e.g. "RunPod
# Pytorch 2.4"). It installs the diffusers stack, syncs this repo, and
# verifies CUDA + VRAM so you know before a long render whether Wan-14B will
# fit or whether you should drop to a smaller variant.
#
# Usage (on the pod):
#   bash setup.sh <git-remote-url> [branch]
# Example:
#   bash setup.sh https://github.com/ping-dev-ui/OpenMontage.git fix/hunyuan-1.5-local-video

set -euo pipefail

REPO_URL="${1:-}"
BRANCH="${2:-main}"
WORKDIR="/workspace/OpenMontage"

if [ -z "$REPO_URL" ]; then
  echo "Usage: bash setup.sh <git-remote-url> [branch]" >&2
  exit 1
fi

echo "== System packages =="
apt-get update -qq && apt-get install -y -qq ffmpeg git >/dev/null

echo "== Cloning repo =="
if [ -d "$WORKDIR/.git" ]; then
  git -C "$WORKDIR" fetch origin "$BRANCH"
  git -C "$WORKDIR" checkout "$BRANCH"
  git -C "$WORKDIR" pull
else
  git clone --branch "$BRANCH" "$REPO_URL" "$WORKDIR"
fi
cd "$WORKDIR"

echo "== Python deps =="
pip install -q -r requirements.txt
# RunPod's stock PyTorch templates ship an old torch (e.g. 2.4.0 on
# "runpod-torch-v240") whose torch.library.infer_schema can't parse the
# PEP-604 union annotations (`torch.Tensor | None`) used by diffusers' Wan
# flash-attention backend registration -- fails at import time with
# "Parameter q has unsupported type torch.Tensor". Confirmed fix: upgrade
# torch itself (pinning diffusers down does NOT help, this is a torch bug).
pip install -q --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
pip install -q "diffusers>=0.39.0" transformers accelerate sentencepiece imageio imageio-ffmpeg ftfy
# ftfy: Wan pipelines use it for prompt text-cleaning; without it i2v fails at
# generation with "name 'ftfy' is not defined" (only on the i2v code path, easy to miss).

echo "== Env =="
if [ ! -f .env ]; then
  cp .env.example .env
fi
# VIDEO_GEN_LOCAL_ENABLED must be a real value, not blank -- an empty/blank
# HF_TOKEN line has bitten us before (read as an invalid empty-string token).
# Fill these in by hand after setup runs, or export them before calling this
# script and it will pick them up:
grep -q '^VIDEO_GEN_LOCAL_ENABLED=' .env && \
  sed -i 's/^VIDEO_GEN_LOCAL_ENABLED=.*/VIDEO_GEN_LOCAL_ENABLED=true/' .env || \
  echo 'VIDEO_GEN_LOCAL_ENABLED=true' >> .env

if [ -n "${HF_TOKEN:-}" ]; then
  grep -q '^HF_TOKEN=' .env && sed -i "s|^HF_TOKEN=.*|HF_TOKEN=${HF_TOKEN}|" .env || echo "HF_TOKEN=${HF_TOKEN}" >> .env
fi

# The Hugging Face cache defaults to /root/.cache, which lives on the small
# ~20GB *container* disk (ephemeral) -- NOT the big persistent volume you
# attached at /workspace. Wan-14B alone is ~28GB of weights, so redirect the
# cache or every download fills the container disk and fails partway
# ("Not enough free disk space"). Confirmed on a real pod 2026-07-07.
mkdir -p /workspace/hf_cache
grep -q '^HF_HOME=' .env && sed -i 's|^HF_HOME=.*|HF_HOME=/workspace/hf_cache|' .env || echo 'HF_HOME=/workspace/hf_cache' >> .env

echo "== GPU / VRAM check =="
python3 -c "
import torch
print('CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    props = torch.cuda.get_device_properties(0)
    print('GPU:', props.name)
    print('VRAM: %.1f GB' % (props.total_memory / 1024**3))
    print('bf16 supported:', torch.cuda.is_bf16_supported())
"

echo ""
echo "Setup done. Next:"
echo "  cd $WORKDIR"
echo "  python3 runpod/render.py --help"
