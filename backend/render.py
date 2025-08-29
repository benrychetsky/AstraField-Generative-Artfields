from __future__ import annotations
import io
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from PIL import Image, ImageFilter

# ---------- layer helpers ----------
def layer_grid(ax, grid_n=16, alpha=0.08):
    if grid_n > 1:
        for i in range(1, grid_n):
            ax.plot([0,1],[i/grid_n,i/grid_n], lw=1, color=(1,1,1,alpha))
            ax.plot([i/grid_n,i/grid_n],[0,1], lw=1, color=(1,1,1,alpha))

def layer_parallel_lines(ax, angle_deg=18, density=80, lw=1.2, alpha=0.35, color=(0,0,0,1.0)):
    angle = np.deg2rad(angle_deg)
    L = 2.5
    for i in np.linspace(-L, L, max(2, density)):
        x0, y0 = -L, i
        x1, y1 =  L, i
        R = np.array([[np.cos(angle), -np.sin(angle)],
                      [np.sin(angle),  np.cos(angle)]])
        p0 = R @ np.array([x0, y0])
        p1 = R @ np.array([x1, y1])
        ax.plot([p0[0]*0.5+0.5, p1[0]*0.5+0.5],
                [p0[1]*0.5+0.5, p1[1]*0.5+0.5],
                linewidth=lw, alpha=alpha, color=color, solid_capstyle="butt")

def layer_concentric_arcs(ax, cx=0.75, cy=0.12, r_min=0.08, r_max=0.28, count=7, jitter=0.015, lw=2.2, alpha=0.9, color=(1.0,0.25,0.25,1.0)):
    radii = np.linspace(r_min, r_max, count)
    for r in radii:
        t = np.linspace(0.1*np.pi, 0.9*np.pi, 240)
        jr = np.sin(np.linspace(0, 6*np.pi, t.size))*jitter
        x = cx + (r+jr)*np.cos(t)
        y = cy + (r+jr)*np.sin(t)
        ax.plot(x, y, lw=lw, alpha=alpha, color=color)

def layer_blocks(ax, rng, count=2, min_w=0.06, max_w=0.18, min_h=0.12, max_h=0.28, y_lo=0.04, y_hi=0.14, colors=((0,0,0,0.85),(1,1,1,0.75))):
    for _ in range(count):
        w = rng.uniform(min_w, max_w)
        h = rng.uniform(min_h, max_h)
        x = rng.uniform(0.06, 0.36)
        y = rng.uniform(y_lo, y_hi)
        col = colors[rng.integers(0, len(colors))]
        ax.add_patch(Rectangle((x,y), w, h, color=col, linewidth=0))

def layer_isolines(ax, field, levels=10, alpha=0.35, lw=1.1, color="k"):
    H, W = field.shape
    X, Y = np.meshgrid(np.linspace(0, 1, W), np.linspace(0, 1, H))
    cs = ax.contour(
        X, 1 - Y, field,
        levels=levels,
        linewidths=lw,
        colors=color,
        alpha=alpha,
    )
    # Some Matplotlib versions don't expose .collections the same way.
    # We don't actually *need* to touch clip_on; it's True by default.
    try:
        cols = getattr(cs, "collections", None)
        if cols is not None:
            for coll in cols:
                coll.set_clip_on(True)
    except Exception:
        # Safe no-op on versions without .collections
        pass


def make_noise_field(h, w, rng, blur_sigma=2.5):
    base = rng.random((h,w)).astype(np.float32)
    img = Image.fromarray((base*255).astype(np.uint8))
    img = img.filter(ImageFilter.GaussianBlur(blur_sigma))
    arr = np.asarray(img).astype(np.float32)/255.0
    return arr

# ---------- renderer ----------
def render_cover(arr: np.ndarray,
                 rng_seed=None,
                 grid_n=16,
                 use_dots=False, dot_step=40, dot_min=1.0, dot_max=9.0, dot_jitter=0.25,
                 use_lines=True, line_angle_deg=22, line_density=110, line_lw=1.0, line_alpha=0.22,
                 use_contours=True, contour_levels=8, contour_alpha=0.30, contour_lw=1.1,
                 use_arcs=True, arc_count=6, arc_rmin=0.07, arc_rmax=0.24, arc_jitter=0.012, arc_lw=2.0, arc_alpha=0.9,
                 use_blocks=True, block_count=2) -> bytes:

    rng = np.random.default_rng(rng_seed)

    fig = plt.figure(figsize=(6,6), dpi=200)
    ax = plt.axes([0,0,1,1])
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    ax.imshow(arr, extent=[0,1,0,1], origin="lower")

    layer_grid(ax, grid_n=grid_n, alpha=0.08)

    if use_dots:
        luma = (0.2126*arr[...,0] + 0.7152*arr[...,1] + 0.0722*arr[...,2])/255.0
        luma_img = Image.fromarray((luma*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))
        luma = np.asarray(luma_img).astype(np.float32)/255.0
        H, W = luma.shape
        ys = np.arange(dot_step//2, H, dot_step)
        xs = np.arange(dot_step//2, W, dot_step)
        for y in ys:
            for x in xs:
                lum = luma[y, x]
                r = dot_min + (1.0 - lum) * (dot_max - dot_min)
                jx = rng.normal(0, dot_jitter*dot_step)
                jy = rng.normal(0, dot_jitter*dot_step)
                cx = (x + jx)/W; cy = 1 - (y + jy)/H
                ax.add_patch(Circle((cx, cy), radius=r/max(W,H), color=(0,0,0,0.45), linewidth=0))

    if use_lines:
        layer_parallel_lines(ax, angle_deg=line_angle_deg, density=line_density,
                             lw=line_lw, alpha=line_alpha, color=(0,0,0,1.0))

    if use_contours:
        field = make_noise_field(220, 220, rng, blur_sigma=2.5)
        layer_isolines(ax, field, levels=contour_levels, alpha=contour_alpha, lw=contour_lw, color="black")

    if use_arcs:
        layer_concentric_arcs(ax, cx=0.78, cy=0.12, r_min=arc_rmin, r_max=arc_rmax,
                              count=arc_count, jitter=arc_jitter, lw=arc_lw,
                              alpha=arc_alpha, color=(1.0,0.25,0.25,0.92))

    if use_blocks and block_count>0:
        layer_blocks(ax, rng, count=block_count)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=200)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()
