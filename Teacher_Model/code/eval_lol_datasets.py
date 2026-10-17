"""
BioNAFNet Knowledge Distillation
================================
Compresses the massive 154M parameter BioNAFNet into a lightweight 18M parameter
"Student" model for fast mobile/laptop inference.

The student learns by mimicking the teacher's exact outputs (L2 Output Mimic Loss)
along with standard GT reconstruction (L1 + SSIM).
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
EPOCHS          = 1000
BATCH_SIZE      = 4
INIT_LR         = 2e-4
MIN_LR          = 1e-6
WEIGHT_DECAY    = 1e-4
GRAD_CLIP       = 0.5
EMA_DECAY       = 0.9995
USE_AMP         = True
ACCUM_STEPS     = 2           # Effective batch size = 4*2 = 8

# NAFNet config (Student Architecture - Lightweight)
WIDTH           = 32          # Dropped from 64
ENC_BLKS        = [2, 2, 4, 8]
MIDDLE_BLK_NUM  = 4           # Dropped from 12
DEC_BLKS        = [2, 2, 2, 2]
STUDENT_PASSES  = 1           # Dropped from 2 to boost FPS

# Distillation Loss Weights
LAMBDA_L1       = 0.5
LAMBDA_SSIM     = 0.1
LAMBDA_MIMIC    = 0.4         # High weight for copying teacher

# Progressive resizing
PATCH_SCHEDULE  = {0: 128}

# Data paths
DATA_ROOT       = r"c:\Users\GNG\Desktop\retinex former\Retinexformer-master\data"
LOLv1_TRAIN_IN  = os.path.join(DATA_ROOT, "LOLv1", "Train", "input")
LOLv1_TRAIN_GT  = os.path.join(DATA_ROOT, "LOLv1", "Train", "target")
LOLv1_TEST_IN   = os.path.join(DATA_ROOT, "LOLv1", "Test", "input")
LOLv1_TEST_GT   = os.path.join(DATA_ROOT, "LOLv1", "Test", "target")
LOLv2R_TRAIN_IN = os.path.join(DATA_ROOT, "LOLv2", "Real_captured", "Train", "Low")
LOLv2R_TRAIN_GT = os.path.join(DATA_ROOT, "LOLv2", "Real_captured", "Train", "Normal")
LOLv2S_TRAIN_IN = os.path.join(DATA_ROOT, "LOLv2", "Synthetic", "Train", "Low")
LOLv2S_TRAIN_GT = os.path.join(DATA_ROOT, "LOLv2", "Synthetic", "Train", "Normal")

SCRIPT_DIR      = os.path.dirname(os.path.abspath(__file__))
CKPT_DIR        = os.path.join(SCRIPT_DIR, "checkpoints_student") # NEW folder
TEACHER_CKPT    = os.path.join(SCRIPT_DIR, "checkpoints", "latest.pth") # Source teacher
RESULTS_DIR     = os.path.join(SCRIPT_DIR, "results_student")
LOG_FILE        = os.path.join(SCRIPT_DIR, "distillation_log.txt")
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
# ══════════════════════════════════════════════════════════════════════════════
# Evaluation Logic
# ══════════════════════════════════════════════════════════════════════════════

def evaluate(model, dataset_dir, output_dir, device):
    os.makedirs(output_dir, exist_ok=True)
    
    # Try different common naming conventions for low-light datasets
    low_dir = os.path.join(dataset_dir, 'low')
    high_dir = os.path.join(dataset_dir, 'high')
    
    if not os.path.exists(low_dir):
        low_dir_test = os.path.join(dataset_dir, 'Low')
        if os.path.exists(low_dir_test): low_dir = low_dir_test
        else:
            low_dir_test = os.path.join(dataset_dir, 'input')
            if os.path.exists(low_dir_test): low_dir = low_dir_test

    if not os.path.exists(high_dir):
        high_dir_test = os.path.join(dataset_dir, 'Normal')
        if os.path.exists(high_dir_test): high_dir = high_dir_test
        else:
            high_dir_test = os.path.join(dataset_dir, 'target')
            if os.path.exists(high_dir_test): high_dir = high_dir_test
        
    if not os.path.exists(low_dir) or not os.path.exists(high_dir):
        print(f"Error: {dataset_dir} must contain low('low', 'Low', 'input') and high('high', 'Normal', 'target') subdirectories.")
        print(f"Checked: {low_dir} and {high_dir}")
        return 0, 0
    
    psnr_list, ssim_list = [], []
    files = sorted(os.listdir(low_dir))
    
    for f in tqdm(files, desc=f"Evaluating in {dataset_dir}"):
        if not f.lower().endswith(('.png', '.jpg', '.jpeg')): continue
        
        low_path = os.path.join(low_dir, f)
        high_path = os.path.join(high_dir, f)
        
        if not os.path.exists(high_path):
            print(f"Skipping {f} - GT not found")
            continue
            
        import cv2
        low_img = cv2.imread(low_path)
        high_img = cv2.imread(high_path)
        
        if low_img is None or high_img is None: continue
        
        # Convert to RGB
        low_img = cv2.cvtColor(low_img, cv2.COLOR_BGR2RGB)
        high_img = cv2.cvtColor(high_img, cv2.COLOR_BGR2RGB)
        
        # Tensor formatting
        input_tensor = torch.from_numpy(low_img).permute(2, 0, 1).float().unsqueeze(0).to(device) / 255.0
        
        with torch.no_grad():
            output_tensor = model(input_tensor)
            
        output_img = output_tensor.squeeze().permute(1, 2, 0).cpu().numpy()
        output_img = np.clip(output_img * 255.0, 0, 255).astype(np.uint8)
        
        # Save exact output for visual inspection (in RGB converted back to BGR)
        cv2.imwrite(os.path.join(output_dir, f), cv2.cvtColor(output_img, cv2.COLOR_RGB2BGR))
        
        # Calculate PSNR and SSIM
        p = calc_psnr(high_img, output_img)
        s = calc_ssim(high_img, output_img, channel_axis=2, data_range=255)
        
        psnr_list.append(p)
        ssim_list.append(s)
        
    avg_psnr = np.mean(psnr_list) if psnr_list else 0
    avg_ssim = np.mean(ssim_list) if ssim_list else 0
    
    return avg_psnr, avg_ssim

def main():
    parser = argparse.ArgumentParser(description="Evaluate BioNAFNet-Lite on LOL datasets")
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to best.pth")
    parser.add_argument("--device", type=str, default="cuda", help="Device (cuda or cpu)")
    args = parser.parse_args()
    
    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Instantiate the Student version of BioNAFNet
    model = BioNAFNet(
        img_channel=3, 
        width=WIDTH, 
        middle_blk_num=MIDDLE_BLK_NUM, 
        enc_blk_nums=ENC_BLKS, 
        dec_blk_nums=DEC_BLKS, 
        n_passes=STUDENT_PASSES
    ).to(device)
    
    try:
        checkpoint = torch.load(args.checkpoint, map_location=device)
        
        # Handle the dictionary structure of this specific best.pth
        if 'model' in checkpoint:
            state_dict = checkpoint['model']
        elif 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
        else:
            state_dict = checkpoint
            
        # Optional: remove 'module.' prefix if it exists from DataParallel/DDP
        if list(state_dict.keys())[0].startswith('module.'):
            state_dict = {k[7:]: v for k, v in state_dict.items()}
            
        model.load_state_dict(state_dict)
        print(f"Successfully loaded checkpoint from {args.checkpoint}")
    except Exception as e:
        print(f"Failed to load checkpoint: {e}")
        import traceback
        traceback.print_exc()
        return
        
    model.eval()
    
    # LOLv1 Eval Setup
    lolv1_dir = r"c:\Users\GNG\Desktop\retinex former\Retinexformer-master\data\LOLv1\Test"
    lolv1_out = r"F:\low_light_enhancement\eye adaption\BioNAFNet\results_student\lolv1"
    
    # LOLv2 Real Eval Setup
    lolv2_real_dir = r"c:\Users\GNG\Desktop\retinex former\Retinexformer-master\data\LOLv2\Real_captured\Test"
    lolv2_real_out = r"F:\low_light_enhancement\eye adaption\BioNAFNet\results_student\lolv2_real"
    
    # LOLv2 Synthetic Eval Setup
    lolv2_synthetic_dir = r"c:\Users\GNG\Desktop\retinex former\Retinexformer-master\data\LOLv2\Synthetic\Test"
    lolv2_synthetic_out = r"F:\low_light_enhancement\eye adaption\BioNAFNet\results_student\lolv2_synthetic"
    
    print("\n" + "="*50)
    print("Evaluating LOLv1")
    lolv1_psnr, lolv1_ssim = evaluate(model, lolv1_dir, lolv1_out, device)
    print(f"LOLv1 -> PSNR: {lolv1_psnr:.4f} dB,  SSIM: {lolv1_ssim:.4f}")
    
    print("\n" + "="*50)
    print("Evaluating LOLv2 Real")
    lolv2_r_psnr, lolv2_r_ssim = evaluate(model, lolv2_real_dir, lolv2_real_out, device)
    print(f"LOLv2 Real -> PSNR: {lolv2_r_psnr:.4f} dB,  SSIM: {lolv2_r_ssim:.4f}")
    
    print("\n" + "="*50)
    print("Evaluating LOLv2 Synthetic")
    lolv2_s_psnr, lolv2_s_ssim = evaluate(model, lolv2_synthetic_dir, lolv2_synthetic_out, device)
    print(f"LOLv2 Synthetic -> PSNR: {lolv2_s_psnr:.4f} dB,  SSIM: {lolv2_s_ssim:.4f}")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
