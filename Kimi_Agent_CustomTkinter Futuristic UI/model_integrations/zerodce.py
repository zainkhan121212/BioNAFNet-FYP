"""
Zero-DCE inference using the official code under Zero-DCE-master (unchanged).
Weights: place any .pth under weights/zero_dce/ (e.g. Epoch99.pth).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Optional

import numpy as np
import torch
from PIL import Image

from .paths import ui_root, weights_root

_ZERO_DCE_MODEL_FILE = (
    ui_root()
    / "Zero-DCE-master"
    / "Zero-DCE-master"
    / "Zero-DCE_code"
    / "model.py"
)

_net_cache = {}


def _load_arch_class():
    if not _ZERO_DCE_MODEL_FILE.is_file():
        raise FileNotFoundError(
            f"Zero-DCE model.py not found at {_ZERO_DCE_MODEL_FILE}"
        )
    spec = importlib.util.spec_from_file_location(
        "_zero_dce_user_model", _ZERO_DCE_MODEL_FILE
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.enhance_net_nopool


def _resolve_weights() -> Path:
    d = weights_root() / "zero_dce"
    if d.is_dir():
        for name in ("Epoch99.pth", "zero_dce.pth", "weights.pth"):
            p = d / name
            if p.is_file():
                return p
        pths = sorted(d.glob("*.pth"))
        if pths:
            return pths[0]
    p = weights_root() / "zero_dce.pth"
    if p.is_file():
        return p
    raise FileNotFoundError(
        "No Zero-DCE weights found. Place a .pth in weights/zero_dce/ "
        "(see weights/README.txt)."
    )


def enhance_zerodce(*, image_path: str, device: str = "cpu", gt_path: Optional[str] = None) -> Image.Image:
    _ = gt_path
    dev = torch.device(device if device in ("cpu", "cuda") else "cpu")
    wp = _resolve_weights()
    cache_key = (str(wp.resolve()), str(dev))
    if cache_key not in _net_cache:
        Net = _load_arch_class()
        net = Net().to(dev)
        try:
            state = torch.load(wp, map_location=dev, weights_only=False)
        except TypeError:
            state = torch.load(wp, map_location=dev)
        net.load_state_dict(state)
        net.eval()
        _net_cache[cache_key] = net
    net = _net_cache[cache_key]

    pil = Image.open(image_path).convert("RGB")
    arr = np.asarray(pil).astype(np.float32) / 255.0
    t = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0).to(dev)

    with torch.no_grad():
        _, enhanced, _ = net(t)
    enhanced = enhanced.clamp(0, 1).squeeze(0).permute(1, 2, 0).detach().cpu().numpy()
    out = (enhanced * 255.0).clip(0, 255).astype(np.uint8)
    return Image.fromarray(out)
