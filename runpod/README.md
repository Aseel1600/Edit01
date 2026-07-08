# Running Wan-14B / HunyuanVideo 1.5 on a rented GPU (RunPod)

Your laptop's 12GB GPU can't fit Wan-14B (it segfaults) and only runs
HunyuanVideo 1.5 with heavy offload tricks. A rented 24GB RTX 4090 clears
both, at roughly $0.34-0.70/hr (see cost breakdown from chat). This directory
is the automated half of that setup — account creation and payment are on
you, everything after is one script.

## 1. One-time manual steps (you do this, not Claude)

1. Sign up at [runpod.io](https://runpod.io) and add a payment method under
   Billing.
2. From the console, **Deploy a Pod**:
   - GPU: **RTX 4090** (24GB) — the recommended tier for Wan-14B/Hunyuan 1.5
   - Template: **RunPod PyTorch 2.4** (or newer 2.x) — comes with CUDA + torch
     preinstalled, so `setup.sh` only needs to layer diffusers on top
   - **Attach a Network Volume** (50-100GB) if you'll render more than once —
     model weights are large (Wan-14B ~28GB, Hunyuan 1.5 several GB per
     variant) and a network volume survives pod restarts, so you don't
     re-download every session. Without one, weights vanish when the pod
     stops and you pay to re-download next time.
   - Enable SSH access (the console gives you a connection command once the
     pod is running)
3. SSH into the pod using the command RunPod shows you.

## 2. Bootstrap the pod (one command)

```bash
bash setup.sh https://github.com/ping-dev-ui/OpenMontage.git fix/hunyuan-1.5-local-video
```

(swap the branch for `main` once this work merges). This installs ffmpeg,
clones the repo, installs the diffusers stack, sets `VIDEO_GEN_LOCAL_ENABLED=true`,
and prints your GPU + VRAM as a sanity check.

Then edit `.env` on the pod to set a real `HF_TOKEN` (from
https://huggingface.co/settings/tokens) — leaving it blank is fine for the
public Wan/Hunyuan repos, but an *empty string* has caused 401s before
(see [[hunyuan-local-video-env]]), so either fill it in for real or delete
the line entirely.

## 3. Render

```bash
cd /workspace/OpenMontage

# Wan 2.1 14B, text-to-video, full 720p
python3 runpod/render.py wan --variant wan2.1-14b \
  --prompt "Cinematic wide shot of a lone fishing boat drifting in fog" \
  --out /workspace/out/boat.mp4

# HunyuanVideo 1.5, image-to-video from a seed still
python3 runpod/render.py hunyuan --variant hunyuan-1.5 --operation image_to_video \
  --prompt "gentle camera push in, subtle fog drift" \
  --ref /workspace/seed.png --out /workspace/out/clip.mp4
```

**If Wan-14B OOMs:** the 24GB RTX 4090 is right at the edge for a 14B model
in bf16 even with offload. Retry the same command with
`--offload-mode sequential` (shuttles submodules to CPU one at a time —
much slower, but fits in less VRAM). If it still OOMs, drop to
`--variant wan2.1-1.3b` for that shot, or step up to an A100 80GB pod instead
(see cost comparison from chat).

## 4. Get your files back

- Small numbers of files: `scp` from your laptop:
  ```bash
  scp -P <pod-ssh-port> root@<pod-ip>:/workspace/out/*.mp4 ./
  ```
  (port + IP are shown in the RunPod SSH connection string)
- Or use the RunPod web console's file browser under your pod's "Connect" tab.

## 5. When you're done

**Stop or terminate the pod from the RunPod console** — you're billed by the
second while it's running, even if idle. If you attached a network volume,
stopping (not terminating) the pod keeps the volume and downloaded model
weights intact for next time at a small storage fee; terminating deletes the
pod but the volume itself persists separately until you delete it too.
