"""
Retinexformer inference using the repo under Retinexformer_Repo (unchanged).

Weights: place one or more .pth files under weights/retinexformer/
Optional: weights/retinexformer/opt.yml — YAML matching your checkpoint
          (if missing, Options/RetinexFormer_LOL_v1.yml is used).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

from .paths import ui_root, weights_root

_REPO = ui_root() / "Retinexformer_Repo"
_ENH = _REPO / "Enhancement"
_DEFAULT_OPT = _REPO / "Options" / "RetinexFormer_LOL_v1.yml"

_model_cache = {}


def _ensure_sys_path() -> None:
    for p in (_REPO, _ENH):
        s = str(p.resolve())
        if s not in sys.path:
            sys.path.insert(0, s)


def _pick_checkpoint_in_dir(folder: Path) -> Optional[Path]:
    if not folder.is_dir():
        return None
    for name in ("retinexformer.pth", "SDSD_indoor.pth", "weights.pth"):
        p = folder / name
        if p.is_file():
            return p
    cands = sorted(folder.glob("*.pth")) + sorted(folder.glob("*.pt"))
    return cands[0] if cands else None


def _resolve_weights_and_opt() -> tuple[Path, Path]:
    d = weights_root() / "retinexformer"
    w = _pick_checkpoint_in_dir(d)
    # Fallbacks if weights were put next to README but not in subfolder / wrong extension
    if w is None:
        for p in (
            weights_root() / "retinexformer.pth",
            weights_root() / "retinexformer.pt",
        ):
            if p.is_file():
                w = p
                break
    if w is None:
        expect = d.resolve()
        raise FileNotFoundError(
            "No Retinexformer weights found.\n\n"
            f"Put a checkpoint here (folder must exist): {expect}\n"
            "Use a .pth or .pt file (any name is fine if it is the only one in that folder).\n"
            "Folder name must be weights (with an s), then retinexformer — not weight/retinexformer.\n"
            "See weights/README.txt."
        )
    user_opt = d / "opt.yml"
    opt_path = user_opt if user_opt.is_file() else _DEFAULT_OPT
    if not opt_path.is_file():
        raise FileNotFoundError(f"Retinexformer option YAML not found: {opt_path}")
    return w, opt_path


def _build_model(weights: Path, opt_path: Path, device: str) -> torch.nn.Module:
    _ensure_sys_path()
    from basicsr.models import create_model  # noqa: WPS433 — after sys.path
    from basicsr.utils.options import parse  # noqa: WPS433

    opt = parse(str(opt_path), is_train=False)
    opt["dist"] = False
    opt["num_gpu"] = 0 if device == "cpu" else 1

    model = create_model(opt).net_g
    dev = torch.device(device if device in ("cpu", "cuda") else "cpu")
    try:
        ckpt = torch.load(weights, map_location=dev, weights_only=False)
    except TypeError:
        ckpt = torch.load(weights, map_location=dev)

    if isinstance(ckpt, dict) and "params" in ckpt:
        state = ckpt["params"]
    elif isinstance(ckpt, dict):
        state = ckpt
    else:
        state = ckpt

    try:
        model.load_state_dict(state, strict=True)
    except Exception:
        prefixed = {}
        for k, v in state.items():
            prefixed["module." + k if not k.startswith("module.") else k] = v
        try:
            model.load_state_dict(prefixed, strict=False)
        except Exception:
            model.load_state_dict(state, strict=False)

    model = model.to(dev)
    model.eval()
    return model


def enhance_retinexformer(
    *, image_path: str, device: str = "cpu", gt_path: Optional[str] = None
) -> Image.Image:
    _ = gt_path
    weights, opt_path = _resolve_weights_and_opt()
    dev_s = device if device in ("cpu", "cuda") else "cpu"
    cache_key = (
        str(weights.resolve()),
        str(opt_path.resolve()),
        dev_s,
    )
    if cache_key not in _model_cache:
        _model_cache[cache_key] = _build_model(weights, opt_path, dev_s)
    model = _model_cache[cache_key]
    dev = torch.device(dev_s)

    _ensure_sys_path()
    import utils as enh_utils  # noqa: WPS433 — Enhancement/utils.py

    img = np.float32(enh_utils.load_img(str(Path(image_path).resolve()))) / 255.0
    input_ = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0).to(dev)

    factor = 4
    _, _, h, w = input_.shape
    H = ((h + factor) // factor) * factor
    W = ((w + factor) // factor) * factor
    padh = H - h if h % factor != 0 else 0
    padw = W - w if w % factor != 0 else 0
    input_ = F.pad(input_, (0, padw, 0, padh), "reflect")

    with torch.inference_mode():
        restored = model(input_)
    restored = restored[:, :, :h, :w]
    restored = torch.clamp(restored, 0, 1).squeeze(0).permute(1, 2, 0).detach().cpu().numpy()
    out = (restored * 255.0).clip(0, 255).astype(np.uint8)
    return Image.fromarray(out)
