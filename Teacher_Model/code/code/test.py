"""
test.py — BioNAFNet Testing Entry Point
========================================
Run this file to TEST / EVALUATE the trained model.

Usage:
    python test.py

Before running:
    1. Edit config.py to set your DATA_ROOT and checkpoint paths
    2. Make sure you have a trained model checkpoint (best.pth)
    3. Install requirements: pip install -r requirements.txt

To test on custom data, edit the paths below:
"""

import torch
from config import (
    WIDTH, ENC_BLKS, MIDDLE_BLK_NUM, DEC_BLKS,
    LOLv1_TEST_IN, LOLv1_TEST_GT, RESULTS_DIR,
    seed_everything, log,
)
from model import BioNAFNet
from test_loop import test


# ╔══════════════════════════════════════════════════════════════╗
# ║  EDIT THESE PATHS TO TEST ON YOUR OWN DATA                  ║
# ╚══════════════════════════════════════════════════════════════╝
TEST_INPUT_PATH = LOLv1_TEST_IN     # Path to low-light test images
TEST_GT_PATH    = LOLv1_TEST_GT     # Path to ground-truth test images
TEST_NAME       = "LOLv1"           # Name for logging
OUTPUT_DIR      = RESULTS_DIR       # Where to save enhanced images


def main():
    seed_everything(42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = BioNAFNet(
        img_channel=3,
        width=WIDTH,
        middle_blk_num=MIDDLE_BLK_NUM,
        enc_blk_nums=ENC_BLKS,
        dec_blk_nums=DEC_BLKS,
        n_passes=2,
    ).to(device)

    log(f"Starting evaluation on {device}...")
    avg_psnr, avg_ssim = test(
        model, device,
        test_in=TEST_INPUT_PATH,
        test_gt=TEST_GT_PATH,
        test_name=TEST_NAME,
        results_dir=OUTPUT_DIR,
    )
    log(f"Done! PSNR: {avg_psnr:.2f} dB | SSIM: {avg_ssim:.4f}")


if __name__ == "__main__":
    main()
