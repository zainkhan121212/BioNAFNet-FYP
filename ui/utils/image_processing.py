"""
image_processing.py — Image Enhancement Functions
===================================================
Extracted enhancement algorithms for each model.
"""

from PIL import Image, ImageEnhance, ImageFilter


def apply_matrix_enhancement(img: Image.Image) -> Image.Image:
    """Matrix-format enhancement — brightness, contrast, sharpness boost."""
    if img.mode != "RGB":
        img = img.convert("RGB")
    img = ImageEnhance.Brightness(img).enhance(1.2)
    img = ImageEnhance.Contrast(img).enhance(1.3)
    img = ImageEnhance.Sharpness(img).enhance(1.5)
    return img


def apply_zero_dce(img: Image.Image) -> Image.Image:
    """Simulated Zero-DCE enhancement."""
    if img.mode != "RGB":
        img = img.convert("RGB")
    img = ImageEnhance.Brightness(img).enhance(1.4)
    img = ImageEnhance.Contrast(img).enhance(1.2)
    r, g, b = img.split()
    r = r.point(lambda i: min(255, int(i * 1.1)))
    return Image.merge("RGB", (r, g, b))


def apply_r1_model(img: Image.Image) -> Image.Image:
    """R1 model enhancement — sharpness-heavy."""
    if img.mode != "RGB":
        img = img.convert("RGB")
    img = ImageEnhance.Sharpness(img).enhance(2.0)
    img = ImageEnhance.Contrast(img).enhance(1.4)
    img = ImageEnhance.Color(img).enhance(1.2)
    return img


def apply_default_enhancement(img: Image.Image) -> Image.Image:
    """Default mild enhancement."""
    if img.mode != "RGB":
        img = img.convert("RGB")
    img = ImageEnhance.Brightness(img).enhance(1.15)
    img = ImageEnhance.Contrast(img).enhance(1.2)
    return img


MODELS = {
    "A": ("Matrix Format",   apply_matrix_enhancement),
    "B": ("Zero DCE",        apply_zero_dce),
    "C": ("R1 Model",        apply_r1_model),
    "D": ("Deep Retinex",    apply_default_enhancement),
    "E": ("EnlightenGAN",    apply_default_enhancement),
    "F": ("SCI Model",       apply_default_enhancement),
    "G": ("URetinex-Net",    apply_default_enhancement),
}
