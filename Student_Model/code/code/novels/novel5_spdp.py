"""
novel5_spdp.py — Scotopic-Photopic Dual Pathway (SPDP)
======================================================
Processing Order: Novel #5

Biological Inspiration:
    The human visual system has two parallel pathways:
    - Scotopic (rod) pathway: processes luminance only (grayscale)
    - Photopic (cone) pathway: processes chrominance (color)
    These pathways are processed independently and then fused.

Implementation:
    - RGB is converted to YUV color space
    - Y (luminance) goes through scotopic conv layers
    - U,V (chrominance) go through photopic conv layers
    - Features are concatenated and fused back to RGB residual
"""

import torch
import torch.nn as nn


class DualPathway(nn.Module):
    """Separate luminance (rods) and color (cones) processing."""
    def __init__(self, ch=32):
        super().__init__()
        self.scotopic = nn.Sequential(
            nn.Conv2d(1, ch, 3, padding=1), nn.PReLU(ch),
            nn.Conv2d(ch, ch, 3, padding=1), nn.PReLU(ch),
        )
        self.photopic = nn.Sequential(
            nn.Conv2d(2, ch, 3, padding=1), nn.PReLU(ch),
            nn.Conv2d(ch, ch, 3, padding=1), nn.PReLU(ch),
        )
        self.fuse = nn.Sequential(
            nn.Conv2d(ch * 2, ch, 1), nn.PReLU(ch),
            nn.Conv2d(ch, 3, 1), nn.Tanh(),
        )

    def forward(self, x):
        y, u, v = self.rgb_to_yuv(x)
        lum_feat = self.scotopic(y)
        col_feat = self.photopic(torch.cat([u, v], dim=1))
        combined = torch.cat([lum_feat, col_feat], dim=1)
        residual = self.fuse(combined) * 0.2
        return x + residual

    def rgb_to_yuv(self, rgb):
        r, g, b = rgb[:, 0:1], rgb[:, 1:2], rgb[:, 2:3]
        y = 0.299 * r + 0.587 * g + 0.114 * b
        u = -0.147 * r - 0.289 * g + 0.436 * b
        v = 0.615 * r - 0.515 * g - 0.100 * b
        return y, u, v
