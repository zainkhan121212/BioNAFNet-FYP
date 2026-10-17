"""
image_ops.py — Image Processing Utilities
===========================================
Placeholder enhancement functions + augmentation/crop/resize logic.
"""

import random
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


def enhance_image(pil_img: Image.Image, model_id: str) -> Image.Image:
    """Apply a simulated enhancement based on the selected model."""
    img = pil_img.copy().convert("RGB")

    if model_id == "zero_dce":
        img = ImageEnhance.Brightness(img).enhance(1.6)
        img = ImageEnhance.Contrast(img).enhance(1.3)
        img = ImageEnhance.Color(img).enhance(1.2)
    elif model_id == "mirnet":
        img = ImageEnhance.Brightness(img).enhance(1.4)
        img = ImageEnhance.Sharpness(img).enhance(1.5)
        img = ImageEnhance.Contrast(img).enhance(1.2)
    elif model_id == "enlightengan":
        img = ImageEnhance.Brightness(img).enhance(1.8)
        img = ImageEnhance.Color(img).enhance(1.4)
    elif model_id == "retinexnet":
        img = ImageEnhance.Brightness(img).enhance(1.5)
        img = ImageEnhance.Contrast(img).enhance(1.4)
        img = ImageEnhance.Sharpness(img).enhance(1.2)
    elif model_id == "kind":
        img = ImageEnhance.Brightness(img).enhance(1.7)
        img = ImageEnhance.Contrast(img).enhance(1.3)
        img = ImageEnhance.Color(img).enhance(1.1)
        img = ImageEnhance.Sharpness(img).enhance(1.3)
    else:
        img = ImageEnhance.Brightness(img).enhance(1.5)

    return img


def augment_image(pil_img: Image.Image, index: int) -> Image.Image:
    """Generate one augmented variant based on the index."""
    img = pil_img.copy().convert("RGB")
    ops = [
        lambda i: ImageOps.mirror(i),
        lambda i: ImageOps.flip(i),
        lambda i: i.rotate(random.choice([90, 180, 270]), expand=True),
        lambda i: ImageEnhance.Brightness(i).enhance(random.uniform(0.7, 1.4)),
    ]
    op = ops[index % len(ops)]
    return op(img)


def crop_image(pil_img: Image.Image, top: int, bottom: int,
               left: int, right: int) -> Image.Image:
    """Crop by specified pixel amounts from each side."""
    w, h = pil_img.size
    x1 = max(0, left)
    y1 = max(0, top)
    x2 = max(x1 + 1, w - right)
    y2 = max(y1 + 1, h - bottom)
    return pil_img.crop((x1, y1, x2, y2))


def resize_image(pil_img: Image.Image, width: int, height: int) -> Image.Image:
    """Resize to exact dimensions."""
    return pil_img.resize((width, height), Image.Resampling.LANCZOS)
