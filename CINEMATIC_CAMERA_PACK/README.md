# CINEMATIC_CAMERA_PACK

Camera-only cinematic motion pack for short-form vertical video
(TikTok / Instagram Reels / YouTube Shorts / Facebook Reels / Snapchat).

## Rule of the pack

**Absolute static-subject rule.** Every video is a frozen photograph:
nothing inside the source image is animated, deformed, morphed or
redesigned. Only a virtual cinema camera moves (eased pan/zoom keyframes
over the still), rendered by `render_cam_pack.py` at the repo root.

## Format (every video)

- Aspect ratio **9:16 vertical**, 1080×1920
- Duration **exactly 10.00 s** (300 frames @ 30 fps)
- H.264 MP4, yuv420p, +faststart

## 9:16 framing

Each source image is mounted complete (zero subject crop) inside an
intentional 9:16 composition: the full original print fitted to frame
width and centered, over a heavily blurred, dimmed copy of itself as
background extension. Camera keyframe ranges are constrained so the
complete subject (person, artwork, typography) stays inside the frame
for every move.

## Slots

This pack is produced one slot per source image. Slot numbering follows
the production order of the 8-image master brief.

### IMAGE_01 — source: collage tile "4." (`source.png` at repo root, NIKA tee)

| File | Camera move |
|------|-------------|
| `IMAGE_01_ORIGINAL.png` | original separated source image |
| `IMAGE_01_CAM_01.mp4` | slow cinematic push-in (zoom 1.02→1.45, centered on the artwork) |
| `IMAGE_01_CAM_02.mp4` | slow pull-back reveal (1.45→1.02) |
| `IMAGE_01_CAM_03.mp4` | subtle left→right dolly at constant depth (z 1.22) |
| `IMAGE_01_CAM_04.mp4` | slow low-angle vertical rise (NIKA typography → sun, z 1.28) |
| `IMAGE_01_CAM_05.mp4` | gentle diagonal dolly (bottom-left → top-right) |
| `IMAGE_01_CAM_06.mp4` | push-in combined with subtle lateral parallax |

## Regenerate

```bash
python3 -m venv .venv && ./.venv/bin/pip install pillow numpy imageio-ffmpeg
./.venv/bin/python render_cam_pack.py source.png CINEMATIC_CAMERA_PACK/IMAGE_01 IMAGE_01
```
