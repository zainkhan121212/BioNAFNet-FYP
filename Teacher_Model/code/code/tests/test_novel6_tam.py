"""
test_novel6_tam.py — Unit tests for TAM (Temporal Adaptation Memory).
"""

import torch
from novels.novel6_tam import TemporalAdaptation


class TestTemporalAdaptation:
    def test_output_shape(self):
        model = TemporalAdaptation(ch=32)
        passes = [torch.rand(2, 3, 16, 16) for _ in range(2)]
        out = model(passes)
        assert out.shape == (2, 3, 16, 16)

    def test_output_is_finite(self):
        model = TemporalAdaptation(ch=32)
        passes = [torch.rand(2, 3, 16, 16) for _ in range(2)]
        out = model(passes)
        assert torch.isfinite(out).all()

    def test_hidden_state_dimensions_correct(self):
        """GRU hidden state must have shape [B*H*W, ch]."""
        ch = 32
        model = TemporalAdaptation(ch=ch)
        passes = [torch.rand(2, 3, 8, 8) for _ in range(3)]
        B, _, H, W = passes[0].shape
        hidden = torch.zeros(B * H * W, ch)
        for p in passes:
            feat = model.proj_in(p)
            feat = feat.permute(0, 2, 3, 1).reshape(B * H * W, -1)
            hidden = model.gru(feat, hidden)
        assert hidden.shape == (B * H * W, ch)

    def test_single_pass_input(self):
        """TAM should work even with a single pass (edge case)."""
        model = TemporalAdaptation(ch=32)
        passes = [torch.rand(1, 3, 8, 8)]
        out = model(passes)
        assert out.shape == (1, 3, 8, 8)
        assert torch.isfinite(out).all()

    def test_multiple_passes_refine(self):
        """Output with 3 passes should differ from 1 pass (GRU accumulates info)."""
        torch.manual_seed(42)
        model = TemporalAdaptation(ch=32)
        p1 = [torch.rand(1, 3, 8, 8)]
        p3 = [torch.rand(1, 3, 8, 8) for _ in range(3)]
        out1 = model(p1)
        out3 = model(p3)
        assert not torch.allclose(out1, out3)

    def test_gradient_flows(self):
        model = TemporalAdaptation(ch=16)
        x = torch.rand(1, 3, 8, 8, requires_grad=True)
        passes = [x, x.clone().detach()]
        out = model(passes)
        loss = out.sum()
        loss.backward()
        assert x.grad is not None
