import os
import time
import glob
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from skimage.metrics import structural_similarity as calc_ssim
from skimage.metrics import peak_signal_noise_ratio as calc_psnr

# Import architecture from our verified test script
from test_distilled import BioNAFNet, LOLDataset

# ══════════════════════════════════════════════════════════════════════════════
# Synergy Configuration
# ══════════════════════════════════════════════════════════════════════════════
# Weights for Fusion: 0.7 Teacher (Quality) + 0.3 Student (Efficiency)
ALPHA = 0.7 

# Data paths
DATA_ROOT       = r"c:\Users\GNG\Desktop\retinex former\Retinexformer-master\data"
DATASETS = {
    "LOLv1": {
        "in": os.path.join(DATA_ROOT, "LOLv1", "Test", "input"),
        "gt": os.path.join(DATA_ROOT, "LOLv1", "Test", "target")
    },
    "LOLv2_Real": {
        "in": os.path.join(DATA_ROOT, "LOLv2", "Real_captured", "Test", "Low"),
        "gt": os.path.join(DATA_ROOT, "LOLv2", "Real_captured", "Test", "Normal")
    },
    "LOLv2_Synthetic": {
        "in": os.path.join(DATA_ROOT, "LOLv2", "Synthetic", "Test", "Low"),
        "gt": os.path.join(DATA_ROOT, "LOLv2", "Synthetic", "Test", "Normal")
    }
}

# Checkpoint paths
TEACHER_CKPT    = r"f:\low_light_enhancement\eye adaption\BioNAFNet\checkpoints\latest.pth"
STUDENT_CKPT    = r"f:\low_light_enhancement\eye adaption\BioNAFNet\BioNAFNet_Distilled_Test\weights\best_student.pth"

def run_synergy_test():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"--- SYNERGY MODE ACTIVATED ---")
    print(f"Device: {device}")
    print(f"Fusion Weight (Alpha): {ALPHA} Teacher / {1-ALPHA:.1f} Student")

    # 1. Load Teacher (Heavy - 154M)
    print("Loading Teacher (154M params)...")
    teacher = BioNAFNet(width=64, middle_blk_num=12, n_passes=2).to(device)
    t_ckpt = torch.load(TEACHER_CKPT, map_location=device, weights_only=False)
    teacher.load_state_dict(t_ckpt.get("ema", t_ckpt.get("model")))
    teacher.eval()

    # 2. Load Student (Lite - 24M)
    print("Loading Student (24M params)...")
    student = BioNAFNet(width=32, middle_blk_num=4, n_passes=1).to(device)
    s_ckpt = torch.load(STUDENT_CKPT, map_location=device, weights_only=False)
    student.load_state_dict(s_ckpt.get("ema", s_ckpt.get("model")))
    student.eval()

    for d_name, d_paths in DATASETS.items():
        if not os.path.exists(d_paths["in"]):
            print(f"Skipping {d_name}: path not found.")
            continue
            
        print(f"\nTesting Synergy on {d_name}...")
        results_dir = os.path.join("results_synergy", d_name)
        os.makedirs(results_dir, exist_ok=True)

        test_ds = LOLDataset(d_paths["in"], d_paths["gt"])
        loader = DataLoader(test_ds, batch_size=1, shuffle=False)

        all_psnr, all_ssim = [], []
        start_time = time.time()
        with torch.no_grad():
            for i, (low, high) in enumerate(loader):
                if low.shape != high.shape: continue
                low, high = low.to(device), high.to(device)
                
                # --- The Synergy Loop ---
                t_out = teacher(low)
                s_out = student(low)
                
                # Weighted Fusion
                final_out = (ALPHA * t_out) + ((1 - ALPHA) * s_out)
                final_out = final_out.clamp(0, 1)
                # ------------------------

                out_np = final_out.squeeze().permute(1, 2, 0).cpu().numpy()
                high_np = high.squeeze().permute(1, 2, 0).cpu().numpy()
                
                p = calc_psnr(high_np, out_np, data_range=1.0)
                s = calc_ssim(high_np, out_np, data_range=1.0, channel_axis=2)
                all_psnr.append(p); all_ssim.append(s)
                
                # Save
                fname = os.path.basename(test_ds.input_files[i])
                Image.fromarray((out_np * 255).astype(np.uint8)).save(os.path.join(results_dir, fname))
                
                if (i+1) % 20 == 0 or i == 0:
                    print(f"  [{i+1}/{len(test_ds)}] Synergy PSNR: {p:.2f} dB")

        total_time = time.time() - start_time
        print("-" * 30)
        print(f"SYNERGY RESULTS for {d_name}")
        print(f"Avg PSNR: {np.mean(all_psnr):.2f} dB")
        print(f"Avg SSIM: {np.mean(all_ssim):.4f}")
        print(f"Time: {total_time:.2f}s ({total_time/len(test_ds):.3f}s/img)")
        print("-" * 30)

if __name__ == "__main__":
    run_synergy_test()
