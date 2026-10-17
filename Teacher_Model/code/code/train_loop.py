"""
train_loop.py — Training Loop (Internal Engine)
=================================================
Processing Order: #8 (called by train.py)

DO NOT RUN THIS FILE DIRECTLY. Run train.py instead.

Contains:
  - psnr_tensor(): quick PSNR computation on GPU tensors
  - get_patch_size(): progressive resizing schedule
  - train(): full training loop with validation, checkpointing, EMA
"""

import os
import math

import torch
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, ConcatDataset
from tqdm import tqdm
from skimage.metrics import structural_similarity as calc_ssim

from config import (
    EPOCHS, BATCH_SIZE, INIT_LR, MIN_LR, WEIGHT_DECAY, GRAD_CLIP,
    EMA_DECAY, USE_AMP, ACCUM_STEPS, WIDTH, ENC_BLKS, MIDDLE_BLK_NUM,
    DEC_BLKS, PATCH_SCHEDULE, LOLv1_TRAIN_IN, LOLv1_TRAIN_GT,
    LOLv1_TEST_IN, LOLv1_TEST_GT, LOLv2R_TRAIN_IN, LOLv2R_TRAIN_GT,
    LOLv2S_TRAIN_IN, LOLv2S_TRAIN_GT, CKPT_DIR, BEST_PATH, log, seed_everything,
)
from losses import TotalLoss
from dataset import LOLDataset
from ema import EMA


def psnr_tensor(pred, target):
    mse = F.mse_loss(pred.clamp(0, 1), target)
    if mse == 0:
        return 100.0
    return 10 * math.log10(1.0 / mse.item())


def get_patch_size(epoch):
    """Progressive resizing: start small, grow larger."""
    ps = 128
    for e, p in sorted(PATCH_SCHEDULE.items()):
        if epoch >= e:
            ps = p
    return ps


def train(model, device):
    seed_everything(42)

    total_params = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    log("=" * 70)
    log("BioNAFNet — Training on LOLv1 + LOLv2")
    log(f"Width: {WIDTH}, Enc: {ENC_BLKS}, Mid: {MIDDLE_BLK_NUM}, Dec: {DEC_BLKS}")
    log(f"Total params: {total_params:,}  |  Trainable: {trainable:,}")
    log(f"Device: {device}")
    log(f"Epochs: {EPOCHS}, LR: {INIT_LR}, Batch: {BATCH_SIZE}x{ACCUM_STEPS}")
    log(f"Progressive patches: {PATCH_SCHEDULE}")
    log("=" * 70)

    # Multi-dataset: LOLv1 + LOLv2Real + LOLv2Synthetic
    val_ds = LOLDataset(LOLv1_TEST_IN, LOLv1_TEST_GT, patch_size=None, augment=False)
    val_loader = DataLoader(val_ds, batch_size=1, shuffle=False,
                            num_workers=2, pin_memory=True)

    criterion = TotalLoss(device)
    optimizer = optim.AdamW(model.parameters(), lr=INIT_LR, weight_decay=WEIGHT_DECAY,
                            betas=(0.9, 0.999))
    scaler = torch.amp.GradScaler(enabled=USE_AMP)
    ema = EMA(model, decay=EMA_DECAY)

    # Cosine annealing with warm restarts
    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer, T_0=50, T_mult=2, eta_min=MIN_LR
    )

    best_psnr = 0.0
    nan_total = 0
    start_epoch = 0

    # Resume from checkpoint if exists
    latest_path = os.path.join(CKPT_DIR, "latest.pth")
    if os.path.exists(latest_path):
        ckpt = torch.load(latest_path, map_location=device, weights_only=False)
        model.load_state_dict(ckpt["model"])
        ema.shadow.load_state_dict(ckpt["ema"])
        optimizer.load_state_dict(ckpt["optimizer"])
        start_epoch = ckpt["epoch"]
        best_psnr = ckpt.get("best_psnr", 0)
        for _ in range(start_epoch):
            scheduler.step()
        log(f"Resumed from epoch {start_epoch}, best PSNR: {best_psnr:.2f} dB")

    for epoch in range(start_epoch, EPOCHS):
        ps = get_patch_size(epoch)

        train_datasets = []
        if os.path.isdir(LOLv1_TRAIN_IN):
            train_datasets.append(LOLDataset(LOLv1_TRAIN_IN, LOLv1_TRAIN_GT,
                                             patch_size=ps, augment=True))
        if os.path.isdir(LOLv2R_TRAIN_IN):
            train_datasets.append(LOLDataset(LOLv2R_TRAIN_IN, LOLv2R_TRAIN_GT,
                                             patch_size=ps, augment=True))
        if os.path.isdir(LOLv2S_TRAIN_IN):
            train_datasets.append(LOLDataset(LOLv2S_TRAIN_IN, LOLv2S_TRAIN_GT,
                                             patch_size=ps, augment=True))

        train_ds = ConcatDataset(train_datasets)
        train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,
                                  num_workers=4, pin_memory=True, drop_last=True,
                                  persistent_workers=True)

        if epoch == start_epoch:
            log(f"Training dataset: {len(train_ds)} images")
            log(f"Validation dataset: {len(val_ds)} images")

        model.train()
        running_loss = 0.0
        running_psnr = 0.0

        pbar = tqdm(train_loader, desc=f"E{epoch+1}/{EPOCHS} ps={ps}")
        optimizer.zero_grad(set_to_none=True)

        for step, (low, high) in enumerate(pbar, 1):
            low = low.to(device, non_blocking=True)
            high = high.to(device, non_blocking=True)

            with torch.amp.autocast(device_type=device.type, enabled=USE_AMP):
                out = model(low)
                loss, loss_dict = criterion(out, high)
                loss = loss / ACCUM_STEPS

            scaler.scale(loss).backward()

            if step % ACCUM_STEPS == 0:
                scaler.unscale_(optimizer)

                has_nan = any(
                    p.grad is not None and torch.isnan(p.grad).any()
                    for p in model.parameters()
                )
                if has_nan:
                    nan_total += 1
                    log(f"  [WARN] NaN grad at epoch {epoch+1}, step {step} (total: {nan_total})")
                    optimizer.zero_grad(set_to_none=True)
                    scaler.update()
                    continue

                torch.nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad(set_to_none=True)
                ema.update(model)

            running_loss += loss.item() * ACCUM_STEPS
            running_psnr += psnr_tensor(out.detach(), high)
            pbar.set_postfix(
                loss=f"{running_loss/step:.4f}",
                psnr=f"{running_psnr/step:.2f}",
                lr=f"{optimizer.param_groups[0]['lr']:.2e}"
            )

        scheduler.step()

        # Validate using EMA model
        ema.shadow.eval()
        vp, vs = 0.0, 0.0
        with torch.no_grad():
            for low, high in val_loader:
                low = low.to(device, non_blocking=True)
                high = high.to(device, non_blocking=True)
                out = ema.shadow(low)
                out = out.clamp(0, 1)
                vp += psnr_tensor(out, high)
                out_np = out.squeeze().permute(1, 2, 0).cpu().numpy()
                high_np = high.squeeze().permute(1, 2, 0).cpu().numpy()
                vs += calc_ssim(high_np, out_np, data_range=1.0, channel_axis=2)

        avg_vp = vp / len(val_loader)
        avg_vs = vs / len(val_loader)
        avg_tl = running_loss / len(train_loader)
        avg_tp = running_psnr / len(train_loader)
        lr = optimizer.param_groups[0]['lr']

        log(f"Epoch {epoch+1}/{EPOCHS} | Loss: {avg_tl:.4f} | Train PSNR: {avg_tp:.2f} | "
            f"Val PSNR: {avg_vp:.2f} dB | Val SSIM: {avg_vs:.4f} | "
            f"LR: {lr:.2e} | Patch: {ps} | Gap: {avg_tp - avg_vp:.2f}")

        if avg_vp > best_psnr:
            best_psnr = avg_vp
            torch.save({
                "epoch": epoch + 1,
                "model": model.state_dict(),
                "ema": ema.shadow.state_dict(),
                "optimizer": optimizer.state_dict(),
                "best_psnr": best_psnr,
            }, BEST_PATH)
            log(f"  *** New Best: {best_psnr:.2f} dB ***")

        # Save latest checkpoint (for resume)
        torch.save({
            "epoch": epoch + 1,
            "model": model.state_dict(),
            "ema": ema.shadow.state_dict(),
            "optimizer": optimizer.state_dict(),
            "best_psnr": best_psnr,
        }, os.path.join(CKPT_DIR, "latest.pth"))

        # Save periodic checkpoints
        if (epoch + 1) % 50 == 0:
            torch.save({
                "epoch": epoch + 1,
                "model": model.state_dict(),
                "ema": ema.shadow.state_dict(),
                "optimizer": optimizer.state_dict(),
                "best_psnr": best_psnr,
            }, os.path.join(CKPT_DIR, f"ckpt_{epoch+1}.pth"))

    log("=" * 70)
    log(f"Training Complete! Best Val PSNR: {best_psnr:.2f} dB")
    log("=" * 70)
    return best_psnr
