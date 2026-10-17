"""
novel6_tam.py — Temporal Adaptation Memory (TAM)
================================================
Processing Order: Novel #6

Biological Inspiration:
    The human visual system adapts over time when moving from bright
    to dark environments (dark adaptation). This is not instantaneous
    but involves progressive refinement as rod cells gradually
    increase sensitivity.

Implementation:
    - The model runs multiple forward passes (n_passes)
    - A GRU cell accumulates information across passes
    - Each pass refines the previous output progressively
    - Final output combines GRU-aggregated temporal information
"""

import torch
import torch.nn as nn


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
