"""
test_novel2_faeb.py — Unit tests for FAEB (Frequency-Aware Enhancement Branch).
"""

import torch
from novels.novel2_faeb import FrequencyBranch


class TestFrequencyBranch:
    def test_output_shape_matches_input(self):
        model = FrequencyBranch(ch=16)
        x = torch.rand(2, 16, 32, 32)
        out = model(x)
        assert out.shape == x.shape

    def test_output_is_finite(self):
        model = FrequencyBranch(ch=16)
        x = torch.rand(2, 16, 32, 32)
        out = model(x)
        assert torch.isfinite(out).all()

    def test_fft_roundtrip_identity(self):
        """Raw FFT -> iFFT should preserve the signal (module adds a learned residual)."""
        x = torch.rand(1, 8, 16, 16)
        fft = torch.fft.rfft2(x, norm="ortho")
        reconstructed = torch.fft.irfft2(fft, s=(16, 16), norm="ortho")
        torch.testing.assert_close(x, reconstructed, atol=1e-5, rtol=1e-5)

    def test_blend_parameter_exists(self):
        model = FrequencyBranch(ch=16)
        assert hasattr(model, "blend")
        assert model.blend.requires_grad

    def test_non_power_of_two_spatial_dims(self):
        """FAEB must work on non-power-of-2 spatial dims (the AMP guard handles this)."""
        model = FrequencyBranch(ch=8)
        x = torch.rand(1, 8, 17, 23)
        out = model(x)
        assert out.shape == x.shape
        assert torch.isfinite(out).all()

    def test_gradient_flows(self):
        model = FrequencyBranch(ch=8)
        x = torch.rand(1, 8, 16, 16, requires_grad=True)
        out = model(x)
        loss = out.sum()
        loss.backward()
        assert x.grad is not None
