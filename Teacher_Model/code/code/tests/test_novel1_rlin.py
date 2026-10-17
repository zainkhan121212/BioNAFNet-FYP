"""
test_novel1_rlin.py — Unit tests for RLIN (Retinal Lateral Inhibition Network).
"""

import torch
from novels.novel1_rlin import LateralInhibition


class TestLateralInhibition:
    def test_output_shape_matches_input(self):
        model = LateralInhibition(ch=16)
        x = torch.rand(2, 16, 32, 32)
        out = model(x)
        assert out.shape == x.shape

    def test_output_is_finite(self):
        model = LateralInhibition(ch=16)
        x = torch.rand(2, 16, 32, 32)
        out = model(x)
        assert torch.isfinite(out).all()

    def test_center_surround_produces_bounded_output(self):
        torch.manual_seed(0)
        model = LateralInhibition(ch=16)
        x = torch.rand(2, 16, 32, 32)
        out = model(x)
        assert out.abs().max() < 100.0, "Output magnitude unexpectedly large"

    def test_zero_input_produces_near_zero(self):
        model = LateralInhibition(ch=8)
        x = torch.zeros(1, 8, 16, 16)
        out = model(x)
        assert out.abs().max() < 1.0, "Zero input should produce near-zero (only bias)"

    def test_alpha_parameter_exists(self):
        model = LateralInhibition(ch=16)
        assert hasattr(model, "alpha")
        assert model.alpha.requires_grad

    def test_gradient_flows(self):
        model = LateralInhibition(ch=8)
        x = torch.rand(1, 8, 16, 16, requires_grad=True)
        out = model(x)
        loss = out.sum()
        loss.backward()
        assert x.grad is not None
        assert x.grad.abs().sum() > 0
