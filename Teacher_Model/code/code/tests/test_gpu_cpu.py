"""
test_gpu_cpu.py — GPU matches CPU: same input -> similar outputs on both devices.
"""

import pytest
import torch
from model import BioNAFNet


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
class TestGPUvsCPU:
    def _make_model(self):
        return BioNAFNet(
            width=16, middle_blk_num=1,
            enc_blk_nums=[1, 1, 1, 1],
            dec_blk_nums=[1, 1, 1, 1],
            n_passes=1,
        )

    def test_outputs_match(self):
        torch.manual_seed(99)
        model = self._make_model()
        model.eval()

        x = torch.rand(1, 3, 32, 32)

        with torch.no_grad():
            cpu_out = model(x)

        model_gpu = self._make_model()
        model_gpu.load_state_dict(model.state_dict())
        model_gpu.eval().cuda()

        with torch.no_grad():
            gpu_out = model_gpu(x.cuda())

        torch.testing.assert_close(
            cpu_out, gpu_out.cpu(),
            atol=1e-3, rtol=1e-3,
        )

    def test_output_shapes_match(self):
        torch.manual_seed(99)
        model = self._make_model()
        model.eval()

        x = torch.rand(2, 3, 32, 32)

        with torch.no_grad():
            cpu_out = model(x)

        model_gpu = self._make_model()
        model_gpu.load_state_dict(model.state_dict())
        model_gpu.eval().cuda()

        with torch.no_grad():
            gpu_out = model_gpu(x.cuda())

        assert cpu_out.shape == gpu_out.shape
