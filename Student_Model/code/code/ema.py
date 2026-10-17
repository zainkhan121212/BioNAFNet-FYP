"""
ema.py — Exponential Moving Average (EMA) Helper
=================================================
Processing Order: #7 (loaded by training.py)

Maintains a shadow copy of model weights for stable validation.
"""

import copy
import torch


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
