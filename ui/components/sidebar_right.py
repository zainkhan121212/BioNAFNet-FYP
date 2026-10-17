"""
sidebar_right.py — Model Selection with Glow Cards & Enhance Button
=====================================================================
"""

import tkinter as tk
from theme import (
    FONT_HEADING, FONT_BODY, FONT_SMALL, FONT_BUTTON_SM,
    FONT_ENHANCE_BTN, get_theme, GPU_OVERLAY, GLASS_BORDER_W,
)
from animations.glow_engine import add_hover_glow
from utils.image_processing import MODELS


MODEL_DESCRIPTIONS = {
    "A": "Matrix Format: Advanced matrix-based\nenhancement — optimized for\nlow-light recovery.",
    "B": "Zero DCE: Deep Curve Estimation\nfor adaptive enhancement without\npaired supervision.",
    "C": "R1 Model: Retinex-inspired single-\nstage enhancement with sharpness.",
    "D": "Deep Retinex: Decomposition-based\nenhancement via illumination\nand reflectance.",
    "E": "EnlightenGAN: Unpaired adversarial\nfor realistic illumination\ncorrection.",
    "F": "SCI Model: Self-Calibrated\nIllumination for robust low-light\nenhancement.",
    "G": "URetinex-Net: Unfolding Retinex\nfor joint denoising and contrast.",
}

MODEL_ICONS = {"A": "🔢", "B": "⚡", "C": "🎯", "D": "🔬",
               "E": "🧠", "F": "📊", "G": "🌐"}


class SidebarRight:
    WIDTH = 260

    def __init__(self, parent: tk.Frame, app):
        self.app = app
        self.frame = tk.Frame(parent, width=self.WIDTH)
        self.frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(4, 8), pady=6)
        self.frame.pack_propagate(False)

        self.model_btns: dict[str, tk.Button] = {}
        self._build()

    def _build(self):
        t = get_theme(self.app.dark_mode.get())
        self.frame.config(bg=t["bg"])

        # ── models card ────────────────────────────────────────────
        self.models_card = tk.Frame(
            self.frame, bg=t["glass_bg"],
            highlightbackground=t["glass_border"],
            highlightthickness=GLASS_BORDER_W
        )
        self.models_card.pack(fill=tk.X, padx=4, pady=(0, 6))

        self.top_line = tk.Frame(self.models_card, height=2, bg=t["glass_highlight"])
        self.top_line.pack(fill=tk.X)

        mpad = tk.Frame(self.models_card, bg=t["glass_bg"])
        mpad.pack(fill=tk.X, padx=14, pady=14)
        self._mpad = mpad

        tk.Label(
            mpad, text="🤖", font=("Segoe UI", 22),
            bg=t["glass_bg"], fg=t["accent"]
        ).pack(anchor=tk.W)

        self.title = tk.Label(
            mpad, text="Enhancement Models", font=FONT_HEADING,
            bg=t["glass_bg"], fg=t["text"], anchor=tk.W
        )
        self.title.pack(fill=tk.X, pady=(4, 2))

        self.subtitle = tk.Label(
            mpad, text="Select AI model for processing",
            font=("Segoe UI", 9), bg=t["glass_bg"], fg=t["text_muted"], anchor=tk.W
        )
        self.subtitle.pack(fill=tk.X, pady=(0, 10))

        # model buttons
        for letter, (name, _fn) in MODELS.items():
            icon = MODEL_ICONS.get(letter, "")
            btn = tk.Button(
                mpad, text=f"  {icon}  {letter}.  {name}",
                font=FONT_BUTTON_SM,
                bg=t["model_default_bg"], fg=t["model_default_fg"],
                activebackground=t["accent"], activeforeground="white",
                relief=tk.FLAT, padx=10, pady=7, cursor="hand2",
                anchor=tk.W, bd=0, highlightthickness=0,
                command=lambda l=letter: self._select(l)
            )
            btn.pack(fill=tk.X, pady=2)
            self.model_btns[letter] = btn

        self._highlight(self.app.selected_model.get())

        # ── enhance card ───────────────────────────────────────────
        self.enhance_card = tk.Frame(
            self.frame, bg=t["glass_bg"],
            highlightbackground=t["glass_border"],
            highlightthickness=GLASS_BORDER_W
        )
        self.enhance_card.pack(fill=tk.X, padx=4, pady=(0, 6))

        self.enhance_line = tk.Frame(self.enhance_card, height=2, bg=t["accent"])
        self.enhance_line.pack(fill=tk.X)

        epad = tk.Frame(self.enhance_card, bg=t["glass_bg"])
        epad.pack(fill=tk.X, padx=14, pady=14)
        self._epad = epad

        self.enhance_btn = tk.Button(
            epad, text="✨  ENHANCE NOW", font=FONT_ENHANCE_BTN,
            bg=t["accent"], fg="white",
            activebackground=t["accent_hover"], activeforeground="white",
            relief=tk.FLAT, padx=18, pady=14, cursor="hand2",
            bd=0, highlightthickness=0,
            command=self.app.enhance_images
        )
        self.enhance_btn.pack(fill=tk.X, pady=(0, 8))

        self.progress = tk.Label(
            epad, text="Ready to enhance", font=FONT_SMALL,
            bg=t["glass_bg"], fg=t["text_secondary"]
        )
        self.progress.pack(fill=tk.X)

        # ── model info card ────────────────────────────────────────
        self.info_card = tk.Frame(
            self.frame, bg=t["glass_bg"],
            highlightbackground=t["glass_border"],
            highlightthickness=GLASS_BORDER_W
        )
        self.info_card.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))

        self.info_line = tk.Frame(self.info_card, height=2, bg=t["glass_highlight"])
        self.info_line.pack(fill=tk.X)

        ipad = tk.Frame(self.info_card, bg=t["glass_bg"])
        ipad.pack(fill=tk.X, padx=14, pady=10)
        self._ipad = ipad

        self.info_title = tk.Label(
            ipad, text="ℹ️  Model Info", font=("Segoe UI", 12, "bold"),
            bg=t["glass_bg"], fg=t["text"], anchor=tk.W
        )
        self.info_title.pack(fill=tk.X)

        self.info_text = tk.Label(
            ipad, text=MODEL_DESCRIPTIONS["A"],
            font=FONT_SMALL, bg=t["glass_bg"], fg=t["text_secondary"],
            wraplength=210, justify=tk.LEFT, anchor=tk.NW
        )
        self.info_text.pack(fill=tk.X, pady=6)

    def _select(self, letter):
        self.app.selected_model.set(letter)
        self._highlight(letter)
        self.info_text.config(text=MODEL_DESCRIPTIONS.get(letter, ""))
        name = MODELS[letter][0]
        self.app.set_status(f"Model {letter} selected — {name}")

    def _highlight(self, letter):
        t = get_theme(self.app.dark_mode.get())
        gpu = self.app.gpu_enabled.get()
        accent = GPU_OVERLAY["model_selected"] if gpu else t["model_selected"]
        for l, btn in self.model_btns.items():
            if l == letter:
                btn.config(bg=accent, fg="white")
            else:
                btn.config(bg=t["model_default_bg"], fg=t["model_default_fg"])
                add_hover_glow(btn, t["model_default_bg"], t["btn_hover_bg"],
                               t["model_default_fg"], t["text"])

    def apply_theme(self):
        t = get_theme(self.app.dark_mode.get())
        gpu = self.app.gpu_enabled.get()
        border = GPU_OVERLAY["glass_border"] if gpu else t["glass_border"]
        highlight = GPU_OVERLAY["glass_highlight"] if gpu else t["glass_highlight"]
        accent = GPU_OVERLAY["accent"] if gpu else t["accent"]

        self.frame.config(bg=t["bg"])
        for card in (self.models_card, self.enhance_card, self.info_card):
            card.config(bg=t["glass_bg"], highlightbackground=border)
        self.top_line.config(bg=highlight)
        self.enhance_line.config(bg=accent)
        self.info_line.config(bg=highlight)

        for pad in (self._mpad, self._epad, self._ipad):
            pad.config(bg=t["glass_bg"])
            for w in pad.winfo_children():
                try:
                    w.config(bg=t["glass_bg"])
                except tk.TclError:
                    pass

        self._highlight(self.app.selected_model.get())
        self.enhance_btn.config(bg=accent)
        self.progress.config(bg=t["glass_bg"], fg=t["text_secondary"])
        self.info_title.config(bg=t["glass_bg"], fg=t["text"])
        self.info_text.config(bg=t["glass_bg"], fg=t["text_secondary"])
