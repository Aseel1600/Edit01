#!/usr/bin/env python3
"""Robust single-shot Qwen-Image test with explicit error capture.
enable_model_cpu_offload (full model ~57GB > 46GB A40). 1024x1024/30 steps to
keep the VAE-decode memory spike modest. Prints a real traceback on failure."""
import os, time, traceback, torch
os.environ.setdefault("HF_HOME", "/workspace/hf_cache")
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
from diffusers import DiffusionPipeline

print("loading...", flush=True)
t = time.time()
pipe = DiffusionPipeline.from_pretrained("Qwen/Qwen-Image", torch_dtype=torch.bfloat16)
pipe.enable_model_cpu_offload()
print("loaded %.1fs" % (time.time() - t), flush=True)
os.makedirs("/workspace/out", exist_ok=True)

CARD = ("A polished 1:1 real estate marketing poster. A photo of a bright modern living "
        "room with large windows fills the frame under a dark navy overlay. Large bold "
        "white headline text reads \"As fotos da sua casa\", and directly below in golden "
        "yellow bold text \"em video que vende\". A solid coral-orange bar across the very "
        "bottom contains dark navy text \"pt.showingreel.com\". Clean minimalist premium "
        "graphic design, crisp perfectly legible sans-serif typography, centered layout.")
INTERIOR = ("Real estate listing photograph of a bright modern living room interior, "
            "floor-to-ceiling windows with warm golden afternoon sunlight, minimalist "
            "Scandinavian furniture, light oak wood floor, neutral cozy tones, "
            "professional interior photography, photorealistic, high detail, no text, no people")

def gen(prompt, name, seed, steps=30, w=1024, h=1024):
    try:
        t = time.time()
        torch.cuda.reset_peak_memory_stats()
        img = pipe(prompt=prompt, negative_prompt=" ", width=w, height=h,
                   num_inference_steps=steps, true_cfg_scale=4.0,
                   generator=torch.Generator("cuda").manual_seed(seed)).images[0]
        peak = torch.cuda.max_memory_allocated() / 1e9
        print("%s pipeline done %.1fs (peak VRAM %.1fGB)" % (name, time.time() - t, peak), flush=True)
        img.save("/workspace/out/qwen_%s.png" % name)
        print("%s SAVED" % name, flush=True)
    except Exception:
        print("%s FAILED:" % name, flush=True)
        traceback.print_exc()

gen(CARD, "card", 7)
gen(INTERIOR, "interior", 1)
print("ALL DONE", flush=True)
