"""
bionafnet_ensemble.py — BioNAFNet Ensemble Model (Teacher + Student)
=====================================================================
Combines the full 154M Teacher and the distilled 24M Student by running
both models on the input and fusing their outputs with a weighted average.

Default fusion: 50/50 (simple average)
"""

import os
import sys
import numpy as np
from PIL import Image

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from bionafnet_teacher import run_bionafnet_teacher
from bionafnet_student import run_bionafnet_student


def run_bionafnet_ensemble(image_path: str, device: str = "cpu",
                           gt_path: str = None,
                           teacher_weight: float = 0.5) -> Image.Image:
    """
    BioNAFNet Ensemble — Teacher + Student weighted fusion.
    Runs both models independently, blends arrays, returns PIL.
    """
    student_weight = 1.0 - teacher_weight

    print(f"[BioNAFNet Ensemble]  Running Teacher + Student  "
          f"(T={teacher_weight:.0%} / S={student_weight:.0%})")

    teacher_result = run_bionafnet_teacher(image_path, device=device, gt_path=gt_path)
    student_result = run_bionafnet_student(image_path, device=device, gt_path=gt_path)

    t_arr = np.array(teacher_result).astype(np.float32)
    s_arr = np.array(student_result).astype(np.float32)

    fused = (teacher_weight * t_arr + student_weight * s_arr).clip(0, 255).astype(np.uint8)
    result = Image.fromarray(fused)

    print(f"[BioNAFNet Ensemble]  device={device}  image={os.path.basename(image_path)}  ✓")
    return result
