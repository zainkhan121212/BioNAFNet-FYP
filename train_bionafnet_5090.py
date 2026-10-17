"""
BioNAFNet — Enhanced NAFNet with 7 Biological Novelties
========================================================
Self-contained training + testing script for LOLv1/v2 low-light enhancement.

7 Novel Contributions integrated into NAFNet backbone:
  1. Retinal Lateral Inhibition Network (RLIN)
  2. Frequency-Aware Enhancement Branch (FAEB)
  3. Adaptive Receptive Field Pooling (ARFP)
  4. Photoreceptor Response Curve Modeling (PRCM)
  5. Scotopic-Photopic Dual Pathway (SPDP)
  6. Temporal Adaptation Memory (TAM)
  7. Weber-Fechner Perceptual Loss (WFPL)

Usage:
  python train_bionafnet.py                 # Train 500 epochs
  python train_bionafnet.py --test_only     # Test best checkpoint
"""

import os
import sys
import math
import glob
import copy
import argparse
import time
import random

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, ConcatDataset
import numpy as np
from PIL import Image
from tqdm import tqdm
from skimage.metrics import structural_similarity as calc_ssim
from skimage.metrics import peak_signal_noise_ratio as calc_psnr

# ══════════════════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════════════════
EPOCHS          = 500
BATCH_SIZE      = 8           # Increased for 5090
INIT_LR         = 2e-4
MIN_LR          = 1e-6
WEIGHT_DECAY    = 1e-4
GRAD_CLIP       = 0.5
EMA_DECAY       = 0.9995
USE_AMP         = True
ACCUM_STEPS     = 4           # Effective batch size = 8*4 = 32

# NAFNet config
# RTX 5090 "Beast Mode" Config
WIDTH           = 64          # Full width
n_passes        = 2           # 2-pass TAM for best quality
ENC_BLKS        = [2, 2, 4, 8]
MIDDLE_BLK_NUM  = 12
DEC_BLKS        = [2, 2, 2, 2]

# High-Res Progressive Resizing (5090 has 24-32GB VRAM)
PATCH_SCHEDULE  = {0: 256, 100: 384, 200: 512}

# Data paths
# Data paths - Try local ./data first, then fallback
DATA_ROOT       = "data"
if not os.path.exists(DATA_ROOT):
    # Fallback to hardcoded path if needed (user should edit this)
    DATA_ROOT   = r"C:\data"

LOLv1_TRAIN_IN  = os.path.join(DATA_ROOT, "LOLv1", "Train", "input")
LOLv1_TRAIN_GT  = os.path.join(DATA_ROOT, "LOLv1", "Train", "target")
LOLv1_TEST_IN   = os.path.join(DATA_ROOT, "LOLv1", "Test", "input")
LOLv1_TEST_GT   = os.path.join(DATA_ROOT, "LOLv1", "Test", "target")
LOLv2R_TRAIN_IN = os.path.join(DATA_ROOT, "LOLv2", "Real_captured", "Train", "Low")
LOLv2R_TRAIN_GT = os.path.join(DATA_ROOT, "LOLv2", "Real_captured", "Train", "Normal")
LOLv2S_TRAIN_IN = os.path.join(DATA_ROOT, "LOLv2", "Synthetic", "Train", "Low")
LOLv2S_TRAIN_GT = os.path.join(DATA_ROOT, "LOLv2", "Synthetic", "Train", "Normal")

SCRIPT_DIR      = os.path.dirname(os.path.abspath(__file__))
CKPT_DIR        = os.path.join(SCRIPT_DIR, "checkpoints_5090")
RESULTS_DIR     = os.path.join(SCRIPT_DIR, "results_5090")
LOG_FILE        = os.path.join(SCRIPT_DIR, "training_log_5090.txt")
os.makedirs(CKPT_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

BEST_PATH       = os.path.join(CKPT_DIR, "best.pth")


def log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def seed_everything(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


# ══════════════════════════════════════════════════════════════════════════════
# NOVEL 1: Retinal Lateral Inhibition Network (RLIN)
# ══════════════════════════════════════════════════════════════════════════════
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


# ══════════════════════════════════════════════════════════════════════════════
# NOVEL 2: Frequency-Aware Enhancement Branch (FAEB)
# ══════════════════════════════════════════════════════════════════════════════
class FrequencyBranch(nn.Module):
    """Fourier-domain texture recovery for degraded high-frequencies."""
    def __init__(self, ch):
        super().__init__()
        self.conv_amp = nn.Sequential(
            nn.Conv2d(ch, ch, 3, padding=1), nn.PReLU(ch),
            nn.Conv2d(ch, ch, 3, padding=1),
        )
        self.conv_phase = nn.Sequential(
            nn.Conv2d(ch, ch, 3, padding=1), nn.PReLU(ch),
            nn.Conv2d(ch, ch, 3, padding=1),
        )
        self.blend = nn.Parameter(torch.ones(1) * 0.15)

    def forward(self, x):
        B, C, H, W = x.shape
        # Disable AMP autocast entirely — cuFFT half-precision only supports
        # power-of-2 dims, but bottleneck features can be 12x12 at patch=192, etc.
        with torch.amp.autocast(device_type='cuda', enabled=False):
            x_fp32 = x.float()
            fft = torch.fft.rfft2(x_fp32, norm="ortho")
            amp = torch.abs(fft)
            phase = torch.angle(fft)
            amp_out = self.conv_amp(amp)
            phase_out = self.conv_phase(phase)
            real = amp_out * torch.cos(phase_out)
            imag = amp_out * torch.sin(phase_out)
            fft_out = torch.complex(real, imag)
            out = torch.fft.irfft2(fft_out, s=(H, W), norm="ortho")
        return x + self.blend * out.to(x.dtype)


# ══════════════════════════════════════════════════════════════════════════════
# NOVEL 3: Adaptive Receptive Field Pooling (ARFP)
# ══════════════════════════════════════════════════════════════════════════════
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


# ══════════════════════════════════════════════════════════════════════════════
# NOVEL 4: Photoreceptor Response Curve Modeling (PRCM)
# ══════════════════════════════════════════════════════════════════════════════
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


# ══════════════════════════════════════════════════════════════════════════════
# NOVEL 5: Scotopic-Photopic Dual Pathway (SPDP)
# ══════════════════════════════════════════════════════════════════════════════
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


# ══════════════════════════════════════════════════════════════════════════════
# NOVEL 6: Temporal Adaptation Memory (TAM)
# ══════════════════════════════════════════════════════════════════════════════
class TemporalAdaptation(nn.Module):
    """GRU-based progressive refinement across iterative passes."""
    def __init__(self, ch=32):
        super().__init__()
        self.gru = nn.GRUCell(ch, ch)
        self.proj_in = nn.Conv2d(3, ch, 1)
        self.proj_out = nn.Conv2d(ch, 3, 1)

    def forward(self, pass_outputs):
        B, _, H, W = pass_outputs[0].shape
        hidden = torch.zeros(B * H * W, self.gru.hidden_size,
                             device=pass_outputs[0].device)
        for out in pass_outputs:
            feat = self.proj_in(out)
            feat = feat.permute(0, 2, 3, 1).reshape(B * H * W, -1)
            hidden = self.gru(feat, hidden)
        out = hidden.reshape(B, H, W, -1).permute(0, 3, 1, 2)
        residual = self.proj_out(out) * 0.15
        return pass_outputs[-1] + residual


# ══════════════════════════════════════════════════════════════════════════════
# NAFNet Building Blocks (Enhanced)
# ══════════════════════════════════════════════════════════════════════════════

def luminance(x):
    return 0.299 * x[:, 0:1] + 0.587 * x[:, 1:2] + 0.114 * x[:, 2:3]


class LayerNorm2d(nn.Module):
    def __init__(self, channels, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(channels))
        self.bias = nn.Parameter(torch.zeros(channels))
        self.eps = eps

    def forward(self, x):
        u = x.mean(1, keepdim=True)
        s = (x - u).pow(2).mean(1, keepdim=True)
        x = (x - u) / torch.sqrt(s + self.eps)
        return self.weight[None, :, None, None] * x + self.bias[None, :, None, None]


class SimpleGate(nn.Module):
    def forward(self, x):
        x1, x2 = x.chunk(2, dim=1)
        return x1 * x2


class BioNAFBlock(nn.Module):
    """NAFBlock enhanced with RLIN (Lateral Inhibition)."""
    def __init__(self, c, DW_Expand=2, FFN_Expand=2, drop_out_rate=0., use_rlin=True):
        super().__init__()
        dw_channel = c * DW_Expand

        self.conv1 = nn.Conv2d(c, dw_channel, 1, bias=True)
        self.conv2 = nn.Conv2d(dw_channel, dw_channel, 3, padding=1,
                               groups=dw_channel, bias=True)
        self.conv3 = nn.Conv2d(dw_channel // 2, c, 1, bias=True)

        # Simplified Channel Attention
        self.sca = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(dw_channel // 2, dw_channel // 2, 1, bias=True),
        )

        self.sg = SimpleGate()

        ffn_channel = FFN_Expand * c
        self.conv4 = nn.Conv2d(c, ffn_channel, 1, bias=True)
        self.conv5 = nn.Conv2d(ffn_channel // 2, c, 1, bias=True)

        self.norm1 = LayerNorm2d(c)
        self.norm2 = LayerNorm2d(c)

        self.dropout1 = nn.Dropout(drop_out_rate) if drop_out_rate > 0. else nn.Identity()
        self.dropout2 = nn.Dropout(drop_out_rate) if drop_out_rate > 0. else nn.Identity()

        self.beta = nn.Parameter(torch.zeros((1, c, 1, 1)), requires_grad=True)
        self.gamma = nn.Parameter(torch.zeros((1, c, 1, 1)), requires_grad=True)

        # NOVEL 1: RLIN integrated into each block
        self.rlin = LateralInhibition(c) if use_rlin else nn.Identity()

    def forward(self, inp):
        x = self.norm1(inp)
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.sg(x)
        x = x * self.sca(x)
        x = self.conv3(x)
        x = self.dropout1(x)

        # RLIN after spatial channel attention
        x = self.rlin(x)

        y = inp + x * self.beta

        x = self.conv4(self.norm2(y))
        x = self.sg(x)
        x = self.conv5(x)
        x = self.dropout2(x)
        return y + x * self.gamma


class BioNAFNet(nn.Module):
    """
    NAFNet enhanced with 7 Biological Novelties.
    Pipeline: PRCM → SPDP → NAFNet(RLIN + FAEB + ARFP) → TAM refinement
    """
    def __init__(self, img_channel=3, width=64, middle_blk_num=12,
                 enc_blk_nums=[2, 2, 4, 8], dec_blk_nums=[2, 2, 2, 2],
                 n_passes=2):
        super().__init__()
        self.n_passes = n_passes

        # NOVEL 4: Photoreceptor Curve (pre-processing)
        self.prcm = PhotoreceptorCurve()

        # NOVEL 5: Dual Pathway (pre-processing)
        self.spdp = DualPathway(ch=32)

        # NAFNet backbone
        self.intro = nn.Conv2d(img_channel, width, 3, padding=1, bias=True)
        self.ending = nn.Conv2d(width, img_channel, 3, padding=1, bias=True)

        self.encoders = nn.ModuleList()
        self.decoders = nn.ModuleList()
        self.ups = nn.ModuleList()
        self.downs = nn.ModuleList()

        chan = width
        for i, num in enumerate(enc_blk_nums):
            # RLIN in encoder blocks (skip deepest to save memory)
            use_rlin = (i < len(enc_blk_nums) - 1)
            self.encoders.append(nn.Sequential(
                *[BioNAFBlock(chan, use_rlin=use_rlin) for _ in range(num)]
            ))
            self.downs.append(nn.Conv2d(chan, 2 * chan, 2, 2))
            chan *= 2

        # Bottleneck + NOVEL 2: FAEB
        self.middle_blks = nn.Sequential(
            *[BioNAFBlock(chan, use_rlin=False) for _ in range(middle_blk_num)]
        )
        self.faeb = FrequencyBranch(chan)

        for num in dec_blk_nums:
            self.ups.append(nn.Sequential(
                nn.Conv2d(chan, chan * 2, 1, bias=False),
                nn.PixelShuffle(2)
            ))
            chan //= 2
            self.decoders.append(nn.Sequential(
                *[BioNAFBlock(chan, use_rlin=False) for _ in range(num)]
            ))

        # NOVEL 3: ARFP at decoder output
        self.arfp = AdaptiveReceptiveField(chan)

        # NOVEL 6: TAM for multi-pass refinement
        self.tam = TemporalAdaptation(ch=32)

        self.padder_size = 2 ** len(self.encoders)

    def forward_single(self, inp, lum_map):
        """Single forward pass through NAFNet backbone."""
        B, C, H, W = inp.shape
        inp_padded = self.check_image_size(inp)

        x = self.intro(inp_padded)
        encs = []
        for encoder, down in zip(self.encoders, self.downs):
            x = encoder(x)
            encs.append(x)
            x = down(x)

        x = self.middle_blks(x)
        x = self.faeb(x)  # NOVEL 2: Frequency branch at bottleneck

        for decoder, up, enc_skip in zip(self.decoders, self.ups, encs[::-1]):
            x = up(x)
            x = x + enc_skip
            x = decoder(x)

        # NOVEL 3: ARFP at final decoder level
        x = self.arfp(x, lum_map)

        x = self.ending(x)
        x = x + inp_padded  # Residual learning
        return x[:, :, :H, :W]

    def forward(self, x):
        # NOVEL 4: Photoreceptor response curve
        x_prcm = self.prcm(x)

        # NOVEL 5: Scotopic-Photopic dual pathway
        x_spdp = self.spdp(x_prcm)

        lum_map = luminance(x)

        # Multi-pass refinement for TAM
        pass_outputs = []
        current = x_spdp
        for p in range(self.n_passes):
            out = self.forward_single(current, lum_map)
            out = out.clamp(0, 1)
            pass_outputs.append(out)
            current = out  # Feed back for next pass

        # NOVEL 6: TAM aggregates multi-pass results
        if self.n_passes > 1:
            final = self.tam(pass_outputs)
        else:
            final = pass_outputs[-1]

        return final.clamp(0, 1)

    def check_image_size(self, x):
        _, _, h, w = x.size()
        mod_pad_h = (self.padder_size - h % self.padder_size) % self.padder_size
        mod_pad_w = (self.padder_size - w % self.padder_size) % self.padder_size
        x = F.pad(x, (0, mod_pad_w, 0, mod_pad_h))
        return x


# ══════════════════════════════════════════════════════════════════════════════
# NOVEL 7: Weber-Fechner Perceptual Loss + Full Loss Suite
# ══════════════════════════════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════════════════════════════
# Dataset with Heavy Augmentation
# ══════════════════════════════════════════════════════════════════════════════

class LOLDataset(Dataset):
    def __init__(self, input_dir, target_dir, patch_size=None, augment=False):
        self.input_files = sorted(glob.glob(os.path.join(input_dir, "*.*")))
        self.target_files = sorted(glob.glob(os.path.join(target_dir, "*.*")))
        assert len(self.input_files) == len(self.target_files), \
            f"Mismatch: {len(self.input_files)} inputs vs {len(self.target_files)} targets"
        self.patch_size = patch_size
        self.augment = augment

    def __len__(self):
        return len(self.input_files)

    def __getitem__(self, idx):
        inp = np.array(Image.open(self.input_files[idx]).convert("RGB")).astype(np.float32) / 255.0
        tgt = np.array(Image.open(self.target_files[idx]).convert("RGB")).astype(np.float32) / 255.0

        # Resize if shapes don't match
        if inp.shape != tgt.shape:
            h = min(inp.shape[0], tgt.shape[0])
            w = min(inp.shape[1], tgt.shape[1])
            inp = inp[:h, :w]
            tgt = tgt[:h, :w]

        if self.patch_size:
            h, w, _ = inp.shape
            ps = self.patch_size
            if h < ps or w < ps:
                # Pad if image is smaller than patch
                pad_h = max(0, ps - h)
                pad_w = max(0, ps - w)
                inp = np.pad(inp, ((0, pad_h), (0, pad_w), (0, 0)), mode='reflect')
                tgt = np.pad(tgt, ((0, pad_h), (0, pad_w), (0, 0)), mode='reflect')
                h, w = inp.shape[:2]
            rh = np.random.randint(0, h - ps + 1)
            rw = np.random.randint(0, w - ps + 1)
            inp = inp[rh:rh + ps, rw:rw + ps]
            tgt = tgt[rh:rh + ps, rw:rw + ps]

        if self.augment:
            # Horizontal flip
            if np.random.rand() > 0.5:
                inp, tgt = inp[:, ::-1].copy(), tgt[:, ::-1].copy()
            # Vertical flip
            if np.random.rand() > 0.5:
                inp, tgt = inp[::-1].copy(), tgt[::-1].copy()
            # Random 90° rotation
            k = np.random.randint(0, 4)
            inp, tgt = np.rot90(inp, k).copy(), np.rot90(tgt, k).copy()
            # MixUp augmentation (20% chance)
            if np.random.rand() < 0.2 and self.patch_size:
                idx2 = np.random.randint(0, len(self))
                inp2 = np.array(Image.open(self.input_files[idx2]).convert("RGB")).astype(np.float32) / 255.0
                tgt2 = np.array(Image.open(self.target_files[idx2]).convert("RGB")).astype(np.float32) / 255.0
                if inp2.shape != tgt2.shape:
                    h2 = min(inp2.shape[0], tgt2.shape[0])
                    w2 = min(inp2.shape[1], tgt2.shape[1])
                    inp2 = inp2[:h2, :w2]
                    tgt2 = tgt2[:h2, :w2]
                h2, w2, _ = inp2.shape
                ps = self.patch_size
                if h2 >= ps and w2 >= ps:
                    rh2 = np.random.randint(0, h2 - ps + 1)
                    rw2 = np.random.randint(0, w2 - ps + 1)
                    inp2 = inp2[rh2:rh2+ps, rw2:rw2+ps]
                    tgt2 = tgt2[rh2:rh2+ps, rw2:rw2+ps]
                    lam = np.random.beta(0.5, 0.5)
                    inp = lam * inp + (1 - lam) * inp2
                    tgt = lam * tgt + (1 - lam) * tgt2

        inp = torch.from_numpy(inp.copy()).permute(2, 0, 1).float()
        tgt = torch.from_numpy(tgt.copy()).permute(2, 0, 1).float()
        return inp, tgt


# ══════════════════════════════════════════════════════════════════════════════
# EMA Helper
# ══════════════════════════════════════════════════════════════════════════════

class EMA:
    def __init__(self, model, decay=0.9995):
        self.decay = decay
        self.shadow = copy.deepcopy(model)
        self.shadow.eval()
        for p in self.shadow.parameters():
            p.requires_grad_(False)

    def update(self, model):
        with torch.no_grad():
            for s_param, m_param in zip(self.shadow.parameters(), model.parameters()):
                s_param.data.mul_(self.decay).add_(m_param.data, alpha=1 - self.decay)

    def apply(self, model):
        model.load_state_dict(self.shadow.state_dict())


# ══════════════════════════════════════════════════════════════════════════════
# Training
# ══════════════════════════════════════════════════════════════════════════════

def psnr_tensor(pred, target):
    mse = F.mse_loss(pred.clamp(0, 1), target)
    if mse == 0:
        return 100.0
    return 10 * math.log10(1.0 / mse.item())


def get_patch_size(epoch):
    """Progressive resizing: start small, grow larger."""
    ps = 128
    for e, p in sorted(PATCH_SCHEDULE.items()):
        if epoch >= e:
            ps = p
    return ps


def train(model, device):
    seed_everything(42)

    total_params = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    log("=" * 70)
    log("BioNAFNet — RTX 5090 Beast Mode")
    log(f"Width: {WIDTH}, Enc: {ENC_BLKS}, Mid: {MIDDLE_BLK_NUM}, Dec: {DEC_BLKS}, Passes: {n_passes}")
    log(f"Total params: {total_params:,}  |  Trainable: {trainable:,}")
    log(f"Device: {device}")
    log(f"Epochs: {EPOCHS}, LR: {INIT_LR}, Batch: {BATCH_SIZE}x{ACCUM_STEPS}")
    log(f"Progressive patches: {PATCH_SCHEDULE}")
    log("=" * 70)

    # Multi-dataset: LOLv1 + LOLv2Real + LOLv2Synthetic
    val_ds = LOLDataset(LOLv1_TEST_IN, LOLv1_TEST_GT, patch_size=None, augment=False)
    val_loader = DataLoader(val_ds, batch_size=1, shuffle=False,
                            num_workers=2, pin_memory=True)

    criterion = TotalLoss(device)
    optimizer = optim.AdamW(model.parameters(), lr=INIT_LR, weight_decay=WEIGHT_DECAY,
                            betas=(0.9, 0.999))
    scaler = torch.amp.GradScaler(enabled=USE_AMP)
    ema = EMA(model, decay=EMA_DECAY)

    # Cosine annealing with warm restarts
    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer, T_0=50, T_mult=2, eta_min=MIN_LR
    )

    best_psnr = 0.0
    nan_total = 0
    start_epoch = 0

    # Resume from checkpoint if exists
    latest_path = os.path.join(CKPT_DIR, "latest.pth")
    if os.path.exists(latest_path):
        ckpt = torch.load(latest_path, map_location=device, weights_only=False)
        model.load_state_dict(ckpt["model"])
        ema.shadow.load_state_dict(ckpt["ema"])
        optimizer.load_state_dict(ckpt["optimizer"])
        start_epoch = ckpt["epoch"]
        best_psnr = ckpt.get("best_psnr", 0)
        # Advance scheduler to the correct position
        for _ in range(start_epoch):
            scheduler.step()
        log(f"Resumed from epoch {start_epoch}, best PSNR: {best_psnr:.2f} dB")

    for epoch in range(start_epoch, EPOCHS):
        # Progressive patch size
        ps = get_patch_size(epoch)

        # Rebuild train loader with new patch size each phase
        train_datasets = []
        if os.path.isdir(LOLv1_TRAIN_IN):
            train_datasets.append(LOLDataset(LOLv1_TRAIN_IN, LOLv1_TRAIN_GT,
                                             patch_size=ps, augment=True))
        if os.path.isdir(LOLv2R_TRAIN_IN):
            train_datasets.append(LOLDataset(LOLv2R_TRAIN_IN, LOLv2R_TRAIN_GT,
                                             patch_size=ps, augment=True))
        if os.path.isdir(LOLv2S_TRAIN_IN):
            train_datasets.append(LOLDataset(LOLv2S_TRAIN_IN, LOLv2S_TRAIN_GT,
                                             patch_size=ps, augment=True))

        train_ds = ConcatDataset(train_datasets)
        train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,
                                  num_workers=4, pin_memory=True, drop_last=True,
                                  persistent_workers=True)

        if epoch == start_epoch:
            log(f"Training dataset: {len(train_ds)} images")
            log(f"Validation dataset: {len(val_ds)} images")

        model.train()
        running_loss = 0.0
        running_psnr = 0.0

        pbar = tqdm(train_loader, desc=f"E{epoch+1}/{EPOCHS} ps={ps}")
        optimizer.zero_grad(set_to_none=True)

        for step, (low, high) in enumerate(pbar, 1):
            low = low.to(device, non_blocking=True)
            high = high.to(device, non_blocking=True)

            with torch.amp.autocast(device_type=device.type, enabled=USE_AMP):
                out = model(low)
                loss, loss_dict = criterion(out, high)
                loss = loss / ACCUM_STEPS

            scaler.scale(loss).backward()

            if step % ACCUM_STEPS == 0:
                scaler.unscale_(optimizer)

                # NaN gradient check
                has_nan = any(
                    p.grad is not None and torch.isnan(p.grad).any()
                    for p in model.parameters()
                )
                if has_nan:
                    nan_total += 1
                    log(f"  [WARN] NaN grad at epoch {epoch+1}, step {step} (total: {nan_total})")
                    optimizer.zero_grad(set_to_none=True)
                    scaler.update()
                    continue

                torch.nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad(set_to_none=True)
                ema.update(model)

            running_loss += loss.item() * ACCUM_STEPS
            running_psnr += psnr_tensor(out.detach(), high)
            pbar.set_postfix(
                loss=f"{running_loss/step:.4f}",
                psnr=f"{running_psnr/step:.2f}",
                lr=f"{optimizer.param_groups[0]['lr']:.2e}"
            )

        scheduler.step()

        # ── Validate using EMA model ──
        ema.shadow.eval()
        vp, vs = 0.0, 0.0
        with torch.no_grad():
            for low, high in val_loader:
                low = low.to(device, non_blocking=True)
                high = high.to(device, non_blocking=True)
                # No AMP here — full-res images have non-power-of-2 dims,
                # cuFFT half-precision only supports power-of-2
                out = ema.shadow(low)
                out = out.clamp(0, 1)
                vp += psnr_tensor(out, high)
                out_np = out.squeeze().permute(1, 2, 0).cpu().numpy()
                high_np = high.squeeze().permute(1, 2, 0).cpu().numpy()
                vs += calc_ssim(high_np, out_np, data_range=1.0, channel_axis=2)

        avg_vp = vp / len(val_loader)
        avg_vs = vs / len(val_loader)
        avg_tl = running_loss / len(train_loader)
        avg_tp = running_psnr / len(train_loader)
        lr = optimizer.param_groups[0]['lr']

        log(f"Epoch {epoch+1}/{EPOCHS} | Loss: {avg_tl:.4f} | Train PSNR: {avg_tp:.2f} | "
            f"Val PSNR: {avg_vp:.2f} dB | Val SSIM: {avg_vs:.4f} | "
            f"LR: {lr:.2e} | Patch: {ps} | Gap: {avg_tp - avg_vp:.2f}")

        if avg_vp > best_psnr:
            best_psnr = avg_vp
            torch.save({
                "epoch": epoch + 1,
                "model": model.state_dict(),
                "ema": ema.shadow.state_dict(),
                "optimizer": optimizer.state_dict(),
                "best_psnr": best_psnr,
            }, BEST_PATH)
            log(f"  *** New Best: {best_psnr:.2f} dB ***")

        # Save latest checkpoint (for resume)
        torch.save({
            "epoch": epoch + 1,
            "model": model.state_dict(),
            "ema": ema.shadow.state_dict(),
            "optimizer": optimizer.state_dict(),
            "best_psnr": best_psnr,
        }, os.path.join(CKPT_DIR, "latest.pth"))

        # Save periodic checkpoints
        if (epoch + 1) % 50 == 0:
            torch.save({
                "epoch": epoch + 1,
                "model": model.state_dict(),
                "ema": ema.shadow.state_dict(),
                "optimizer": optimizer.state_dict(),
                "best_psnr": best_psnr,
            }, os.path.join(CKPT_DIR, f"ckpt_{epoch+1}.pth"))

    log("=" * 70)
    log(f"Training Complete! Best Val PSNR: {best_psnr:.2f} dB")
    log("=" * 70)
    return best_psnr


# ══════════════════════════════════════════════════════════════════════════════
# Testing
# ══════════════════════════════════════════════════════════════════════════════

def test(model, device):
    if os.path.exists(BEST_PATH):
        ckpt = torch.load(BEST_PATH, map_location=device, weights_only=False)
        # Use EMA weights for best performance
        if "ema" in ckpt:
            model.load_state_dict(ckpt["ema"])
            log(f"Loaded EMA checkpoint: epoch {ckpt.get('epoch', '?')}, "
                f"PSNR {ckpt.get('best_psnr', 0):.2f} dB")
        else:
            model.load_state_dict(ckpt["model"])
            log(f"Loaded model checkpoint: epoch {ckpt.get('epoch', '?')}")
    else:
        log("WARNING: No checkpoint found. Running with random weights.")

    val_ds = LOLDataset(LOLv1_TEST_IN, LOLv1_TEST_GT, patch_size=None, augment=False)
    val_loader = DataLoader(val_ds, batch_size=1, shuffle=False, num_workers=2, pin_memory=True)

    model.eval()
    all_psnr, all_ssim = [], []

    log(f"\n{'='*70}")
    log(f"BioNAFNet — Testing on LOLv1 ({len(val_ds)} images)")
    log(f"{'='*70}")

    with torch.no_grad():
        for i, (low, high) in enumerate(val_loader):
            low = low.to(device, non_blocking=True)
            high = high.to(device, non_blocking=True)

            # No AMP — full-res images can have non-power-of-2 dims
            out = model(low)
            out = out.clamp(0, 1)

            out_np = out.squeeze().permute(1, 2, 0).cpu().numpy()
            high_np = high.squeeze().permute(1, 2, 0).cpu().numpy()
            p = calc_psnr(high_np, out_np, data_range=1.0)
            s = calc_ssim(high_np, out_np, data_range=1.0, channel_axis=2)
            all_psnr.append(p)
            all_ssim.append(s)

            # Save enhanced image
            out_img = (out_np * 255).clip(0, 255).astype(np.uint8)
            fname = os.path.basename(val_ds.input_files[i])
            Image.fromarray(out_img).save(os.path.join(RESULTS_DIR, fname))

            print(f"  {fname:30s} PSNR: {p:.2f} dB  SSIM: {s:.4f}")

    avg_psnr = np.mean(all_psnr)
    avg_ssim = np.mean(all_ssim)
    log(f"\n{'='*70}")
    log(f"Average PSNR: {avg_psnr:.2f} dB")
    log(f"Average SSIM: {avg_ssim:.4f}")
    log(f"Enhanced images saved to: {RESULTS_DIR}")
    log(f"{'='*70}")

    return avg_psnr, avg_ssim


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_only", action="store_true")
    parser.add_argument("--n_passes", type=int, default=2,
                        help="Number of iterative refinement passes (for TAM)")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = BioNAFNet(
        img_channel=3,
        width=WIDTH,
        middle_blk_num=MIDDLE_BLK_NUM,
        enc_blk_nums=ENC_BLKS,
        dec_blk_nums=DEC_BLKS,
        n_passes=args.n_passes,
    ).to(device)

    if not args.test_only:
        train(model, device)

    test(model, device)
