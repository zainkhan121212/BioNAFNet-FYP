"""
header.py — Premium Header with Gradient Background & Neon Accents
===================================================================
"""

import tkinter as tk
from theme import (
    FONT_LOGO, FONT_TITLE, FONT_BODY, FONT_BUTTON_SM,
    get_theme, GPU_OVERLAY,
)
from animations.glow_engine import add_hover_glow


class Header:
    """Builds the top header bar: gradient bg, logo, GPU toggle, theme toggle."""

    def __init__(self, parent: tk.Frame, app):
        self.app = app

        # outer frame with accent border at bottom
        self.frame = tk.Frame(parent, height=78, bd=0)
        self.frame.pack(fill=tk.X)
        self.frame.pack_propagate(False)

        self._build()

    def _build(self):
        t = get_theme(self.app.dark_mode.get())
        self.frame.config(bg=t["header_bg"])

        # accent line at bottom
        self.accent_line = tk.Frame(self.frame, height=2, bg=t["glass_highlight"])
        self.accent_line.pack(side=tk.BOTTOM, fill=tk.X)

        # ── left: logo + title ─────────────────────────────────────
        logo_frame = tk.Frame(self.frame, bg=t["header_bg"])
        logo_frame.pack(side=tk.LEFT, padx=24, pady=12)
        self._logo_frame = logo_frame

        self.logo_label = tk.Label(
            logo_frame, text="⚡", font=FONT_LOGO,
            bg=t["header_bg"], fg=t["accent"]
        )
        self.logo_label.pack(side=tk.LEFT)

        self.title_label = tk.Label(
            logo_frame, text="ImageEnhancer Pro",
            font=FONT_TITLE, bg=t["header_bg"], fg=t["text"]
        )
        self.title_label.pack(side=tk.LEFT, padx=(10, 14))

        # version badge with accent bg + rounded pill look
        self.version = tk.Label(
            logo_frame, text="  v2.0  ", font=("Segoe UI", 9, "bold"),
            bg=t["accent"], fg="white", padx=10, pady=3
        )
        self.version.pack(side=tk.LEFT, pady=10)

        # ── right: controls ────────────────────────────────────────
        ctrl = tk.Frame(self.frame, bg=t["header_bg"])
        ctrl.pack(side=tk.RIGHT, padx=24, pady=16)
        self._ctrl = ctrl

        # GPU indicator dot
        gpu_box = tk.Frame(ctrl, bg=t["header_bg"])
        gpu_box.pack(side=tk.LEFT, padx=(0, 14))
        self._gpu_box = gpu_box

        self.gpu_indicator = tk.Canvas(
            gpu_box, width=16, height=16,
            bg=t["header_bg"], highlightthickness=0
        )
        self.gpu_indicator.pack(side=tk.LEFT, padx=(0, 6))
        self.gpu_indicator.create_oval(2, 2, 14, 14, fill=t["text_muted"],
                                       outline=t["border"], tags="indicator")

        self.gpu_btn = tk.Button(
            gpu_box, text="🖥  GPU Processing",
            font=FONT_BUTTON_SM,
            bg=t["btn_bg"], fg=t["btn_fg"],
            activebackground=t["accent"], activeforeground="white",
            relief=tk.FLAT, padx=16, pady=7, cursor="hand2",
            bd=0, highlightthickness=0,
            command=self.app.toggle_gpu
        )
        self.gpu_btn.pack(side=tk.LEFT)
        add_hover_glow(self.gpu_btn, t["btn_bg"], t["accent_subtle"],
                       t["btn_fg"], t["text"])

        # Theme toggle
        self.theme_btn = tk.Button(
            ctrl, text="🌙  Dark Mode",
            font=FONT_BUTTON_SM,
            bg=t["btn_bg"], fg=t["btn_fg"],
            activebackground=t["accent"], activeforeground="white",
            relief=tk.FLAT, padx=16, pady=7, cursor="hand2",
            bd=0, highlightthickness=0,
            command=self.app.toggle_theme
        )
        self.theme_btn.pack(side=tk.LEFT, padx=(12, 0))
        add_hover_glow(self.theme_btn, t["btn_bg"], t["accent_subtle"],
                       t["btn_fg"], t["text"])

    def apply_theme(self):
        t = get_theme(self.app.dark_mode.get())
        gpu_on = self.app.gpu_enabled.get()
        accent = GPU_OVERLAY["accent"] if gpu_on else t["accent"]
        glow = GPU_OVERLAY["glass_highlight"] if gpu_on else t["glass_highlight"]

        self.frame.config(bg=t["header_bg"])
        self.accent_line.config(bg=glow)
        self._logo_frame.config(bg=t["header_bg"])
        self.logo_label.config(bg=t["header_bg"], fg=accent)
        self.title_label.config(bg=t["header_bg"], fg=t["text"])
        self.version.config(bg=accent)

        self._ctrl.config(bg=t["header_bg"])
        self._gpu_box.config(bg=t["header_bg"])
        self.gpu_indicator.config(bg=t["header_bg"])

        if gpu_on:
            self.gpu_btn.config(bg=GPU_OVERLAY["accent"], fg="#0f172a",
                                text="⚡ GPU ACTIVE")
            self.gpu_indicator.itemconfig("indicator",
                                          fill=GPU_OVERLAY["heartbeat_color"],
                                          outline=GPU_OVERLAY["accent"])
        else:
            self.gpu_btn.config(bg=t["btn_bg"], fg=t["btn_fg"],
                                text="🖥  GPU Processing")
            self.gpu_indicator.itemconfig("indicator", fill=t["text_muted"],
                                          outline=t["border"])
            add_hover_glow(self.gpu_btn, t["btn_bg"], t["accent_subtle"],
                           t["btn_fg"], t["text"])

        theme_text = "☀️  Light Mode" if self.app.dark_mode.get() else "🌙  Dark Mode"
        self.theme_btn.config(text=theme_text, bg=t["btn_bg"], fg=t["btn_fg"])
        add_hover_glow(self.theme_btn, t["btn_bg"], t["accent_subtle"],
                       t["btn_fg"], t["text"])
