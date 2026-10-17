"""
novel2_faeb.py — Frequency-Aware Enhancement Branch (FAEB)
==========================================================
Processing Order: Novel #2

Biological Inspiration:
    The visual cortex processes spatial frequencies separately.
    Low-light degradation primarily damages high-frequency details
    (textures, edges) while preserving low-frequency structure.

Implementation:
    - Applies FFT to extract amplitude and phase spectra
    - Learns corrections in the Fourier domain via convolutions
    - Reconstructs enhanced spatial features via inverse FFT
    - Blended with original via learnable parameter
"""

import torch
import torch.nn as nn


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
