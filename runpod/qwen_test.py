#!/usr/bin/env python3
"""One-off Qwen-Image comparison test: load once, render (1) a photoreal
real-estate interior (compare vs FLUX) and (2) a full promo card with baked-in
Portuguese text (Qwen's differentiator). A40 48GB -> full bf16, no offload."""
import os, time, torch
os.environ.setdefault("HF_HOME", "/workspace/hf_cache")
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
from diffusers import DiffusionPipeline

t = time.time()
pipe = DiffusionPipeline.from_pretrained("Qwen/Qwen-Image", torch_dtype=torch.bfloat16)
pipe.enable_model_cpu_offload()  # full model ~57GB > 46GB A40; offload keeps the largest single component (~41GB) on GPU
print("loaded in %.1fs" % (time.time() - t), flush=True)
os.makedirs("/workspace/out", exist_ok=True)

def gen(prompt, name, w, h, seed):
    t = time.time()
    img = pipe(prompt=prompt, negative_prompt=" ", width=w, height=h,
               num_inference_steps=40, true_cfg_scale=4.0,
               generator=torch.Generator("cuda").manual_seed(seed)).images[0]
    out = f"/workspace/out/qwen_{name}.png"
    img.save(out)
    print("%s done in %.1fs -> %s" % (name, time.time() - t, out), flush=True)

INTERIOR = ("Real estate listing photograph of a bright modern living room interior, "
            "floor-to-ceiling windows with warm golden afternoon sunlight, minimalist "
            "Scandinavian furniture, light oak wood floor, neutral cozy tones, "
            "professional interior photography, photorealistic, high detail, no text, no people")

CARD = ("A polished 1:1 real estate marketing poster. A photo of a bright modern living "
        "room with large windows fills the frame under a dark navy overlay. Large bold "
        "white headline text reads \"As fotos da sua casa\", and directly below in golden "
        "yellow bold text \"em video que vende\". A solid coral-orange bar across the very "
        "bottom contains dark navy text \"pt.showingreel.com\". Clean minimalist premium "
        "graphic design, crisp perfectly legible sans-serif typography, centered layout.")

gen(INTERIOR, "interior", 1328, 1328, 1)
gen(CARD, "card", 1328, 1328, 7)
print("ALL DONE", flush=True)
