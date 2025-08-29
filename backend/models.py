from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field

class GenerateParams(BaseModel):
    # output & grade
    size: int = Field(1024, ge=256, le=4096)
    tone_lo: str = "#050a10"
    tone_hi: str = "#12cabf"
    tone_strength: float = Field(0.9, ge=0.0, le=1.0)
    seed: Optional[int] = None

    # grid
    grid_n: int = Field(16, ge=1, le=64)

    # toggles
    use_dots: bool = False
    use_lines: bool = True
    use_contours: bool = True
    use_arcs: bool = True
    use_blocks: bool = True

    # dots
    dot_step: int = Field(40, ge=8, le=128)
    dot_min: float = Field(1.0, ge=0.0, le=50.0)
    dot_max: float = Field(9.0, ge=0.0, le=50.0)

    # lines
    line_angle_deg: float = 22.0
    line_density: int = Field(110, ge=2, le=400)
    line_lw: float = Field(1.0, ge=0.2, le=8.0)
    line_alpha: float = Field(0.22, ge=0.0, le=1.0)

    # contours
    contour_levels: int = Field(8, ge=2, le=40)
    contour_alpha: float = Field(0.30, ge=0.0, le=1.0)
    contour_lw: float = Field(1.1, ge=0.2, le=6.0)

    # arcs
    arc_count: int = Field(6, ge=1, le=40)
    arc_rmin: float = Field(0.07, ge=0.0, le=0.9)
    arc_rmax: float = Field(0.24, ge=0.0, le=1.0)
    arc_jitter: float = Field(0.012, ge=0.0, le=0.2)
    arc_lw: float = Field(2.0, ge=0.2, le=12.0)
    arc_alpha: float = Field(0.9, ge=0.0, le=1.0)

    # blocks
    block_count: int = Field(2, ge=0, le=10)

# Some presets your UI can load
PRESETS = {
    "default": GenerateParams(),
    "geo-lines": GenerateParams(use_dots=False, use_lines=True, use_contours=False, use_arcs=True, use_blocks=False, line_density=90, line_lw=1.6, arc_count=7),
    "contour-field": GenerateParams(use_lines=False, use_contours=True, contour_levels=12, contour_lw=1.6, use_arcs=False, use_blocks=False),
    "bold-grid": GenerateParams(grid_n=28, line_alpha=0.3, line_density=60),
    "warm-dusk": GenerateParams(tone_lo="#1b0f0a", tone_hi="#f48b45", tone_strength=0.95),
}
