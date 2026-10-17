"""
model.py — BioNAFNet Model Architecture
========================================
Processing Order: #4 (loaded by training.py and testing.py)

The main model class that assembles all 7 biological novelties
into an enhanced NAFNet backbone.

Pipeline: PRCM -> SPDP -> NAFNet(RLIN + FAEB + ARFP) -> TAM refinement
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

from novels import (
    luminance,
    FrequencyBranch,
    AdaptiveReceptiveField,
    PhotoreceptorCurve,
    DualPathway,
    TemporalAdaptation,
)
from nafnet_blocks import BioNAFBlock


class BioNAFNet(nn.Module):
    """
    NAFNet enhanced with 7 Biological Novelties.
    Pipeline: PRCM -> SPDP -> NAFNet(RLIN + FAEB + ARFP) -> TAM refinement
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
        """Single forward pass through NAFNet backbone — runs once per pass (called twice for Teacher)."""
        B, C, H, W = inp.shape                      # Store original image dimensions to crop back later
        inp_padded = self.check_image_size(inp)      # Pad image to be divisible by 16 (required by downsampling)

        x = self.intro(inp_padded)                   # First 3×3 conv: expand from 3 channels (RGB) → 64 feature channels
        encs = []                                    # List to store encoder outputs for skip connections
        for encoder, down in zip(self.encoders, self.downs):
            x = encoder(x)                           # Run through encoder blocks — RLIN (Novelty 1) fires here at each level
            encs.append(x)                           # Save this encoder output — will be reused later in decoder (skip connection)
            x = down(x)                              # Downsample: halve H and W, double channels (go deeper into U-Net)

        x = self.middle_blks(x)                      # Run through 12 middle bottleneck blocks — deepest part of the network
        x = self.faeb(x)                             # NOVELTY 2: FAEB fires — FFT frequency enhancement at the bottleneck

        for decoder, up, enc_skip in zip(self.decoders, self.ups, encs[::-1]):
            x = up(x)                                # Upsample: double H and W, halve channels (come back up the U-Net)
            x = x + enc_skip                         # Add skip connection — paste in matching encoder output to recover lost detail
            x = decoder(x)                           # Run through decoder blocks to refine reconstructed features

        # NOVEL 3: ARFP at final decoder level
        x = self.arfp(x, lum_map)                   # NOVELTY 3: ARFP fires — adaptive receptive field guided by brightness map

        x = self.ending(x)                           # Final 3×3 conv: collapse from 64 feature channels back to 3 (RGB)
        x = x + inp_padded                           # Residual learning: add original padded input (model only learns the correction/residual)
        return x[:, :, :H, :W]                       # Crop padding off — return image at original H × W size

    def forward(self, x):
        # Step 5a — NOVELTY 4: PRCM fires first
        # Simulates pupil dilation in darkness — applies a biological brightness curve to the raw input
        x_prcm = self.prcm(x)

        # Step 5b — NOVELTY 5: SPDP fires second
        # Splits input into rod pathway (dark/peripheral) and cone pathway (colour/central), then merges
        x_spdp = self.spdp(x_prcm)

        # Step 5c — Compute luminance map: a per-pixel brightness estimate used later by ARFP
        lum_map = luminance(x)                       # Shape: (B, 1, H, W) — single channel brightness map

        # Step 5d — Multi-pass refinement loop (Teacher runs this TWICE, Student only ONCE)
        pass_outputs = []                            # Collect outputs from each pass for TAM to aggregate
        current = x_spdp                             # First pass starts from the SPDP-processed input
        for p in range(self.n_passes):               # n_passes=2 for Teacher, n_passes=1 for Student
            out = self.forward_single(current, lum_map)  # Full U-Net pass: RLIN(1) + FAEB(2) + ARFP(3) all fire inside here
            out = out.clamp(0, 1)                    # Clamp output to valid pixel range [0.0, 1.0]
            pass_outputs.append(out)                 # Save this pass output
            current = out                            # Pass 2 takes Pass 1's enhanced output as its input — progressive refinement

        # Step 5e — NOVELTY 6: TAM fires last — aggregates both passes with GRU memory cell
        # Like eyes progressively adapting to darkness — Pass 2 refines what Pass 1 missed
        if self.n_passes > 2:
            final = self.tam(pass_outputs)           # TAM combines both pass outputs intelligently via GRU
        else:
            final = pass_outputs[-1]                 # Student model: only one pass, skip TAM aggregation

        return final.clamp(0, 1)                     # Return final enhanced image, clamped to [0, 1]

    def check_image_size(self, x):
        _, _, h, w = x.size()
        mod_pad_h = (self.padder_size - h % self.padder_size) % self.padder_size   # How many rows to pad
        mod_pad_w = (self.padder_size - w % self.padder_size) % self.padder_size   # How many cols to pad
        x = F.pad(x, (0, mod_pad_w, 0, mod_pad_h))  # Pad right and bottom edges only (doesn't shift image)
        return x

