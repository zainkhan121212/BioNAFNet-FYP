"""
test_luminance_utils.py — Unit tests for luminance() helper.
"""

import torch
from novels.luminance_utils import luminance


class TestLuminance:
    def test_output_shape(self, rgb_tensor):
        out = luminance(rgb_tensor)
        B, _, H, W = rgb_tensor.shape
        assert out.shape == (B, 1, H, W)

    def test_output_range_for_unit_input(self, rgb_tensor):
        out = luminance(rgb_tensor)
        assert out.min() >= 0.0
        assert out.max() <= 1.0

    def test_finite_values(self, rgb_tensor):
        out = luminance(rgb_tensor)
        assert torch.isfinite(out).all()

    def test_known_value_white(self):
        white = torch.ones(1, 3, 4, 4)
        out = luminance(white)
        torch.testing.assert_close(out, torch.ones(1, 1, 4, 4), atol=1e-5, rtol=1e-5)

    def test_known_value_black(self):
        black = torch.zeros(1, 3, 4, 4)
        out = luminance(black)
        torch.testing.assert_close(out, torch.zeros(1, 1, 4, 4), atol=1e-5, rtol=1e-5)
