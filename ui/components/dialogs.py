"""
dialogs.py — Styled Popup Dialogs (Resize, Crop, Augmentation)
================================================================
"""

import tkinter as tk
from theme import (
    FONT_HEADING, FONT_BODY, FONT_SMALL, FONT_BUTTON,
    get_theme,
)


def _dialog_base(parent, title_text: str, emoji: str, w=440, h=360):
    """Create a themed top-level dialog and return (dialog, content_frame)."""
    t = get_theme(parent.dark_mode.get() if hasattr(parent, "dark_mode") else False)

    dlg = tk.Toplevel(parent)
    dlg.title(title_text)
    dlg.geometry(f"{w}x{h}")
    dlg.transient(parent)
    dlg.config(bg=t["sidebar"])
    dlg.grab_set()

    # header
    tk.Label(
        dlg, text=f"{emoji}  {title_text}",
        font=("Segoe UI", 17, "bold"),
        bg=t["sidebar"], fg=t["text"]
    ).pack(pady=(22, 10))

    # content frame
    content = tk.Frame(dlg, bg=t["sidebar"])
    content.pack(fill=tk.BOTH, expand=True, padx=24)

    return dlg, content, t


def _apply_btn(parent_frame, t, text, command):
    btn = tk.Button(
        parent_frame, text=text, font=FONT_BUTTON,
        bg=t["accent"], fg="white",
        activebackground=t["accent_hover"], activeforeground="white",
        relief=tk.FLAT, padx=28, pady=10, cursor="hand2",
        command=command
    )
    btn.pack(pady=(16, 20))
    return btn


# ══════════════════════════════════════════════════════════════════
# Resize Dialog
# ══════════════════════════════════════════════════════════════════
def open_resize_dialog(app):
    dlg, body, t = _dialog_base(app, "Image Resizing", "📐", 420, 330)

    row1 = tk.Frame(body, bg=t["sidebar"])
    row1.pack(pady=8)
    tk.Label(row1, text="Width:", font=FONT_BODY,
             bg=t["sidebar"], fg=t["text"]).pack(side=tk.LEFT, padx=8)
    w_entry = tk.Entry(row1, font=FONT_BODY, width=8,
                       bg=t["bg"], fg=t["text"],
                       insertbackground=t["text"])
    w_entry.pack(side=tk.LEFT)
    w_entry.insert(0, "800")
    tk.Label(row1, text="px", font=FONT_SMALL,
             bg=t["sidebar"], fg=t["text_muted"]).pack(side=tk.LEFT, padx=4)

    row2 = tk.Frame(body, bg=t["sidebar"])
    row2.pack(pady=8)
    tk.Label(row2, text="Height:", font=FONT_BODY,
             bg=t["sidebar"], fg=t["text"]).pack(side=tk.LEFT, padx=8)
    h_entry = tk.Entry(row2, font=FONT_BODY, width=8,
                       bg=t["bg"], fg=t["text"],
                       insertbackground=t["text"])
    h_entry.pack(side=tk.LEFT)
    h_entry.insert(0, "600")
    tk.Label(row2, text="px", font=FONT_SMALL,
             bg=t["sidebar"], fg=t["text_muted"]).pack(side=tk.LEFT, padx=4)

    aspect = tk.BooleanVar(value=True)
    tk.Checkbutton(
        body, text="  Maintain aspect ratio", variable=aspect,
        font=FONT_BODY, bg=t["sidebar"], fg=t["text"],
        selectcolor=t["accent"], activebackground=t["sidebar"]
    ).pack(pady=10)

    _apply_btn(body, t, "Apply Resize", dlg.destroy)


# ══════════════════════════════════════════════════════════════════
# Crop Dialog
# ══════════════════════════════════════════════════════════════════
def open_crop_dialog(app):
    dlg, body, t = _dialog_base(app, "Image Cropping", "✂️", 480, 380)

    tk.Label(body, text="Aspect Ratio Presets", font=FONT_BODY,
             bg=t["sidebar"], fg=t["text"]).pack(anchor=tk.W, pady=(4, 6))

    rf = tk.Frame(body, bg=t["sidebar"])
    rf.pack(pady=4)
    for ratio, name in [("1:1", "Square"), ("16:9", "Wide"),
                         ("4:3", "Std"), ("3:2", "Photo")]:
        tk.Button(
            rf, text=f"{ratio}\n{name}", font=FONT_SMALL,
            width=8, bg=t["btn_bg"], fg=t["btn_fg"], relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=4)

    tk.Label(body, text="Custom Dimensions", font=FONT_BODY,
             bg=t["sidebar"], fg=t["text"]).pack(anchor=tk.W, pady=(12, 4))

    cf = tk.Frame(body, bg=t["sidebar"])
    cf.pack(pady=4)
    for lbl in ("X:", "Y:", "W:", "H:"):
        tk.Label(cf, text=lbl, font=FONT_SMALL,
                 bg=t["sidebar"], fg=t["text_muted"]).pack(side=tk.LEFT, padx=3)
        tk.Entry(cf, font=FONT_SMALL, width=5,
                 bg=t["bg"], fg=t["text"],
                 insertbackground=t["text"]).pack(side=tk.LEFT, padx=2)

    _apply_btn(body, t, "Apply Crop", dlg.destroy)


# ══════════════════════════════════════════════════════════════════
# Augmentation Dialog
# ══════════════════════════════════════════════════════════════════
def open_augmentation_dialog(app):
    dlg, body, t = _dialog_base(app, "Data Augmentation", "🔄", 460, 440)

    augs = [
        ("Horizontal Flip", True),
        ("Vertical Flip", False),
        ("Random Rotation", True),
        ("Brightness Adjustment", True),
        ("Noise Addition", False),
        ("Blur Effect", False),
        ("Color Jitter", True),
    ]
    app._aug_vars = {}
    for name, default in augs:
        var = tk.BooleanVar(value=default)
        app._aug_vars[name] = var
        tk.Checkbutton(
            body, text=f"  {name}", variable=var,
            font=FONT_BODY, bg=t["sidebar"], fg=t["text"],
            selectcolor=t["accent"], activebackground=t["sidebar"],
            anchor=tk.W
        ).pack(fill=tk.X, pady=2)

    row = tk.Frame(body, bg=t["sidebar"])
    row.pack(pady=12)
    tk.Label(row, text="Variations per image:", font=FONT_BODY,
             bg=t["sidebar"], fg=t["text"]).pack(side=tk.LEFT)
    sp = tk.Spinbox(row, from_=1, to=10, width=4, font=FONT_BODY,
                    bg=t["bg"], fg=t["text"])
    sp.pack(side=tk.LEFT, padx=8)
    sp.delete(0, tk.END)
    sp.insert(0, "3")

    _apply_btn(body, t, "Generate Augmented Data", dlg.destroy)
