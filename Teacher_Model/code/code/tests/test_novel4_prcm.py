"""
test_novel4_prcm.py — Unit tests for PRCM (Photoreceptor Response Curve Modeling).
"""

import torch
from novels.novel4_prcm import PhotoreceptorCurve


class TestPhotoreceptorCurve:
    def test_output_in_zero_one(self, rgb_tensor):
        model = PhotoreceptorCurve()
        out = model(rgb_tensor)
        assert out.min() >= 0.0 - 1e-6
        assert out.max() <= 1.0 + 1e-6

    def test_output_shape(self, rgb_tensor):
        model = PhotoreceptorCurve()
        out = model(rgb_tensor)
        assert out.shape == rgb_tensor.shape

    def test_output_is_finite(self, rgb_tensor):
        model = PhotoreceptorCurve()
        out = model(rgb_tensor)
        assert torch.isfinite(out).all()

    def test_all_zeros_input(self):
        """Near-black input should still produce valid output (clamped to 1e-5)."""
        model = PhotoreceptorCurve()
        x = torch.zeros(1, 3, 16, 16)
        out = model(x)
        assert torch.isfinite(out).all()
        assert out.min() >= 0.0

    def test_all_ones_input(self):
        model = PhotoreceptorCurve()
        x = torch.ones(1, 3, 16, 16)
        out = model(x)
        torch.testing.assert_close(out, torch.ones_like(out), atol=1e-4, rtol=1e-4)

    def test_learnable_parameters(self):
        model = PhotoreceptorCurve()
        assert model.rod_gamma.requires_grad
        assert model.cone_gamma.requires_grad
        assert model.threshold.requires_grad

    def test_gradient_flows(self):
        model = PhotoreceptorCurve()
        x = torch.rand(1, 3, 16, 16, requires_grad=True)
        out = model(x)
        loss = out.sum()
        loss.backward()
        assert x.grad is not None
