"""
model_hooks.py — Model inference dispatch for the UI
======================================================
Each function accepts (image_path, device) and returns a PIL Image.

device will be "cpu" or "cuda" based on the UI hardware toggle.
"""

from PIL import Image

# BioNAFNet models
from bionafnet_teacher import run_bionafnet_teacher
from bionafnet_student import run_bionafnet_student

# External model integrations (see model_integrations/)
from model_integrations.retinexformer import enhance_retinexformer
from model_integrations.zerodce import enhance_zerodce


# ═══════════════════════════════════════════════════════════════════
#  UNSUPERVISED / ZERO-REFERENCE MODELS  (No ground truth needed)
# ═══════════════════════════════════════════════════════════════════

def run_zerodce(image_path: str, device: str = "cpu") -> Image.Image:
    """
    Zero-DCE  —  Zero-Reference Deep Curve Estimation
    --------------------------------------------------
    Code  : Zero-DCE-master/Zero-DCE-master/Zero-DCE_code/
    Weights: weights/zero_dce/*.pth
    """
    return enhance_zerodce(image_path=image_path, device=device)


def run_retinexformer(image_path: str, device: str = "cpu",
                      gt_path: str = None) -> Image.Image:
    """
    Retinexformer  —  One-stage Retinex-based Transformer
    -------------------------------------------------------
    Code  : Retinexformer_Repo/
    Weights: weights/retinexformer/*.pth
    Optional YAML (must match checkpoint): weights/retinexformer/opt.yml
    """
    return enhance_retinexformer(image_path=image_path, device=device, gt_path=gt_path)


# ═══════════════════════════════════════════════════════════════════
#  SUPERVISED MODELS  (Require ground truth for evaluation/training)
# ═══════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════
#  MODEL REGISTRY  —  used by the UI to dispatch calls
# ═══════════════════════════════════════════════════════════════════

UNSUPERVISED_MODELS = {
    "Zero-DCE":           {"fn": run_zerodce,           "icon": "\u26a1", "desc": "Zero-Reference Deep Curve Estimation\n(weights: weights/zero_dce/)"},
    "Retinexformer":      {"fn": run_retinexformer,     "icon": "\U0001f31f", "desc": "One-stage Retinex Transformer\n(weights: weights/retinexformer/)"},
    "BioNAFNet Teacher":  {"fn": run_bionafnet_teacher, "icon": "\U0001f9ec", "desc": "Full 154M param BioNAFNet\n(real model, , 25.05 dB)"},
    "BioNAFNet Student":  {"fn": run_bionafnet_student, "icon": "\U0001f9ec", "desc": "Distilled 24M param BioNAFNet\n(real model,  25.09 dB)"},
}

SUPERVISED_MODELS = {
    "Retinexformer":      {"fn": run_retinexformer,     "icon": "\U0001f31f", "desc": "One-stage Retinex Transformer\n(self-ensemble, works with GT eval)"},
    "BioNAFNet Teacher":  {"fn": run_bionafnet_teacher, "icon": "\U0001f9ec", "desc": "Full 154M param BioNAFNet\n(real model, eval with GT metrics)"},
    "BioNAFNet Student":  {"fn": run_bionafnet_student, "icon": "\U0001f9ec", "desc": "Distilled 24M param BioNAFNet\n(real model, eval with GT metrics)"},
}

ALL_MODELS = {**UNSUPERVISED_MODELS, **SUPERVISED_MODELS}
