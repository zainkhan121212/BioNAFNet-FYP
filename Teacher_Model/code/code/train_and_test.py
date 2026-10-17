"""
train_and_test.py — BioNAFNet Full Pipeline (Train + Test)
==========================================================
Run this file to TRAIN the model and then automatically TEST it.

Usage:
    python train_and_test.py

Before running:
    1. Edit config.py to set your DATA_ROOT path
    2. Install requirements: pip install -r requirements.txt
"""

import torch
from config import WIDTH, ENC_BLKS, MIDDLE_BLK_NUM, DEC_BLKS, seed_everything, log
from model import BioNAFNet
from train_loop import train
from test_loop import test


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

    # Phase 1: Training
    log("=" * 70)
    log("PHASE 1: TRAINING")
    log("=" * 70)
    best_psnr = train(model, device)
    log(f"Training complete! Best PSNR: {best_psnr:.2f} dB")

    # Phase 2: Testing
    log("=" * 70)
    log("PHASE 2: TESTING")
    log("=" * 70)
    avg_psnr, avg_ssim = test(model, device)
    log(f"Final Results — PSNR: {avg_psnr:.2f} dB | SSIM: {avg_ssim:.4f}")


if __name__ == "__main__":
    main()
