"""
Step 3a — prep a raw photo for ASCII conversion.

Usage:
    python scripts/prep_photo.py path/to/source-photo.png

Pipeline:
  1. Remove the background with rembg (isolates the subject).
  2. Boost local contrast with CLAHE so a flat, evenly-lit face gets
     real highlights/shadows (otherwise it converts to a dark blob).
  3. Composite onto pure white so the background maps to the blank
     end of the ASCII ramp (white -> space character).

Output: source-prepped.png (grayscale, ready for make_ascii_svg.py)
"""
import sys
import numpy as np
import cv2
from PIL import Image
from rembg import remove

from config import SOURCE_PHOTO, PREPPED_PHOTO


def prep(src_path: str, out_path: str) -> None:
    with open(src_path, "rb") as f:
        raw = f.read()

    # 1. Remove background -> RGBA with alpha mask around the subject
    cutout = remove(raw)
    img = Image.open(__import__("io").BytesIO(cutout)).convert("RGBA")

    # 2. Composite onto pure white using the alpha channel
    white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, img).convert("RGB")

    # 3. CLAHE contrast boost (operates in LAB space on the L channel)
    arr = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(arr)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    boosted = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

    gray = cv2.cvtColor(boosted, cv2.COLOR_RGB2GRAY)
    Image.fromarray(gray).save(out_path)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else SOURCE_PHOTO
    prep(src, PREPPED_PHOTO)
