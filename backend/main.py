from __future__ import annotations

import io, json
from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse

from models import GenerateParams, PRESETS
from image_utils import to_square, gradient_map, parse_hex_color
from render import render_cover
from PIL import Image

app = FastAPI(title="AstraField Backend", version="0.2.0")

# Dev CORS (tighten allow_origins in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"msg": "AstraField backend OK", "version": app.version}

@app.get("/presets")
def get_presets():
    return {k: v.model_dump() for k, v in PRESETS.items()}

@app.post("/generate")
async def generate(
    request: Request,
    # multipart form (used by browser FormData)
    photo: UploadFile | None = File(None),
    grid_n: int = Form(16),
    dot_step: int = Form(40),
    dot_min: float = Form(1.0),
    dot_max: float = Form(9.0),
    tone_lo: str = Form("#050a10"),
    tone_hi: str = Form("#12cabf"),
    tone_strength: float = Form(0.9),
    seed: int | None = Form(None),
    size: int = Form(1024),
    # geometric toggles
    use_dots: bool = Form(False),
    use_lines: bool = Form(True),
    use_contours: bool = Form(True),
    use_arcs: bool = Form(True),
    use_blocks: bool = Form(True),
    # line params
    line_angle_deg: float = Form(22.0),
    line_density: int = Form(110),
    line_lw: float = Form(1.0),
    line_alpha: float = Form(0.22),
    # contour params
    contour_levels: int = Form(8),
    contour_alpha: float = Form(0.30),
    contour_lw: float = Form(1.1),
    # arc params
    arc_count: int = Form(6),
    arc_rmin: float = Form(0.07),
    arc_rmax: float = Form(0.24),
    arc_jitter: float = Form(0.012),
    arc_lw: float = Form(2.0),
    arc_alpha: float = Form(0.9),
    # blocks
    block_count: int = Form(2),
):
    """
    Supports:
      - multipart/form-data (with optional photo) using form fields above, OR
      - application/json (no file) with the GenerateParams schema.
    """
    # JSON mode (no file) — allow frontend to send JSON body
    if request.headers.get("content-type", "").startswith("application/json"):
        try:
            data = await request.json()
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON body.")
        params = GenerateParams(**data)
        base_img = Image.new("RGB", (params.size, params.size), (10, 20, 30))
    else:
        # multipart mode
        params = GenerateParams(
            grid_n=grid_n, dot_step=dot_step, dot_min=dot_min, dot_max=dot_max,
            tone_lo=tone_lo, tone_hi=tone_hi, tone_strength=tone_strength,
            seed=seed, size=size,
            use_dots=use_dots, use_lines=use_lines, use_contours=use_contours,
            use_arcs=use_arcs, use_blocks=use_blocks,
            line_angle_deg=line_angle_deg, line_density=line_density,
            line_lw=line_lw, line_alpha=line_alpha,
            contour_levels=contour_levels, contour_alpha=contour_alpha, contour_lw=contour_lw,
            arc_count=arc_count, arc_rmin=arc_rmin, arc_rmax=arc_rmax,
            arc_jitter=arc_jitter, arc_lw=arc_lw, arc_alpha=arc_alpha,
            block_count=block_count,
        )
        if photo is not None:
            try:
                img = Image.open(io.BytesIO(await photo.read())).convert("RGB")
            except Exception:
                raise HTTPException(status_code=400, detail="Could not read image upload.")
            base_img = to_square(img, size=params.size)
        else:
            base_img = Image.new("RGB", (params.size, params.size), (10, 20, 30))

    # color grading
    c0 = parse_hex_color(params.tone_lo)
    c1 = parse_hex_color(params.tone_hi)
    graded = gradient_map(np_array := None, c0=c0, c1=c1, strength=params.tone_strength, img=base_img)

    # render
    png_bytes = render_cover(
        graded,
        rng_seed=params.seed,
        grid_n=params.grid_n,
        use_dots=params.use_dots, dot_step=params.dot_step, dot_min=params.dot_min, dot_max=params.dot_max,
        use_lines=params.use_lines, line_angle_deg=params.line_angle_deg,
        line_density=params.line_density, line_lw=params.line_lw, line_alpha=params.line_alpha,
        use_contours=params.use_contours, contour_levels=params.contour_levels,
        contour_alpha=params.contour_alpha, contour_lw=params.contour_lw,
        use_arcs=params.use_arcs, arc_count=params.arc_count, arc_rmin=params.arc_rmin,
        arc_rmax=params.arc_rmax, arc_jitter=params.arc_jitter, arc_lw=params.arc_lw, arc_alpha=params.arc_alpha,
        use_blocks=params.use_blocks, block_count=params.block_count,
    )

    return Response(content=png_bytes, media_type="image/png")

@app.exception_handler(HTTPException)
async def http_exc_handler(_, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
