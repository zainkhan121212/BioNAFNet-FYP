"""
train.py — BioNAFNet Training Entry Point
==========================================
Run this file to TRAIN the model.

Usage:
    python train.py

Before running:
    1. Edit config.py to set your DATA_ROOT path
    2. Install requirements: pip install -r requirements.txt
"""

import torch
from config import WIDTH, ENC_BLKS, MIDDLE_BLK_NUM, DEC_BLKS, seed_everything, log
from model import BioNAFNet
from train_loop import train


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

    log(f"Starting training on {device}...")
    best_psnr = train(model, device)
    log(f"Training finished! Best PSNR: {best_psnr:.2f} dB")


if __name__ == "__main__":
    main()
