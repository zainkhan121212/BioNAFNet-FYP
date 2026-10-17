"""
config.py — Configuration Constants, Logging, and Seed
=======================================================
Processing Order: #1 (loaded first by all other modules)

Contains all hyperparameters, data paths, directory setup,
the log() utility function, and seed_everything().
"""

import os
import time
import random
import numpy as np
import torch


# ── Hyperparameters ──
EPOCHS          = 1000
BATCH_SIZE      = 4
INIT_LR         = 2e-4
MIN_LR          = 1e-6
WEIGHT_DECAY    = 1e-4
GRAD_CLIP       = 0.5
EMA_DECAY       = 0.9995
USE_AMP         = True
ACCUM_STEPS     = 2           # Effective batch size = 4*2 = 8

# ── NAFNet Architecture Config ──
WIDTH           = 64          # Channel width (up from 32)
ENC_BLKS        = [2, 2, 4, 8]
MIDDLE_BLK_NUM  = 12
DEC_BLKS        = [2, 2, 2, 2]

# ── Progressive resizing (DISABLED - fixed at 128) ──
PATCH_SCHEDULE  = {0: 128}

# ── Data paths ──
DATA_ROOT       = r"c:\Users\GNG\Desktop\retinex former\Retinexformer-master\data"
LOLv1_TRAIN_IN  = os.path.join(DATA_ROOT, "LOLv1", "Train", "input")
LOLv1_TRAIN_GT  = os.path.join(DATA_ROOT, "LOLv1", "Train", "target")
LOLv1_TEST_IN   = os.path.join(DATA_ROOT, "LOLv1", "Test", "input")
LOLv1_TEST_GT   = os.path.join(DATA_ROOT, "LOLv1", "Test", "target")
LOLv2R_TRAIN_IN = os.path.join(DATA_ROOT, "LOLv2", "Real_captured", "Train", "Low")
LOLv2R_TRAIN_GT = os.path.join(DATA_ROOT, "LOLv2", "Real_captured", "Train", "Normal")
LOLv2S_TRAIN_IN = os.path.join(DATA_ROOT, "LOLv2", "Synthetic", "Train", "Low")
LOLv2S_TRAIN_GT = os.path.join(DATA_ROOT, "LOLv2", "Synthetic", "Train", "Normal")

# ── Output directories ──
SCRIPT_DIR      = os.path.dirname(os.path.abspath(__file__))
CKPT_DIR        = os.path.join(SCRIPT_DIR, "checkpoints")
RESULTS_DIR     = os.path.join(SCRIPT_DIR, "results")
LOG_FILE        = os.path.join(SCRIPT_DIR, "training_log.txt")
os.makedirs(CKPT_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

BEST_PATH       = os.path.join(CKPT_DIR, "best.pth")


def log(msg):
    """Timestamped logging to console and file."""
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def seed_everything(seed=42):
    """Fix all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
