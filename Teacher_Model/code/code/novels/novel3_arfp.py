"""
novel3_arfp.py — Adaptive Receptive Field Pooling (ARFP)
========================================================
Processing Order: Novel #3

Biological Inspiration:
    In the human retina, rod cells (active in darkness) have larger
    receptive fields than cone cells (active in brightness). The visual
    system dynamically adjusts its spatial resolution based on ambient
    light levels.

Implementation:
    - Three parallel depthwise convolutions: 3x3, 5x5, 7x7
    - A luminance-driven gate network produces soft attention weights
    - Dark regions favor the large (7x7) kernel, bright regions favor small (3x3)
"""

import torch.nn as nn
import torch.nn.functional as F


class AdaptiveReceptiveField(nn.Module):
    """Luminance-dependent receptive field (larger in dark, smaller in bright)."""

    def __init__(self, ch):
        super().__init__()
        self.small = nn.Conv2d(ch, ch, 3, padding=1, groups=ch, bias=True)
        self.medium = nn.Conv2d(ch, ch, 5, padding=2, groups=ch, bias=True)
        self.large = nn.Conv2d(ch, ch, 7, padding=3, groups=ch, bias=True)
        self.gate = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1), nn.PReLU(16),
            nn.Conv2d(16, 3, 1), nn.Softmax(dim=1),
        )

    def forward(self, x, lum_map):
        lum = F.interpolate(lum_map, size=x.shape[-2:], mode="bilinear", align_corners=False)
        weights = self.gate(lum)
        s = self.small(x)
        m = self.medium(x)
        l = self.large(x)
        return weights[:, 0:1] * s + weights[:, 1:2] * m + weights[:, 2:3] * l
