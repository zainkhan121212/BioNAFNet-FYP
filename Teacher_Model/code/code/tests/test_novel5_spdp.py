"""
test_novel5_spdp.py — Unit tests for SPDP (Scotopic-Photopic Dual Pathway).
"""

import torch
from novels.novel5_spdp import DualPathway


class TestDualPathway:
    def test_output_shape(self, rgb_tensor):
        model = DualPathway(ch=32)
        out = model(rgb_tensor)
        assert out.shape == rgb_tensor.shape

    def test_output_is_finite(self, rgb_tensor):
        model = DualPathway(ch=32)
        out = model(rgb_tensor)
        assert torch.isfinite(out).all()

    def test_yuv_conversion_shapes(self):
        model = DualPathway(ch=16)
        rgb = torch.rand(2, 3, 16, 16)
        y, u, v = model.rgb_to_yuv(rgb)
        assert y.shape == (2, 1, 16, 16)
        assert u.shape == (2, 1, 16, 16)
        assert v.shape == (2, 1, 16, 16)

    def test_yuv_luminance_range(self):
        """Y channel for [0,1] RGB should be in [0,1]."""
        model = DualPathway(ch=16)
        rgb = torch.rand(4, 3, 8, 8)
        y, _, _ = model.rgb_to_yuv(rgb)
        assert y.min() >= -0.01
        assert y.max() <= 1.01

    def test_residual_scaling(self, rgb_tensor):
        """SPDP adds residual * 0.2, so output should be close to input."""
        model = DualPathway(ch=32)
        out = model(rgb_tensor)
        diff = (out - rgb_tensor).abs().max()
        assert diff < 2.0, "Residual too large — 0.2 * Tanh should keep it bounded"

    def test_gradient_flows(self):
        model = DualPathway(ch=16)
        x = torch.rand(1, 3, 16, 16, requires_grad=True)
        out = model(x)
        loss = out.sum()
        loss.backward()
        assert x.grad is not None
