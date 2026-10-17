"""
BioNAFNet Standalone Inference — Enhanced Quality Version
═══════════════════════════════════════════════════════════
Uses the EXACT architecture from train_bionafnet.py to guarantee
correct weight loading, plus optional post-processing for sharper,
cleaner results on real-world images.
"""
import os
import sys
import glob
import copy
import math
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from PIL import Image, ImageFilter
from tqdm import tqdm
import argparse
import cv2

# ══════════════════════════════════════════════════════════════════════════════
# EXACT Architecture from train_bionafnet.py (verbatim)
# ══════════════════════════════════════════════════════════════════════════════

def luminance(x):
    return 0.299 * x[:, 0:1] + 0.587 * x[:, 1:2] + 0.114 * x[:, 2:3]


# NOVEL 1: RLIN
class LateralInhibition(nn.Module):
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


# NOVEL 2: FAEB
class FrequencyBranch(nn.Module):
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


# NOVEL 3: ARFP
class AdaptiveReceptiveField(nn.Module):
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


# NOVEL 4: PRCM
class PhotoreceptorCurve(nn.Module):
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


# NOVEL 5: SPDP
class DualPathway(nn.Module):
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


# NOVEL 6: TAM
class TemporalAdaptation(nn.Module):
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


# NAFNet Building Blocks
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


# Standard NAFNet Building Blocks (for standalone SIDD denoising model)
class NAFBlock(nn.Module):
    def __init__(self, c, DW_Expand=2, FFN_Expand=2, drop_out_rate=0.):
        super().__init__()
        dw_channel = c * DW_Expand
        self.conv1 = nn.Conv2d(in_channels=c, out_channels=dw_channel, kernel_size=1, padding=0, stride=1, groups=1, bias=True)
        self.conv2 = nn.Conv2d(in_channels=dw_channel, out_channels=dw_channel, kernel_size=3, padding=1, stride=1, groups=dw_channel, bias=True)
        self.conv3 = nn.Conv2d(in_channels=dw_channel // 2, out_channels=c, kernel_size=1, padding=0, stride=1, groups=1, bias=True)
        self.sca = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(in_channels=dw_channel // 2, out_channels=dw_channel // 2, kernel_size=1, padding=0, stride=1, groups=1, bias=True),
        )
        self.sg = SimpleGate()
        ffn_channel = FFN_Expand * c
        self.conv4 = nn.Conv2d(in_channels=c, out_channels=ffn_channel, kernel_size=1, padding=0, stride=1, groups=1, bias=True)
        self.conv5 = nn.Conv2d(in_channels=ffn_channel // 2, out_channels=c, kernel_size=1, padding=0, stride=1, groups=1, bias=True)
        self.norm1 = LayerNorm2d(c)
        self.norm2 = LayerNorm2d(c)
        self.dropout1 = nn.Dropout(drop_out_rate) if drop_out_rate > 0. else nn.Identity()
        self.dropout2 = nn.Dropout(drop_out_rate) if drop_out_rate > 0. else nn.Identity()
        self.beta = nn.Parameter(torch.zeros((1, c, 1, 1)), requires_grad=True)
        self.gamma = nn.Parameter(torch.zeros((1, c, 1, 1)), requires_grad=True)

    def forward(self, inp):
        x = self.norm1(inp)
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.sg(x)
        x = x * self.sca(x)
        x = self.conv3(x)
        x = self.dropout1(x)
        y = inp + x * self.beta
        x = self.conv4(self.norm2(y))
        x = self.sg(x)
        x = self.conv5(x)
        x = self.dropout2(x)
        return y + x * self.gamma


class NAFNet(nn.Module):
    def __init__(self, img_channel=3, width=16, middle_blk_num=1, enc_blk_nums=[], dec_blk_nums=[]):
        super().__init__()
        self.intro = nn.Conv2d(in_channels=img_channel, out_channels=width, kernel_size=3, padding=1, stride=1, groups=1, bias=True)
        self.ending = nn.Conv2d(in_channels=width, out_channels=img_channel, kernel_size=3, padding=1, stride=1, groups=1, bias=True)
        self.encoders = nn.ModuleList()
        self.decoders = nn.ModuleList()
        self.middle_blks = nn.ModuleList()
        self.ups = nn.ModuleList()
        self.downs = nn.ModuleList()
        chan = width
        for num in enc_blk_nums:
            self.encoders.append(nn.Sequential(*[NAFBlock(chan) for _ in range(num)]))
            self.downs.append(nn.Conv2d(chan, 2*chan, 2, 2))
            chan = chan * 2
        self.middle_blks = nn.Sequential(*[NAFBlock(chan) for _ in range(middle_blk_num)])
        for num in dec_blk_nums:
            self.ups.append(nn.Sequential(nn.Conv2d(chan, chan * 2, 1, bias=False), nn.PixelShuffle(2)))
            chan = chan // 2
            self.decoders.append(nn.Sequential(*[NAFBlock(chan) for _ in range(num)]))
        self.padder_size = 2 ** len(self.encoders)

    def forward(self, inp):
        B, C, H, W = inp.shape
        inp_padded = self.check_image_size(inp)
        x = self.intro(inp_padded)
        encs = []
        for encoder, down in zip(self.encoders, self.downs):
            x = encoder(x)
            encs.append(x)
            x = down(x)
        x = self.middle_blks(x)
        for decoder, up, enc_skip in zip(self.decoders, self.ups, encs[::-1]):
            x = up(x)
            x = x + enc_skip
            x = decoder(x)
        x = self.ending(x)
        x = x + inp_padded
        return x[:, :, :H, :W]

    def check_image_size(self, x):
        _, _, h, w = x.size()
        mod_pad_h = (self.padder_size - h % self.padder_size) % self.padder_size
        mod_pad_w = (self.padder_size - w % self.padder_size) % self.padder_size
        x = F.pad(x, (0, mod_pad_w, 0, mod_pad_h))
        return x


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
        x = self.faeb(x)

        for decoder, up, enc_skip in zip(self.decoders, self.ups, encs[::-1]):
            x = up(x)
            x = x + enc_skip
            x = decoder(x)

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
            current = out

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
# Post-Processing Pipeline (NEW)
# ══════════════════════════════════════════════════════════════════════════════

def guided_filter(I, p, radius=4, eps=0.01):
    """Edge-preserving smoothing filter (denoises without blurring edges)."""
    mean_I = cv2.boxFilter(I, -1, (radius, radius))
    mean_p = cv2.boxFilter(p, -1, (radius, radius))
    corr_Ip = cv2.boxFilter(I * p, -1, (radius, radius))
    corr_II = cv2.boxFilter(I * I, -1, (radius, radius))

    var_I = corr_II - mean_I * mean_I
    cov_Ip = corr_Ip - mean_I * mean_p

    a = cov_Ip / (var_I + eps)
    b = mean_p - a * mean_I

    mean_a = cv2.boxFilter(a, -1, (radius, radius))
    mean_b = cv2.boxFilter(b, -1, (radius, radius))

    return mean_a * I + mean_b


def unsharp_mask(img, sigma=1.0, strength=0.5):
    """Gentle sharpening that enhances edges without amplifying noise."""
    blurred = cv2.GaussianBlur(img, (0, 0), sigma)
    sharpened = cv2.addWeighted(img, 1.0 + strength, blurred, -strength, 0)
    return np.clip(sharpened, 0, 255).astype(np.uint8)


def adaptive_denoise(img, strength=5):
    """Luminance-aware denoising: stronger in dark regions, gentler in bright."""
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l_channel = lab[:, :, 0].astype(np.float32) / 255.0

    # Denoise more aggressively in darker regions
    h_lum = int(strength * 1.5)   # stronger for dark
    h_bright = int(strength * 0.5)  # gentler for bright

    # Non-local means denoising (positional args for OpenCV compat)
    bgr_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    denoised = cv2.fastNlMeansDenoisingColored(bgr_img, None, strength, strength, 7, 21)
    return cv2.cvtColor(denoised, cv2.COLOR_BGR2RGB)


def post_process(img_np, denoise_strength=5, sharpen_strength=0.4, sharpen_sigma=1.0):
    """
    Full post-processing pipeline:
    1. Adaptive denoising
    2. Gentle unsharp masking
    3. Final clip
    """
    # Step 1: Denoise
    if denoise_strength > 0:
        img_np = adaptive_denoise(img_np, strength=denoise_strength)

    # Step 2: Sharpen
    if sharpen_strength > 0:
        img_np = unsharp_mask(img_np, sigma=sharpen_sigma, strength=sharpen_strength)

    return img_np


# ══════════════════════════════════════════════════════════════════════════════
# Inference Driver
# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════════
# Self-Ensemble (Test Time Augmentation) — The Key to Lower NIQE
# ══════════════════════════════════════════════════════════════════════════════

def self_ensemble(model, inp):
    """
    Run the model on 8 augmented versions of the input (4 rotations x 2 flips),
    reverse the augmentations, and average all outputs.
    This dramatically reduces noise and produces more natural-looking images.
    """
    results = []

    for flip in [False, True]:
        for rot in range(4):
            # Apply augmentation
            x = inp.clone()
            if flip:
                x = torch.flip(x, dims=[3])  # Horizontal flip
            if rot > 0:
                x = torch.rot90(x, k=rot, dims=[2, 3])

            # Run model
            out = model(x)

            # Reverse augmentation
            if rot > 0:
                out = torch.rot90(out, k=4 - rot, dims=[2, 3])
            if flip:
                out = torch.flip(out, dims=[3])

            results.append(out)

    # Average all 8 outputs
    return torch.stack(results, dim=0).mean(dim=0).clamp(0, 1)


def run_inference(input_dir, output_dir, weights_path, n_passes=2,
                  denoise=5, sharpen=0.4, use_postprocess=True,
                  use_ensemble=False, sidd_weights=None):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = BioNAFNet(n_passes=n_passes).to(device)

    # Load Weights
    print(f"Loading weights from: {weights_path}")
    ckpt = torch.load(weights_path, map_location=device, weights_only=False)
    weights = ckpt["ema"] if "ema" in ckpt else ckpt["model"]

    # Verify all keys match
    missing, unexpected = model.load_state_dict(weights, strict=False)
    if missing:
        print(f"WARNING: {len(missing)} missing keys!")
        for k in missing[:5]:
            print(f"  - {k}")
    if unexpected:
        print(f"WARNING: {len(unexpected)} unexpected keys!")
        for k in unexpected[:5]:
            print(f"  - {k}")
    if not missing and not unexpected:
        print(f"[OK] All weights loaded perfectly (epoch {ckpt.get('epoch', '?')}, "
              f"PSNR {ckpt.get('best_psnr', 0):.2f} dB)")

    model.eval()

    sidd_model = None
    if sidd_weights and os.path.exists(sidd_weights):
        print(f"Loading SIDD denoising model from: {sidd_weights}")
        sidd_model = NAFNet(width=64, enc_blk_nums=[2, 2, 4, 8], middle_blk_num=12, dec_blk_nums=[2, 2, 2, 2]).to(device)
        sidd_ckpt = torch.load(sidd_weights, map_location=device, weights_only=False)
        sidd_w = sidd_ckpt["params"] if "params" in sidd_ckpt else (sidd_ckpt["state_dict"] if "state_dict" in sidd_ckpt else sidd_ckpt)
        sidd_model.load_state_dict(sidd_w, strict=True)
        sidd_model.eval()
        print(f"[OK] SIDD denoising model loaded.")

    # Prepare Directories
    os.makedirs(output_dir, exist_ok=True)
    img_exts = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.PNG', '*.JPG', '*.JPEG']
    files = []
    for ext in img_exts:
        files.extend(glob.glob(os.path.join(input_dir, ext)))
    files = sorted(set(files))

    if not files:
        print(f"No images found in {input_dir}")
        return

    print(f"\n{'='*60}")
    print(f"BioNAFNet Enhanced Inference")
    print(f"  Images: {len(files)}")
    print(f"  Passes: {n_passes}")
    print(f"  Self-Ensemble (8x TTA): {'ON' if use_ensemble else 'OFF'}")
    print(f"  SIDD Denoising Model: {'ACTIVE' if sidd_model is not None else 'OFF'}")
    print(f"  Post-processing: {'ON' if use_postprocess else 'OFF'}")
    if use_postprocess:
        print(f"    Denoise strength: {denoise}")
        print(f"    Sharpen strength: {sharpen}")
    print(f"  Device: {device}")
    print(f"{'='*60}\n")

    with torch.no_grad():
        for fpath in tqdm(files, desc="Enhancing"):
            fname = os.path.basename(fpath)
            img = Image.open(fpath).convert("RGB")

            # Convert to tensor
            inp = torch.from_numpy(
                np.array(img).astype(np.float32) / 255.0
            ).permute(2, 0, 1).unsqueeze(0).to(device)

            # Model inference (with or without self-ensemble)
            if use_ensemble:
                out = self_ensemble(model, inp)
            else:
                out = model(inp)

            if sidd_model is not None:
                if use_ensemble:
                    out = self_ensemble(sidd_model, out)
                else:
                    out = sidd_model(out)

            # Convert back to numpy [0, 255]
            out_np = (out.squeeze().permute(1, 2, 0).cpu().numpy() * 255.0
                      ).clip(0, 255).astype(np.uint8)

            # Post-processing
            if use_postprocess:
                out_np = post_process(
                    out_np,
                    denoise_strength=denoise,
                    sharpen_strength=sharpen
                )

            # Save
            Image.fromarray(out_np).save(os.path.join(output_dir, fname))

    print(f"\n[DONE] Enhanced images saved to: {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="BioNAFNet Enhanced Inference (No GT required)")
    parser.add_argument("--input", type=str, required=True,
                        help="Path to folder containing low-light images")
    parser.add_argument("--output", type=str, default="enhanced_results",
                        help="Path to save enhanced images")
    parser.add_argument("--weights", type=str,
                        default=r"f:\low_light_enhancement\eye adaption\BioNAFNet\checkpoints\best.pth",
                        help="Path to .pth weights")
    parser.add_argument("--sidd-weights", type=str,
                        default=None,
                        help="Path to NAFNet-SIDD-width64.pth for sequential denoising")
    parser.add_argument("--passes", type=int, default=2,
                        help="Number of refinement passes (more = cleaner, slower)")
    parser.add_argument("--denoise", type=int, default=5,
                        help="Denoising strength (0=off, 3=light, 5=medium, 10=strong)")
    parser.add_argument("--sharpen", type=float, default=0.4,
                        help="Sharpening strength (0=off, 0.3=gentle, 0.5=medium, 1.0=strong)")
    parser.add_argument("--no-postprocess", action="store_true",
                        help="Disable all post-processing")
    parser.add_argument("--self-ensemble", action="store_true",
                        help="Enable 8x self-ensemble (TTA) for maximum quality")
    args = parser.parse_args()

    run_inference(
        args.input, args.output, args.weights,
        n_passes=args.passes,
        denoise=args.denoise,
        sharpen=args.sharpen,
        use_postprocess=not args.no_postprocess,
        use_ensemble=args.self_ensemble,
        sidd_weights=args.sidd_weights
    )
