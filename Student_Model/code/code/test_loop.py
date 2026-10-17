"""
test_loop.py — Testing / Evaluation Loop (Internal Engine)
===========================================================
Processing Order: #9 (called by test.py)

DO NOT RUN THIS FILE DIRECTLY. Run test.py instead.

Contains:
  - test(): loads best checkpoint and evaluates on test set
"""

import os
import numpy as np
import torch
from torch.utils.data import DataLoader
from skimage.metrics import structural_similarity as calc_ssim
from skimage.metrics import peak_signal_noise_ratio as calc_psnr
from PIL import Image

from config import LOLv1_TEST_IN, LOLv1_TEST_GT, RESULTS_DIR, BEST_PATH, log
from dataset import LOLDataset
from train_loop import psnr_tensor


def test(model, device, test_in=None, test_gt=None, test_name="LOLv1", results_dir=None):
    if os.path.exists(BEST_PATH):
        ckpt = torch.load(BEST_PATH, map_location=device, weights_only=False)
        # Use EMA weights for best performance
        if "ema" in ckpt:
            model.load_state_dict(ckpt["ema"])
            log(f"Loaded EMA checkpoint: epoch {ckpt.get('epoch', '?')}, "
                f"PSNR {ckpt.get('best_psnr', 0):.2f} dB")
        else:
            model.load_state_dict(ckpt["model"])
            log(f"Loaded model checkpoint: epoch {ckpt.get('epoch', '?')}")
    else:
        log("WARNING: No checkpoint found. Running with random weights.")

    ti = test_in if test_in else LOLv1_TEST_IN
    tg = test_gt if test_gt else LOLv1_TEST_GT
    rd = results_dir if results_dir else RESULTS_DIR
    os.makedirs(rd, exist_ok=True)

    val_ds = LOLDataset(ti, tg, patch_size=None, augment=False)
    val_loader = DataLoader(val_ds, batch_size=1, shuffle=False, num_workers=2, pin_memory=True)

    model.eval()
    all_psnr, all_ssim = [], []

    log(f"\n{'='*70}")
    log(f"BioNAFNet — Testing on {test_name} ({len(val_ds)} images)")
    log(f"{'='*70}")

    with torch.no_grad():
        for i, (low, high) in enumerate(val_loader):
            low = low.to(device, non_blocking=True)
            high = high.to(device, non_blocking=True)

            # No AMP — full-res images can have non-power-of-2 dims
            out = model(low)
            out = out.clamp(0, 1)

            out_np = out.squeeze().permute(1, 2, 0).cpu().numpy()
            high_np = high.squeeze().permute(1, 2, 0).cpu().numpy()
            p = calc_psnr(high_np, out_np, data_range=1.0)
            s = calc_ssim(high_np, out_np, data_range=1.0, channel_axis=2)
            all_psnr.append(p)
            all_ssim.append(s)

            # Save enhanced image
            out_img = (out_np * 255).clip(0, 255).astype(np.uint8)
            fname = os.path.basename(val_ds.input_files[i])
            Image.fromarray(out_img).save(os.path.join(rd, fname))

            print(f"  {fname:30s} PSNR: {p:.2f} dB  SSIM: {s:.4f}")

    avg_psnr = np.mean(all_psnr)
    avg_ssim = np.mean(all_ssim)
    log(f"\n{'='*70}")
    log(f"Average PSNR: {avg_psnr:.2f} dB")
    log(f"Average SSIM: {avg_ssim:.4f}")
    log(f"Enhanced images saved to: {rd}")
    log(f"{'='*70}")

    return avg_psnr, avg_ssim
