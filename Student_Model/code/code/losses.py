"""
losses.py — Loss Functions (including NOVEL 7: Weber-Fechner Perceptual Loss)
=============================================================================
Processing Order: #5 (loaded by training.py)

Contains:
  - CharbonnierLoss
  - SSIMLoss
  - EdgeLoss
  - ColorLoss
  - WeberFechnerLoss  (NOVEL 7)
  - PerceptualLoss (VGG-based)
  - TotalLoss (combined weighted loss)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

from novels import luminance


class CharbonnierLoss(nn.Module):
    def __init__(self, eps=1e-3):
        super().__init__()
        self.eps = eps

    def forward(self, pred, target):
        diff = pred - target
        return torch.sqrt(diff * diff + self.eps * self.eps).mean()


class SSIMLoss(nn.Module):
    def __init__(self):
        super().__init__()
        self.c1 = 0.01 ** 2
        self.c2 = 0.03 ** 2

    def forward(self, x, y):
        mu_x = F.avg_pool2d(x, 3, 1, 1)
        mu_y = F.avg_pool2d(y, 3, 1, 1)
        sig_x = F.avg_pool2d(x * x, 3, 1, 1) - mu_x * mu_x
        sig_y = F.avg_pool2d(y * y, 3, 1, 1) - mu_y * mu_y
        sig_xy = F.avg_pool2d(x * y, 3, 1, 1) - mu_x * mu_y
        num = (2 * mu_x * mu_y + self.c1) * (2 * sig_xy + self.c2)
        den = (mu_x ** 2 + mu_y ** 2 + self.c1) * (sig_x + sig_y + self.c2)
        return 1 - (num / (den + 1e-7)).mean()


class EdgeLoss(nn.Module):
    def __init__(self):
        super().__init__()
        sx = torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
                          dtype=torch.float32).view(1, 1, 3, 3)
        sy = torch.tensor([[-1, -2, -1], [0, 0, 0], [1, 2, 1]],
                          dtype=torch.float32).view(1, 1, 3, 3)
        self.register_buffer("sx", sx)
        self.register_buffer("sy", sy)

    def edges(self, x):
        g = luminance(x)
        # Move Sobel filters to input device/dtype (fixes AMP half-precision crash)
        sx = self.sx.to(g.device, g.dtype)
        sy = self.sy.to(g.device, g.dtype)
        ex = F.conv2d(g, sx, padding=1)
        ey = F.conv2d(g, sy, padding=1)
        return torch.sqrt(ex * ex + ey * ey + 1e-4)

    def forward(self, pred, target):
        return F.l1_loss(self.edges(pred), self.edges(target))


class ColorLoss(nn.Module):
    def rgb_to_yuv(self, rgb):
        r, g, b = rgb[:, 0:1], rgb[:, 1:2], rgb[:, 2:3]
        y = 0.299 * r + 0.587 * g + 0.114 * b
        u = -0.147 * r - 0.289 * g + 0.436 * b
        v = 0.615 * r - 0.515 * g - 0.100 * b
        return torch.cat([y, u, v], dim=1)

    def forward(self, pred, target):
        py, ty = self.rgb_to_yuv(pred), self.rgb_to_yuv(target)
        return F.l1_loss(py[:, 1:], ty[:, 1:])


class WeberFechnerLoss(nn.Module):
    """NOVEL 7: Weber-Fechner Perceptual Loss.
    Weights errors more in dark regions where human perception is most sensitive.
    """
    def __init__(self, eps=0.02):
        super().__init__()
        self.eps = eps

    def forward(self, pred, target):
        lum = luminance(target)
        weight = 1.0 / (lum + self.eps)
        weight = weight / (weight.mean() + 1e-6)
        diff = torch.abs(pred - target)
        return (diff * weight).mean()


class PerceptualLoss(nn.Module):
    def __init__(self, device):
        super().__init__()
        from torchvision import models
        vgg = models.vgg16(weights=models.VGG16_Weights.IMAGENET1K_V1).features[:16].eval().to(device)
        for p in vgg.parameters():
            p.requires_grad = False
        self.vgg = vgg
        self.mean = torch.tensor([0.485, 0.456, 0.406], device=device).view(1, 3, 1, 1)
        self.std = torch.tensor([0.229, 0.224, 0.225], device=device).view(1, 3, 1, 1)

    def norm(self, x):
        return (x - self.mean) / (self.std + 1e-6)

    def forward(self, x, y):
        return F.l1_loss(self.vgg(self.norm(x)), self.vgg(self.norm(y)))


class TotalLoss(nn.Module):
    """Combined loss with all 7 components."""
    def __init__(self, device):
        super().__init__()
        self.charb = CharbonnierLoss()
        self.ssim = SSIMLoss()
        self.perc = PerceptualLoss(device)
        self.edge = EdgeLoss()
        self.color = ColorLoss()
        self.weber = WeberFechnerLoss()

    def forward(self, out, target):
        l_charb = self.charb(out, target)
        l_ssim = self.ssim(out, target)
        l_perc = self.perc(out, target)
        l_edge = self.edge(out, target)
        l_color = self.color(out, target)
        l_weber = self.weber(out, target)

        total = (
            1.0 * l_charb +
            0.8 * l_ssim +
            0.2 * l_perc +
            0.25 * l_edge +
            0.1 * l_color +
            0.3 * l_weber
        )

        return total, {
            "charb": l_charb.item(),
            "ssim": l_ssim.item(),
            "perc": l_perc.item(),
            "edge": l_edge.item(),
            "color": l_color.item(),
            "weber": l_weber.item(),
        }
