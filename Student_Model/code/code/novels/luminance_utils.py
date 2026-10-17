"""
luminance_utils.py — Luminance Helper Function
===============================================
Processing Order: Loaded first within novels/ (used by Novel 3, 4, 7)

Computes the luminance (grayscale) channel from an RGB tensor
using standard BT.601 coefficients.
"""


def luminance(x):
    """Compute luminance channel from RGB tensor.

    Args:
        x: Tensor of shape (B, 3, H, W) with RGB channels.

    Returns:
        Tensor of shape (B, 1, H, W) with luminance values.
    """
    return 0.299 * x[:, 0:1] + 0.587 * x[:, 1:2] + 0.114 * x[:, 2:3]
