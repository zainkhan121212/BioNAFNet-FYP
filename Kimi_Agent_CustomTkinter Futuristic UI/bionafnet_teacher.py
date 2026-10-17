"""
bionafnet_teacher.py — Real BioNAFNet Teacher Model (154M parameters)
=====================================================================
Imports the actual BioNAFNet architecture from:
  <BioNAFNet_or_bundle_root>/Teacher_Model/code/code/
Loads the trained checkpoint (epoch 476, PSNR 25.05 dB, ~2.47 GB).

``Teacher_Model`` must sit next to this folder's parent (same layout as on your dev PC
or inside ``NeonEnhancer_Portable`` on another laptop).
"""

import os
import sys
import numpy as np
import torch
from PIL import Image

# Parent of this file's folder = bundle root (BioNAFNet root or NeonEnhancer_Portable)
_BUNDLE_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
)

# ── Add the real model source to the import path ──
_TEACHER_CODE_DIR = os.path.join(_BUNDLE_ROOT, "Teacher_Model", "code", "code")
if _TEACHER_CODE_DIR not in sys.path:
    sys.path.insert(0, _TEACHER_CODE_DIR)

# Import the REAL architecture + config from the teacher folder
from model import BioNAFNet  # noqa: E402

# ── Teacher architecture config (matches Teacher_Model/code/code/config.py) ──
TEACHER_WIDTH       = 64
TEACHER_ENC_BLKS    = [2, 2, 4, 8]
TEACHER_MIDDLE_BLK  = 12
TEACHER_DEC_BLKS    = [2, 2, 2, 2]
TEACHER_PASSES      = 2

# ── Checkpoint paths ──
TEACHER_WEIGHTS = os.path.join(_BUNDLE_ROOT, "Teacher_Model", "checkpoints", "best.pth")

# Model cache to avoid reloading the 2.47GB file on every call
_teacher_model_cache = {}## will use on the line 85 to sotore the model eithout reeloading again and again


def run_bionafnet_teacher(image_path, device="cpu", gt_path=None):
    """
    Run the real 154M-parameter BioNAFNet Teacher model.

    Args:
        image_path: Absolute path to a low-light input image.
        device:     "cpu" or "cuda" (from the UI toggle).
        gt_path:    Optional ground truth path (unused during inference).

    Returns:
        Enhanced PIL Image.
    """
    dev = torch.device(device)  # Step 3a: Set device — either GPU ("cuda") or CPU

    # ── Load model (cached per device) ──
    # Step 3b: Check if model is already in memory — avoids reloading 2.47GB every time
    if device not in _teacher_model_cache:
        print(f"[BioNAFNet Teacher] Building 154M parameter model on {device}...")

        # Step 3c: Build the full Teacher model architecture with all novelties
        model = BioNAFNet(
            img_channel=3,          # RGB image — 3 colour channels (Red, Green, Blue)
            width=TEACHER_WIDTH,    # 64 feature channels per layer (controls model size — 154M params)
            middle_blk_num=TEACHER_MIDDLE_BLK,  # 12 blocks at the deepest bottleneck — where FAEB (Novelty 2) runs
            enc_blk_nums=TEACHER_ENC_BLKS,      # Encoder: 4 levels with [2,2,4,8] blocks — RLIN (Novelty 1) in each
            dec_blk_nums=TEACHER_DEC_BLKS,      # Decoder: 4 symmetric levels with [2,2,2,2] blocks to rebuild image
            n_passes=TEACHER_PASSES,             # 2 iterative passes through the network — TAM (Novelty 6)
        ).to(dev)  # Move the entire model to GPU or CPU

        # Step 3d: Load the trained weights from the saved checkpoint file
        if os.path.exists(TEACHER_WEIGHTS):
            print(f"[BioNAFNet Teacher Loading 2.47GB weights into memory. Please wait...")
            ckpt = torch.load(TEACHER_WEIGHTS, map_location=dev, weights_only=False)  # Load the .pth file
            weights = ckpt.get("ema", ckpt.get("model", ckpt))  # Prefer EMA weights if saved (more stable)
            model.load_state_dict(weights, strict=False)         # Fill the model with the trained numbers
            epoch = ckpt.get("epoch", "?")          # Which training epoch the checkpoint was saved at
            best  = ckpt.get("best_psnr", 0)        # The best PSNR score achieved during training
            print(f"[BioNAFNet Teacher] Loaded checkpoint: epoch {epoch}, PSNR {best:.2f} dB")
        else:
            print(f"[BioNAFNet Teacher] WARNING: Weights not found at {TEACHER_WEIGHTS}")

        model.eval()                            # Step 3e: Switch to inference mode (disables dropout, batchnorm updates)
        _teacher_model_cache[device] = model    # Step 3f: Cache the model so next call is instant

    model = _teacher_model_cache[device]  # Retrieve from cache if already loaded

    # ── Inference ──
    # Step 4: Open the uploaded image and convert to RGB (removes any alpha channel)
    img = Image.open(image_path).convert("RGB")

    # Step 4a: Convert from PIL image → PyTorch tensor the model can process
    inp = torch.from_numpy(
        np.array(img).astype(np.float32) / 255.0  # Normalise pixel values from [0-255] → [0.0-1.0]
    ).permute(2, 0, 1)   # Reorder from (Height, Width, Channels) → (Channels, Height, Width)
    inp = inp.unsqueeze(0)  # Add batch dimension: (C,H,W) → (1,C,H,W) — model expects a batch
    inp = inp.to(dev)       # Move tensor to GPU or CPU

    # Step 4b: Run image through the full BioNAFNet Teacher model — this is where all 7 novelties execute
    with torch.no_grad():                   # Disable gradient tracking (saves memory, faster inference)
        out = model(inp).clamp(0, 1)        # Forward pass → clamp output to valid [0,1] range,,,,there  to the forwrd of the  model.py

    # Step 4c: Convert output tensor back to a PIL image to display in the app
    out_np = (out.squeeze(0)               # Remove batch dimension: (1,C,H,W) → (C,H,W)
              .permute(1, 2, 0)            # Reorder back: (C,H,W) → (H,W,C)
              .cpu().numpy() * 255.0       # Move to CPU, convert to numpy, scale back to [0-255]
              ).clip(0, 255).astype(np.uint8)  # Clip and convert to integer pixel values
    return Image.fromarray(out_np)         # Return as PIL Image — the app displays this in the gallery
