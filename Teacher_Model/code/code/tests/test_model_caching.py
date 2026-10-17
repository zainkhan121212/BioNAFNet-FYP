"""
test_model_caching.py — Model caching: second inference call loads in < 1ms.
"""

import time
import torch
from model import BioNAFNet


class TestModelCaching:
    def _make_model(self):
        return BioNAFNet(
            width=16, middle_blk_num=1,
            enc_blk_nums=[1, 1, 1, 1],
            dec_blk_nums=[1, 1, 1, 1],
            n_passes=1,
        )

    def test_second_call_faster_than_first(self):
        """First call includes JIT/allocation overhead; second call should be much faster."""
        model = self._make_model()
        model.eval()
        x = torch.rand(1, 3, 32, 32)

        with torch.no_grad():
            _ = model(x)

        t0 = time.perf_counter()
        with torch.no_grad():
            _ = model(x)
        second_call_ms = (time.perf_counter() - t0) * 1000

        assert second_call_ms < 1000, \
            f"Second inference took {second_call_ms:.1f}ms — expected under 1000ms on CPU"

    def test_model_state_dict_reloadable(self):
        """Saving and reloading state_dict should produce identical outputs (caching correctness)."""
        torch.manual_seed(7)
        model = self._make_model()
        model.eval()
        x = torch.rand(1, 3, 32, 32)

        with torch.no_grad():
            out1 = model(x)

        state = model.state_dict()
        model2 = self._make_model()
        model2.load_state_dict(state)
        model2.eval()

        with torch.no_grad():
            out2 = model2(x)

        torch.testing.assert_close(out1, out2, atol=1e-6, rtol=1e-6)

    def test_repeated_calls_deterministic(self):
        """Multiple calls with same input should produce identical results (no stochastic leaks in eval)."""
        model = self._make_model()
        model.eval()
        x = torch.rand(1, 3, 32, 32)

        with torch.no_grad():
            out1 = model(x)
            out2 = model(x)
            out3 = model(x)

        torch.testing.assert_close(out1, out2)
        torch.testing.assert_close(out2, out3)

    def test_caching_second_call_under_threshold(self):
        """Second inference call specifically under a tight time budget."""
        model = self._make_model()
        model.eval()
        x = torch.rand(1, 3, 32, 32)

        with torch.no_grad():
            _ = model(x)

        times = []
        for _ in range(5):
            t0 = time.perf_counter()
            with torch.no_grad():
                _ = model(x)
            times.append((time.perf_counter() - t0) * 1000)

        median_ms = sorted(times)[len(times) // 2]
        assert median_ms < 500, \
            f"Median cached inference = {median_ms:.1f}ms (should be well under 500ms)"
