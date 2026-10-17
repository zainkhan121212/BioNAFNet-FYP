"""
train_and_test.py — BioNAFNet Student Full Pipeline (Train + Test)
===================================================================
Run this file to TRAIN the student model and then automatically TEST it.

Usage:
    python train_and_test.py

Before running:
    1. Edit config.py to set your DATA_ROOT path and TEACHER_CKPT path
    2. Install requirements: pip install -r requirements.txt
    3. Ensure the Teacher model checkpoint exists
"""

import sys
import argparse
import torch
from config import (
    WIDTH, ENC_BLKS, MIDDLE_BLK_NUM, DEC_BLKS, STUDENT_PASSES,
    TEACHER_CKPT, seed_everything, log,
)
from model import BioNAFNet
from train_loop import train
from test_loop import test


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_passes", type=int, default=STUDENT_PASSES,
                        help="Number of iterative refinement passes (for TAM)")
    args = parser.parse_args()

    seed_everything(42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 1. Instantiate Teacher (Heavy Model)
    print(f"Loading Teacher Model from {TEACHER_CKPT}...")
    teacher_model = BioNAFNet(
        img_channel=3, width=64, middle_blk_num=12,
        enc_blk_nums=[2, 2, 4, 8], dec_blk_nums=[2, 2, 2, 2], n_passes=2
    ).to(device)

    import os
    if os.path.exists(TEACHER_CKPT):
        teacher_ckpt = torch.load(TEACHER_CKPT, map_location=device, weights_only=False)
        teacher_model.load_state_dict(teacher_ckpt.get("ema", teacher_ckpt.get("model")))
        print("[OK] Teacher Loaded.")
    else:
        print(f"ERROR: No Teacher model found at {TEACHER_CKPT}. Please ensure it exists.")
        sys.exit(1)

    teacher_model.eval()
    for param in teacher_model.parameters():
        param.requires_grad = False

    # 2. Instantiate Student (Lightweight Model)
    print("Instantiating Student Model (BioNAFNet-Lite)...")
    student_model = BioNAFNet(
        img_channel=3, width=WIDTH, middle_blk_num=MIDDLE_BLK_NUM,
        enc_blk_nums=ENC_BLKS, dec_blk_nums=DEC_BLKS, n_passes=args.n_passes
    ).to(device)

    # Phase 1: Training
    log("=" * 70)
    log("PHASE 1: DISTILLATION TRAINING")
    log("=" * 70)
    best_psnr = train(student_model, teacher_model, device)
    log(f"Training complete! Best PSNR: {best_psnr:.2f} dB")

    # Phase 2: Testing
    log("=" * 70)
    log("PHASE 2: TESTING")
    log("=" * 70)
    avg_psnr, avg_ssim = test(student_model, device)
    log(f"Final Results — PSNR: {avg_psnr:.2f} dB | SSIM: {avg_ssim:.4f}")


if __name__ == "__main__":
    main()
