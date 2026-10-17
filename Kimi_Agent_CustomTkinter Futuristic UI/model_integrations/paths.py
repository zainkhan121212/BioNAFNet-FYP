from __future__ import annotations

import os
from pathlib import Path


def ui_root() -> Path:
    # This file lives in: <UI_ROOT>/model_integrations/paths.py
    return Path(__file__).resolve().parents[1]


def weights_root() -> Path:
    return ui_root() / "weights"


def require_file(path: Path, hint: str) -> Path:
    if path.exists():
        return path
    raise FileNotFoundError(
        f"Required weights file not found: {path}\n\n"
        f"{hint}\n"
        f"Expected location is inside: {weights_root()}"
    )

