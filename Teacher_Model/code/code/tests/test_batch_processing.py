"""
test_batch_processing.py — Batch IO: N images in -> N outputs out.
"""

import torch
from model import BioNAFNet


class TestBatchProcessing:
    def test_batch_size_preserved(self):
        """10 images in -> output batch dim = 10."""
        model = BioNAFNet(width=16, middle_blk_num=1,
                          enc_blk_nums=[1, 1, 1, 1],
                          dec_blk_nums=[1, 1, 1, 1],
                          n_passes=1)
        model.eval()
        batch = torch.rand(10, 3, 32, 32)
        with torch.no_grad():
            out = model(batch)
        assert out.shape[0] == 10, f"Expected batch=10, got {out.shape[0]}"

    def test_output_spatial_dims_match_input(self):
        model = BioNAFNet(width=16, middle_blk_num=1,
                          enc_blk_nums=[1, 1, 1, 1],
                          dec_blk_nums=[1, 1, 1, 1],
                          n_passes=1)
        model.eval()
        batch = torch.rand(4, 3, 48, 64)
        with torch.no_grad():
            out = model(batch)
        assert out.shape == (4, 3, 48, 64)

    def test_output_in_valid_range(self):
        model = BioNAFNet(width=16, middle_blk_num=1,
                          enc_blk_nums=[1, 1, 1, 1],
                          dec_blk_nums=[1, 1, 1, 1],
                          n_passes=1)
        model.eval()
        batch = torch.rand(2, 3, 32, 32)
        with torch.no_grad():
            out = model(batch)
        assert out.min() >= 0.0 - 1e-6
        assert out.max() <= 1.0 + 1e-6

    def test_single_image_batch(self):
        model = BioNAFNet(width=16, middle_blk_num=1,
                          enc_blk_nums=[1, 1, 1, 1],
                          dec_blk_nums=[1, 1, 1, 1],
                          n_passes=1)
        model.eval()
        x = torch.rand(1, 3, 32, 32)
        with torch.no_grad():
            out = model(x)
        assert out.shape == (1, 3, 32, 32)
