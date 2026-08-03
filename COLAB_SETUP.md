Colab Free PoC — OpenMontage

Goal

Run a fully free proof-of-concept on Google Colab (no paid APIs or paid endpoints). This uses free/open assets and local Python libraries Colab can install.

What this provides

- A zero-API, zero-paid path that builds a short video from free images (Wikimedia Commons) + free TTS (gTTS) + assembles with moviepy/ffmpeg.
- Optional notes for using local GPU-based model generation if the user wants to run local diffusion models (requires additional model downloads; optional and not required).

Quick start (Colab)

1. Open Google Colab and click File → Upload notebook, then upload `notebooks/colab_free_poc.ipynb` from this repo, or open it in Colab via GitHub (Open in Colab).
2. Runtime → Change runtime type → Hardware accelerator: GPU (recommended but not required for the zero-API path).
3. Run cells in order. The notebook installs needed packages, downloads free images, generates narration with gTTS, and assembles a final MP4 in `/content/output/final.mp4`.
4. Download the produced `final.mp4` from the Colab Files panel or via the notebook link shown after rendering.

Why this is free

- Uses Wikimedia Commons media (public domain / free reuse) for visuals — no API keys required.
- Uses gTTS (Google Translate TTS) for narration — free library with no paid API key required.
- Uses moviepy + ffmpeg (installed via apt) for video assembly — all free and runs on Colab.

Optional: local model generation

- The notebook includes commented cells and notes describing how to swap the image download step for diffusion image generation via `diffusers` if the user provides a HuggingFace token and wants to run local models on GPU. This is optional and not required for the PoC.

Files added

- notebooks/colab_free_poc.ipynb — runnable Colab notebook with step-by-step cells.
- COLAB_SETUP.md — short step-by-step instructions and rationale.

If you want, commit these files and I can also add a minimal example Python script (colab/colab_run.py) to run the same steps non-interactively.
