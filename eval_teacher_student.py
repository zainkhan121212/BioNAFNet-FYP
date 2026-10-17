"""
eval_teacher_student.py — Evaluate Teacher & Student Models on LOLv1/v2
========================================================================
Tests both models on:
  - LOL v1  (15 test images)
  - LOL v2 Real  (100 test images)
  - LOL v2 Synthetic  (100 test images)

Saves enhanced images + per-image CSV + summary to:
  Teacher_Model/results/LOLv1/
  Teacher_Model/results/LOLv2_Real/
  Teacher_Model/results/LOLv2_Synthetic/
  Student_Model/results/LOLv1/
  Student_Model/results/LOLv2_Real/
  Student_Model/results/LOLv2_Synthetic/

Usage:
    python eval_teacher_student.py
"""

import os
import sys
import glob
import csv
import time
import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from skimage.metrics import structural_similarity as calc_ssim
from skimage.metrics import peak_signal_noise_ratio as calc_psnr

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
TEACHER_CODE    = os.path.join(BASE_DIR, "Teacher_Model", "code", "code")
STUDENT_CODE    = os.path.join(BASE_DIR, "Student_Model", "code", "code")
DATA_ROOT       = r"c:\Users\GNG\Desktop\retinex former\Retinexformer-master\data"

# Dataset test paths
DATASETS = {
    "LOLv1": {
        "input":  os.path.join(DATA_ROOT, "LOLv1", "Test", "input"),
        "target": os.path.join(DATA_ROOT, "LOLv1", "Test", "target"),
    },
    "LOLv2_Real": {
        "input":  os.path.join(DATA_ROOT, "LOLv2", "Real_captured", "Test", "Low"),
        "target": os.path.join(DATA_ROOT, "LOLv2", "Real_captured", "Test", "Normal"),
    },
    "LOLv2_Synthetic": {
        "input":  os.path.join(DATA_ROOT, "LOLv2", "Synthetic", "Test", "Low"),
        "target": os.path.join(DATA_ROOT, "LOLv2", "Synthetic", "Test", "Normal"),
    },
}

# Model configs
TEACHER_CFG = dict(
    name        = "Teacher",
    ckpt        = os.path.join(BASE_DIR, "Teacher_Model", "checkpoints", "best.pth"),
    results_dir = os.path.join(BASE_DIR, "Teacher_Model", "results"),
    width       = 64,
    middle_blks = 12,
    enc_blks    = [2, 2, 4, 8],
    dec_blks    = [2, 2, 2, 2],
    n_passes    = 2,
    code_dir    = TEACHER_CODE,
)

STUDENT_CFG = dict(
    name        = "Student",
    ckpt        = os.path.join(BASE_DIR, "Student_Model", "checkpoints", "best.pth"),
    results_dir = os.path.join(BASE_DIR, "Student_Model", "results"),
    width       = 32,
    middle_blks = 4,
    enc_blks    = [2, 2, 4, 8],
    dec_blks    = [2, 2, 2, 2],
    n_passes    = 1,
    code_dir    = STUDENT_CODE,
)


# ── Minimal Dataset ────────────────────────────────────────────────────────
class TestDataset(Dataset):
    def __init__(self, input_dir, target_dir):
        self.input_files  = sorted(glob.glob(os.path.join(input_dir,  "*.*")))
        self.target_files = sorted(glob.glob(os.path.join(target_dir, "*.*")))
        assert len(self.input_files) == len(self.target_files), (
            f"Mismatch: {len(self.input_files)} inputs vs "
            f"{len(self.target_files)} targets"
        )

    def __len__(self):
        return len(self.input_files)

    def __getitem__(self, idx):
        inp = np.array(Image.open(self.input_files[idx]).convert("RGB"),
                       dtype=np.float32) / 255.0
        tgt = np.array(Image.open(self.target_files[idx]).convert("RGB"),
                       dtype=np.float32) / 255.0
        # Align sizes if needed
        if inp.shape != tgt.shape:
            h = min(inp.shape[0], tgt.shape[0])
            w = min(inp.shape[1], tgt.shape[1])
            inp, tgt = inp[:h, :w], tgt[:h, :w]
        inp_t = torch.from_numpy(inp).permute(2, 0, 1).float()
        tgt_t = torch.from_numpy(tgt).permute(2, 0, 1).float()
        return inp_t, tgt_t


# ── Load model from its own code directory ─────────────────────────────────
def load_model(cfg, device):
    # Temporarily prepend the model's code dir so its local imports resolve
    code_dir = cfg["code_dir"]
    if code_dir in sys.path:
        sys.path.remove(code_dir)
    sys.path.insert(0, code_dir)

    # Force reload in case the other model's modules are already cached
    for mod_name in list(sys.modules.keys()):
        if mod_name in ("model", "nafnet_blocks", "novels") or \
           mod_name.startswith("novels.") or mod_name.startswith("model."):
            del sys.modules[mod_name]

    from model import BioNAFNet  # noqa: PLC0415  (dynamic import by design)

    model = BioNAFNet(
        img_channel   = 3,
        width         = cfg["width"],
        middle_blk_num= cfg["middle_blks"],
        enc_blk_nums  = cfg["enc_blks"],
        dec_blk_nums  = cfg["dec_blks"],
        n_passes      = cfg["n_passes"],
    ).to(device)

    ckpt_path = cfg["ckpt"]
    if not os.path.exists(ckpt_path):
        print(f"  [WARNING] Checkpoint not found: {ckpt_path}")
        print("  Running with random weights (metrics will be meaningless).")
        return model

    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    if "ema" in ckpt:
        model.load_state_dict(ckpt["ema"])
        epoch = ckpt.get("epoch", "?")
        psnr  = ckpt.get("best_psnr", 0.0)
        print(f"  Loaded EMA weights  — epoch {epoch}, recorded PSNR {psnr:.2f} dB")
    elif "model" in ckpt:
        model.load_state_dict(ckpt["model"])
        print(f"  Loaded model weights — epoch {ckpt.get('epoch', '?')}")
    else:
        model.load_state_dict(ckpt)
        print("  Loaded raw state-dict")

    return model


# ── Evaluate one model on one dataset ──────────────────────────────────────
def evaluate(model, device, dataset_name, ds_cfg, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    ds      = TestDataset(ds_cfg["input"], ds_cfg["target"])
    loader  = DataLoader(ds, batch_size=1, shuffle=False,
                         num_workers=2, pin_memory=True)

    model.eval()
    all_psnr, all_ssim, rows = [], [], []

    print(f"\n  {'─'*60}")
    print(f"  Dataset : {dataset_name}  ({len(ds)} images)")
    print(f"  Output  : {out_dir}")
    print(f"  {'─'*60}")

    with torch.no_grad():
        for i, (low, high) in enumerate(loader):
            low  = low.to(device, non_blocking=True)
            high = high.to(device, non_blocking=True)

            out     = model(low).clamp(0, 1)
            out_np  = out.squeeze().permute(1, 2, 0).cpu().numpy()
            high_np = high.squeeze().permute(1, 2, 0).cpu().numpy()

            p = calc_psnr(high_np, out_np, data_range=1.0)
            s = calc_ssim(high_np, out_np, data_range=1.0, channel_axis=2)
            all_psnr.append(p)
            all_ssim.append(s)

            # Save enhanced image
            fname = os.path.basename(ds.input_files[i])
            out_img = (out_np * 255).clip(0, 255).astype(np.uint8)
            Image.fromarray(out_img).save(os.path.join(out_dir, fname))

            rows.append({"filename": fname, "psnr": p, "ssim": s})
            print(f"  [{i+1:3d}/{len(ds)}] {fname:35s}  "
                  f"PSNR: {p:6.2f} dB   SSIM: {s:.4f}")

    avg_psnr = float(np.mean(all_psnr))
    avg_ssim = float(np.mean(all_ssim))

    # ── Save per-image CSV ─────────────────────────────────────────────────
    csv_path = os.path.join(out_dir, "metrics.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "psnr", "ssim"])
        writer.writeheader()
        writer.writerows(rows)
        writer.writerow({"filename": "AVERAGE",
                         "psnr": f"{avg_psnr:.4f}",
                         "ssim": f"{avg_ssim:.4f}"})

    print(f"\n  Average PSNR : {avg_psnr:.2f} dB")
    print(f"  Average SSIM : {avg_ssim:.4f}")
    print(f"  Metrics saved: {csv_path}")

    return avg_psnr, avg_ssim


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n{'='*70}")
    print(f"  BioNAFNet — Teacher vs Student Evaluation")
    print(f"  Device: {device}")
    print(f"{'='*70}")

    summary_rows = []

    for cfg in [TEACHER_CFG, STUDENT_CFG]:
        model_name = cfg["name"]
        print(f"\n{'='*70}")
        print(f"  MODEL: {model_name}")
        print(f"  Checkpoint: {cfg['ckpt']}")
        print(f"{'='*70}")

        model = load_model(cfg, device)

        for ds_name, ds_cfg in DATASETS.items():
            out_dir = os.path.join(cfg["results_dir"], ds_name)
            t0      = time.time()
            avg_psnr, avg_ssim = evaluate(model, device, ds_name, ds_cfg, out_dir)
            elapsed = time.time() - t0
            summary_rows.append({
                "model":    model_name,
                "dataset":  ds_name,
                "avg_psnr": f"{avg_psnr:.4f}",
                "avg_ssim": f"{avg_ssim:.4f}",
                "time_s":   f"{elapsed:.1f}",
            })

        del model
        torch.cuda.empty_cache()

    # ── Print & save overall summary ────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"  FINAL SUMMARY")
    print(f"{'='*70}")
    header = f"  {'Model':<12} {'Dataset':<22} {'PSNR (dB)':>10} {'SSIM':>8}  {'Time':>7}"
    print(header)
    print(f"  {'─'*60}")
    for r in summary_rows:
        print(f"  {r['model']:<12} {r['dataset']:<22} "
              f"{float(r['avg_psnr']):>10.4f} {float(r['avg_ssim']):>8.4f}  "
              f"{r['time_s']:>6}s")

    summary_csv = os.path.join(BASE_DIR, "eval_summary_teacher_student.csv")
    with open(summary_csv, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["model", "dataset", "avg_psnr", "avg_ssim", "time_s"])
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"\n  Summary CSV saved: {summary_csv}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
