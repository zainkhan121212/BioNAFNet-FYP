"""
novel1_rlin.py — Retinal Lateral Inhibition Network (RLIN)
==========================================================
Processing Order: Novel #1

Biological Inspiration:
    Retinal ganglion cells use center-surround antagonism to enhance
    local contrast. The center pathway excites while the surround
    pathway inhibits, creating edge-enhancing differentiation.

Implementation:
    - Center: 1x1 convolution (fine local detail)
    - Surround: 5x5 average pooling + 1x1 conv (broad context)
    - Learnable alpha blends the center-surround difference
"""

import torch
import torch.nn as nn


class LateralInhibition(nn.Module):
    """Center-surround differentiation inspired by retinal ganglion cells."""

    def __init__(self, ch):
        super().__init__()
        self.center = nn.Conv2d(ch, ch, 1, bias=True)
        self.surround = nn.Sequential(
            nn.AvgPool2d(5, stride=1, padding=2),
            nn.Conv2d(ch, ch, 1, bias=True),
        )
        self.alpha = nn.Parameter(torch.ones(1) * 0.3)

    def forward(self, x):
        c = self.center(x)
        s = self.surround(x)
        return x + self.alpha * (c - s)
