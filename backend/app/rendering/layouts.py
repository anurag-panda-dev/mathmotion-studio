"""Shared layout helpers: frames, themes, colors, quality tiers.

Pure Python (no Manim import) so the compiler, the worker, and the tests
can all use them. The render subprocess shares this module through the
same package import path.

Frame geometry comes from ``prompts/SCENE_FORMAT_SPEC.md`` section 7.1 and
the pixel resolutions are derived from those frames *exactly*, so pixels
per scene unit are uniform on both axes and every in-frame position is
visible in the rendered video.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.schemas.scene import FRAMES, QUALITIES, QUALITY_FRAME_RATES, RESOLUTIONS

# Palette hex values — identical to SCENE_FORMAT_SPEC.md section 7.2.
PALETTE_HEX: dict[str, str] = {
    "navy": "#061830",
    "violet": "#6A4AEE",
    "ivory": "#F1F3EA",
    "white": "#FFFFFF",
    "black": "#000000",
    "gray": "#8A93A6",
    "red": "#D0402E",
    "green": "#2E9E6B",
    "blue": "#2E6FD0",
    "amber": "#E0A126",
    "teal": "#1F9E9E",
    "pink": "#D0509E",
}

HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")


@dataclass(frozen=True)
class Theme:
    name: str
    background: str
    ink: str
    grid: str


THEMES: dict[str, Theme] = {
    "midnight": Theme("midnight", PALETTE_HEX["navy"], PALETTE_HEX["ivory"], PALETTE_HEX["gray"]),
    "ivory": Theme("ivory", PALETTE_HEX["ivory"], PALETTE_HEX["navy"], PALETTE_HEX["gray"]),
}


def resolve_theme(name: str | None) -> Theme:
    return THEMES.get(name or "midnight", THEMES["midnight"])


def resolve_color(value: str | None, theme: Theme) -> str:
    """Palette name or #RRGGBB -> hex; unknown/absent -> theme ink."""
    if not value:
        return theme.ink
    if value in PALETTE_HEX:
        return PALETTE_HEX[value]
    if HEX_COLOR.match(value):
        return value.upper()
    return theme.ink


@dataclass(frozen=True)
class RenderPlan:
    """Everything the worker needs to invoke Manim for one job."""

    aspect_ratio: str
    quality: str
    frame_rate: int
    resolution: tuple[int, int]
    frame: tuple[float, float, float, float]  # xmin, xmax, ymin, ymax

    @property
    def frame_width(self) -> float:
        return self.frame[1] - self.frame[0]

    @property
    def frame_height(self) -> float:
        return self.frame[3] - self.frame[2]

    def resolution_flag(self) -> str:
        # Manim 0.19.x parses --resolution as "W,H" (comma), not "WxH".
        return f"{self.resolution[0]},{self.resolution[1]}"


def build_render_plan(aspect_ratio: str, quality: str) -> RenderPlan:
    if aspect_ratio not in FRAMES:
        aspect_ratio = "16:9"
    if quality not in QUALITIES:
        quality = "standard"
    resolution = RESOLUTIONS[(aspect_ratio, quality)]
    # Safety: pixel ratio must match the frame ratio (uniform pixels per unit).
    fw = FRAMES[aspect_ratio][1] - FRAMES[aspect_ratio][0]
    fh = FRAMES[aspect_ratio][3] - FRAMES[aspect_ratio][2]
    px_ratio = resolution[0] / resolution[1]
    frame_ratio = fw / fh
    if abs(px_ratio - frame_ratio) > 1e-6:  # pragma: no cover - table is consistent
        height = round(resolution[1])
        width = round(height * frame_ratio)
        resolution = (width, height)
    return RenderPlan(
        aspect_ratio=aspect_ratio,
        quality=quality,
        frame_rate=QUALITY_FRAME_RATES[quality],
        resolution=resolution,
        frame=FRAMES[aspect_ratio],
    )


def nice_step(span: float, target_ticks: int = 7) -> float:
    """A readable axis step for a numeric range of width ``span``."""
    if span <= 0:
        return 1.0
    raw = span / max(1, target_ticks)
    magnitude = 10.0 ** (len(str(int(abs(raw)))) - 1) if raw >= 1 else 0.1
    for multiple in (1.0, 2.0, 2.5, 5.0, 10.0):
        if raw <= multiple * magnitude:
            return multiple * magnitude
    return 10.0 * magnitude


def value_to_x(value: float, vmin: float, vmax: float, frame: tuple[float, float, float, float]) -> float:
    """Map a number-line value onto the horizontal scene axis (padded)."""
    xmin, xmax, _, _ = frame
    pad = 0.6
    lo, hi = xmin + pad, xmax - pad
    if vmax == vmin:
        return (lo + hi) / 2
    return lo + (value - vmin) / (vmax - vmin) * (hi - lo)
