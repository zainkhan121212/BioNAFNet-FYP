"""
novel4_prcm.py — Photoreceptor Response Curve Modeling (PRCM)
=============================================================
Processing Order: Novel #4

Biological Inspiration:
    Rod cells (scotopic vision) have a different response curve than
    cone cells (photopic vision). Rods are more sensitive in low light
    with a lower gamma, while cones handle bright light with higher gamma.
    A learned threshold determines the transition between rod and cone
    dominated processing.

Implementation:
    - Learnable rod_gamma (~0.45) and cone_gamma (~0.95)
    - Sigmoid-based blending controlled by luminance vs threshold
    - Pre-processes the input image before the NAFNet backbone
"""

import torch
import torch.nn as nn

from .luminance_utils import luminance


class PhotoreceptorCurve(nn.Module):
    """Rod/Cone response simulation with learned gamma curves."""
    def __init__(self):
        super().__init__()
        self.rod_gamma = nn.Parameter(torch.tensor([0.45]))
        self.cone_gamma = nn.Parameter(torch.tensor([0.95]))
        self.threshold = nn.Parameter(torch.tensor([0.25]))

    def forward(self, x):
        lum = luminance(x)
        cone_weight = torch.sigmoid((lum - self.threshold) * 12)
        x_rod = torch.pow(x.clamp(1e-5, 1), self.rod_gamma)
        x_cone = torch.pow(x.clamp(1e-5, 1), self.cone_gamma)
        return x_rod * (1 - cone_weight) + x_cone * cone_weight
