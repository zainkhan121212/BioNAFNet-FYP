"""
test_novel7_wfpl.py — Unit tests for WFPL (Weber-Fechner Perceptual Loss).
"""

import torch
from losses import WeberFechnerLoss


class TestWeberFechnerLoss:
    def test_loss_non_negative(self, rgb_pair):
        loss_fn = WeberFechnerLoss()
        pred, target = rgb_pair
        loss = loss_fn(pred, target)
        assert loss.item() >= 0.0

    def test_loss_is_finite(self, rgb_pair):
        loss_fn = WeberFechnerLoss()
        pred, target = rgb_pair
        loss = loss_fn(pred, target)
        assert torch.isfinite(loss)

    def test_identical_inputs_give_zero_loss(self):
        loss_fn = WeberFechnerLoss()
        x = torch.rand(2, 3, 16, 16)
        loss = loss_fn(x, x)
        assert loss.item() < 1e-6, f"Self-loss should be ~0, got {loss.item()}"

    def test_dark_regions_weighted_more(self):
        """Loss in dark regions should be amplified by 1/(lum + eps)."""
        loss_fn = WeberFechnerLoss(eps=0.02)
        dark_target = torch.full((1, 3, 8, 8), 0.05)
        bright_target = torch.full((1, 3, 8, 8), 0.9)
        pred_off = dark_target + 0.1
        loss_dark = loss_fn(pred_off, dark_target)
        pred_off_b = bright_target + 0.1
        loss_bright = loss_fn(pred_off_b, bright_target)
        assert loss_dark.item() > loss_bright.item(), \
            "Dark-region errors should produce larger loss"

    def test_gradient_flows(self):
        loss_fn = WeberFechnerLoss()
        pred = torch.rand(1, 3, 8, 8, requires_grad=True)
        target = torch.rand(1, 3, 8, 8)
        loss = loss_fn(pred, target)
        loss.backward()
        assert pred.grad is not None
