"""
model.py — BioNAFNet Model Architecture (Student)
==================================================
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
