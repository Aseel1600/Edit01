"""Shared helpers for render-based component tests.

Renders real Remotion stills (no JS test runner, no new dependencies) and
measures WCAG contrast from the resulting PNGs with Pillow, which is already a
project dependency.

Every helper is local-only: `npx remotion still` runs against the checked-in
`remotion-composer/` bundle and never touches the network beyond npm's local
cache, so it stays inside the tests/conftest.py socket guard's intent.
"""

from __future__ import annotations

import shutil
import subprocess
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPOSER_DIR = REPO_ROOT / "remotion-composer"
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "theme_contracts"
GOLDEN_DIR = REPO_ROOT / "tests" / "fixtures" / "theme_contracts" / "goldens"

# Frames chosen inside each fixture cut, at 30fps.
FIXTURE_FRAMES = {
    "hero": 45,        # 1.5s - hero_title
    "stat": 105,       # 3.5s - stat_card + section_title overlay
    "comparison": 165,  # 5.5s - comparison (default colours) + stat_reveal overlay
    "kpi": 225,        # 7.5s - kpi_grid (legacy formatting)
}
CAPABILITY_FRAMES = {
    "kpi_exact": 45,       # 1.5s - kpi_grid with decimals/abbreviate
    "cmp_explicit": 105,   # 3.5s - comparison with explicit left/right colours
}


def _npx() -> str | None:
    """Resolve the npx launcher (npx.cmd on Windows)."""
    return shutil.which("npx") or shutil.which("npx.cmd")


def remotion_available() -> bool:
    """True when the Remotion composer can render locally."""
    return (COMPOSER_DIR / "node_modules" / "remotion").exists() and _npx() is not None


def render_still(props_path: Path, frame: int, out_path: Path, timeout: int = 900) -> Path:
    """Render one frame of the Explainer composition to a PNG."""
    npx = _npx()
    if npx is None:
        raise RuntimeError("npx not found on PATH")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        npx, "remotion", "still", "Explainer", str(out_path.resolve()),
        f"--props={props_path.resolve()}", f"--frame={frame}", "--overwrite",
    ]
    proc = subprocess.run(cmd, cwd=COMPOSER_DIR, capture_output=True, text=True, timeout=timeout, shell=False)
    if proc.returncode != 0 or not out_path.exists():
        raise RuntimeError(
            f"remotion still failed (frame {frame}, props {props_path.name}):\n"
            f"{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}"
        )
    return out_path


# --------------------------------------------------------------------------
# Pixel analysis
# --------------------------------------------------------------------------

def _srgb_channel(value: int) -> float:
    c = value / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = (_srgb_channel(v) for v in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    la, lb = relative_luminance(a), relative_luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def crop_box(size: tuple[int, int], box: tuple[float, float, float, float]) -> tuple[int, int, int, int]:
    """Normalised (x0, y0, x1, y1) -> pixel box."""
    w, h = size
    x0, y0, x1, y1 = box
    return (int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h))


def region_contrast(png_path: Path, box: tuple[float, float, float, float]) -> dict:
    """Best text-vs-background contrast inside a normalised region.

    Background is the most common colour in the region; the "ink" is the pixel
    with the greatest contrast against it. For a readable caption/label this is
    the glyph colour; for text rendered in the background colour it collapses
    toward 1.0.
    """
    from PIL import Image

    with Image.open(png_path) as img:
        region = img.convert("RGB").crop(crop_box(img.size, box))
        pixels = list(region.getdata())

    background = Counter(pixels).most_common(1)[0][0]
    best_ratio, best_pixel = 1.0, background
    for pixel, _count in Counter(pixels).most_common(4000):
        ratio = contrast_ratio(pixel, background)
        if ratio > best_ratio:
            best_ratio, best_pixel = ratio, pixel
    return {"ratio": best_ratio, "background": background, "ink": best_pixel, "pixels": len(pixels)}


def ink_extent(png_path: Path, box: tuple[float, float, float, float], min_ratio: float = 2.0) -> int:
    """Horizontal extent (in pixels) of glyph-like pixels inside a region.

    Used to show that a longer formatted number ("31,700 years") occupies more
    horizontal space than an abbreviated one ("31.7K years").
    """
    from PIL import Image

    with Image.open(png_path) as img:
        region = img.convert("RGB").crop(crop_box(img.size, box))
        width, height = region.size
        pixels = region.load()
        background = Counter(region.getdata()).most_common(1)[0][0]
        columns = [
            x for x in range(width)
            if any(contrast_ratio(pixels[x, y], background) >= min_ratio for y in range(0, height, 2))
        ]
    return (max(columns) - min(columns) + 1) if columns else 0


def images_identical(a: Path, b: Path) -> bool:
    return a.read_bytes() == b.read_bytes()
