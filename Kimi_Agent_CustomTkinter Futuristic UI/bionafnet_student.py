"""
bionafnet_student.py — Real BioNAFNet Student Model (24M parameters)
=====================================================================
Imports the actual BioNAFNet architecture from:
  <BioNAFNet_or_bundle_root>/Student_Model/code/code/
Loads the trained checkpoint (epoch 693, PSNR 25.09 dB).

``Student_Model`` must sit next to this folder's parent (portable bundle or dev tree).
"""

import os
import sys
import numpy as np
import torch
from PIL import Image

_BUNDLE_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
)

# ── Add the real model source to the import path ──
_STUDENT_CODE_DIR = os.path.join(_BUNDLE_ROOT, "Student_Model", "code", "code")
if _STUDENT_CODE_DIR not in sys.path:
    sys.path.insert(0, _STUDENT_CODE_DIR)

# Import the REAL architecture + config from the student folder
from model import BioNAFNet  # noqa: E402

# ── Student architecture config (matches Student_Model/code/code/config.py) ──
STUDENT_WIDTH       = 32
STUDENT_ENC_BLKS    = [2, 2, 4, 8]
STUDENT_MIDDLE_BLK  = 4
STUDENT_DEC_BLKS    = [2, 2, 2, 2]
STUDENT_PASSES      = 1

# ── Checkpoint paths ──
STUDENT_WEIGHTS = os.path.join(_BUNDLE_ROOT, "Student_Model", "checkpoints", "best.pth")

# Model cache to avoid reloading on every call
_student_model_cache = {}


def run_bionafnet_student(image_path, device="cpu", gt_path=None):
    """
    Run the real 24M-parameter BioNAFNet Student model.

    Args:
        image_path: Absolute path to a low-light input image.
        device:     "cpu" or "cuda" (from the UI toggle).
        gt_path:    Optional ground truth path (unused during inference).

    Returns:
        Enhanced PIL Image.
    """
    dev = torch.device(device)

    # ── Load model (cached per device) ──
    if device not in _student_model_cache:
        print(f"[BioNAFNet Student] Building model on {device}...")
        model = BioNAFNet(
            img_channel=3,
            width=STUDENT_WIDTH,
            middle_blk_num=STUDENT_MIDDLE_BLK,
            enc_blk_nums=STUDENT_ENC_BLKS,
            dec_blk_nums=STUDENT_DEC_BLKS,
            n_passes=STUDENT_PASSES,
        ).to(dev)

        if os.path.exists(STUDENT_WEIGHTS):
            ckpt = torch.load(STUDENT_WEIGHTS, map_location=dev, weights_only=False)
            # Prefer EMA weights if available
            weights = ckpt.get("ema", ckpt.get("model", ckpt))
            model.load_state_dict(weights, strict=False)
            epoch = ckpt.get("epoch", "?")
            best  = ckpt.get("best_psnr", 0)
            print(f"[BioNAFNet Student] Loaded checkpoint: epoch {epoch}, PSNR {best:.2f} dB")
        else:
            print(f"[BioNAFNet Student] WARNING: Weights not found at {STUDENT_WEIGHTS}")

        model.eval()
        _student_model_cache[device] = model

    model = _student_model_cache[device]

    # ── Inference ──
    img = Image.open(image_path).convert("RGB")
    inp = torch.from_numpy(
        np.array(img).astype(np.float32) / 255.0
    ).permute(2, 0, 1).unsqueeze(0).to(dev)

    with torch.no_grad():
        out = model(inp).clamp(0, 1)

    out_np = (out.squeeze(0).permute(1, 2, 0).cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)
    return Image.fromarray(out_np)
