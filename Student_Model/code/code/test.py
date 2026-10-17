"""
test.py — BioNAFNet Student Testing Entry Point
=================================================
Run this file to TEST / EVALUATE the trained student model.

Usage:
    python test.py
    python test.py --test_in /path/to/input --test_gt /path/to/gt --test_name MyData

Before running:
    1. Edit config.py to set your DATA_ROOT and checkpoint paths
    2. Make sure you have a trained model checkpoint (best.pth)
    3. Install requirements: pip install -r requirements.txt
"""

import argparse
import torch
from config import (
    WIDTH, ENC_BLKS, MIDDLE_BLK_NUM, DEC_BLKS, STUDENT_PASSES,
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_in", type=str, default=None)
    parser.add_argument("--test_gt", type=str, default=None)
    parser.add_argument("--test_name", type=str, default="LOLv1")
    parser.add_argument("--results_dir", type=str, default=None)
    args = parser.parse_args()

    seed_everything(42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = BioNAFNet(
        img_channel=3,
        width=WIDTH,
        middle_blk_num=MIDDLE_BLK_NUM,
        enc_blk_nums=ENC_BLKS,
        dec_blk_nums=DEC_BLKS,
        n_passes=STUDENT_PASSES,
    ).to(device)

    log(f"Starting evaluation on {device}...")
    avg_psnr, avg_ssim = test(
        model, device,
        test_in=args.test_in or TEST_INPUT_PATH,
        test_gt=args.test_gt or TEST_GT_PATH,
        test_name=args.test_name or TEST_NAME,
        results_dir=args.results_dir or OUTPUT_DIR,
    )
    log(f"Done! PSNR: {avg_psnr:.2f} dB | SSIM: {avg_ssim:.4f}")


if __name__ == "__main__":
    main()
