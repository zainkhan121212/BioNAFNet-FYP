"""
test_novel3_arfp.py — Unit tests for ARFP (Adaptive Receptive Field Pooling).
"""

import torch
from novels.novel3_arfp import AdaptiveReceptiveField


class TestAdaptiveReceptiveField:
    def test_output_shape_matches_input(self):
        model = AdaptiveReceptiveField(ch=16)
        x = torch.rand(2, 16, 32, 32)
        lum = torch.rand(2, 1, 32, 32)
        out = model(x, lum)
        assert out.shape == x.shape

    def test_output_is_finite(self):
        model = AdaptiveReceptiveField(ch=16)
        x = torch.rand(2, 16, 32, 32)
        lum = torch.rand(2, 1, 32, 32)
        out = model(x, lum)
        assert torch.isfinite(out).all()

    def test_softmax_weights_sum_to_one(self):
        model = AdaptiveReceptiveField(ch=8)
        lum = torch.rand(2, 1, 16, 16)
        weights = model.gate(lum)
        sums = weights.sum(dim=1)
        torch.testing.assert_close(sums, torch.ones_like(sums), atol=1e-5, rtol=1e-5)

    def test_luminance_map_different_spatial_size(self):
        """ARFP interpolates lum_map to feature size — must handle mismatched dims."""
        model = AdaptiveReceptiveField(ch=8)
        x = torch.rand(1, 8, 32, 32)
        lum = torch.rand(1, 1, 64, 64)
        out = model(x, lum)
        assert out.shape == x.shape

    def test_three_kernels_exist(self):
        model = AdaptiveReceptiveField(ch=16)
        assert model.small.kernel_size == (3, 3)
        assert model.medium.kernel_size == (5, 5)
        assert model.large.kernel_size == (7, 7)

    def test_gradient_flows(self):
        model = AdaptiveReceptiveField(ch=8)
        x = torch.rand(1, 8, 16, 16, requires_grad=True)
        lum = torch.rand(1, 1, 16, 16)
        out = model(x, lum)
        loss = out.sum()
        loss.backward()
        assert x.grad is not None
