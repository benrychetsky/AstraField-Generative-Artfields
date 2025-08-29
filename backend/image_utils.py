from __future__ import annotations
from typing import Tuple, Optional
import numpy as np
from PIL import Image, ImageOps, ImageFilter
import matplotlib.colors as mcolors

def to_square(img: Image.Image, size: int = 1024) -> Image.Image:
    img = ImageOps.exif_transpose(img)
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top  = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    return img.resize((size, size), Image.Resampling.LANCZOS)

def parse_hex_color(s: str) -> Tuple[float, float, float]:
    try:
        return mcolors.to_rgb(s)
    except Exception as e:
        raise ValueError(f"Invalid color: {s}") from e

def gradient_map(np_array: Optional[np.ndarray] = None,
                 c0=(0.02, 0.04, 0.06),
                 c1=(0.07, 0.8, 0.75),
                 strength: float = 0.9,
                 img: Optional[Image.Image] = None) -> np.ndarray:
    """
    Accepts either np_array (H,W,3 uint8) or a PIL.Image via `img`.
    Applies duotone-like grade (low->c0, high->c1) blended by `strength`.
    Returns uint8 numpy array.
    """
    if img is not None:
        arr = np.array(img)
    elif np_array is not None:
        arr = np_array
    else:
        raise ValueError("Provide either np_array or img")

    a = arr.astype(np.float32) / 255.0
    l = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2])
    l = np.asarray(Image.fromarray((l * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))) / 255.0
    c0 = np.array(c0, dtype=np.float32)
    c1 = np.array(c1, dtype=np.float32)
    mapped = (1 - l)[..., None] * c0 + l[..., None] * c1
    out = (strength * mapped + (1 - strength) * a)
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)
