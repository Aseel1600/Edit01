# OpenMontage + ComfyUI + Remotion Starter Lane

Goal
- Use OpenMontage as the orchestration and edit system.
- Use local ComfyUI as the custom asset generation subsystem.
- Use Remotion as the final motion-graphics and composition lane.

Recommended pipeline choice
- Default: `hybrid`
- Use `talking-head` only when the job is primarily a speaker edit with captions and light overlays.

System roles
- OpenMontage: pipeline orchestration, artifacts, edit decisions, render reports
- ComfyUI: generated inserts, character motion clips, stylized support visuals
- Remotion: captions, charts, text cards, transitions, mixed-media final assembly
- FFmpeg: utility processing and fallback composition

What is already verified
- `remotion-composer/` exists and has dependencies installed
- `npm run build` succeeds in `/mnt/c/-PROJECT-FOLDERS-/OpenMontage/remotion-composer`
- Existing Remotion output file exists at `remotion-composer/out/video.mp4`
- Existing historical demo video exists at `assets/signal-from-tomorrow-demo.mp4`
- Node.js, npm, and ffmpeg are installed in the current environment

Current recommended working pattern
1. Start each production in `projects/<project-name>/`
2. Put source footage into `projects/<project-name>/assets/video/`
3. Put ComfyUI-generated support images/clips into:
   - `projects/<project-name>/assets/images/`
   - `projects/<project-name>/assets/video/`
4. Use the `hybrid` pipeline when source footage remains the anchor medium.
5. Keep generated inserts secondary until the proof pass is approved.
6. Render preview before final.

ComfyUI handoff rules
- WAN 2.1 I2V: best first lane for character-consistent support inserts
- LTX I2V: proof-of-motion lane when lower-risk testing is needed
- Generate short proof clips first
- Keep prompts focused on one subject and one motion
- Prefer existing safe recipes before scaling quality

Minimal proof-of-progress test
- 1 source clip
- 1 generated support still or short video insert from ComfyUI
- 1 subtitle pass
- 1 Remotion preview render

Expected project structure
```text
projects/comfyui-remotion-proof/
  artifacts/
  assets/
    audio/
    images/
    music/
    video/
  renders/
```

First production recipe
- Pipeline: `hybrid`
- Anchor medium: source footage or screen capture
- Support asset: one ComfyUI-generated insert
- Playbook: `clean-professional` or `flat-motion-graphics`
- Output target: preview first

Next user input needed to execute a real run
- Either:
  1. a source video file path for the anchor footage, or
  2. a clear content brief for a no-footage motion-graphics piece, or
  3. both a source clip and the specific ComfyUI asset idea to insert
