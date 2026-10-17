"""
header.py — Neumorphic Header
================================
Logo, GPU toggle pill, dark/light toggle — soft extruded style.
"""

import tkinter as tk
import theme as T
from neumorphic import neu_card, neu_button, hover_glow


class Header:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=T.BG, height=68)
        self.frame.pack(fill=tk.X)
        self.frame.pack_propagate(False)
        self._build()

    def _build(self):
        # Content row
        inner = tk.Frame(self.frame, bg=T.BG)
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self._inner = inner

        # ── Left: Logo ─────────────────────────────────────────────
        left = tk.Frame(inner, bg=T.BG)
        left.pack(side=tk.LEFT)
        self._left = left

        self.logo_icon = tk.Label(left, text="⬢", font=("Segoe UI", 26),
                                   bg=T.BG, fg=T.PURPLE)
        self.logo_icon.pack(side=tk.LEFT, padx=(0, 10))

        title_box = tk.Frame(left, bg=T.BG)
        title_box.pack(side=tk.LEFT)
        self._title_box = title_box

        self.title = tk.Label(title_box, text="PixelForge", font=T.FONT_LOGO,
                               bg=T.BG, fg=T.TEXT)
        self.title.pack(anchor=tk.W)

        self.subtitle = tk.Label(title_box, text="AI Image Enhancement Studio",
                                  font=T.FONT_MONO_SM, bg=T.BG, fg=T.TEXT3)
        self.subtitle.pack(anchor=tk.W)

        # Accent line
        accent_line = tk.Frame(self.frame, height=2, bg=T.PURPLE)
        accent_line.pack(side=tk.BOTTOM, fill=tk.X)
        self._accent_line = accent_line

        # ── Right: Controls ────────────────────────────────────────
        right = tk.Frame(inner, bg=T.BG)
        right.pack(side=tk.RIGHT)
        self._right = right

        # Processing badge (neumorphic pill)
        self.status_badge = tk.Label(
            right, text="  🖥  CPU Mode  ", font=T.FONT_TINY,
            bg=T.BG, fg=T.TEXT3, padx=12, pady=4
        )
        self.status_badge.pack(side=tk.LEFT, padx=6)

        # GPU toggle (purple accent when on)
        self.gpu_btn = tk.Label(
            right, text="  🖥  GPU OFF  ", font=T.FONT_BUTTON_SM,
            bg=T.BG, fg=T.TEXT2, cursor="hand2", padx=14, pady=6
        )
        self.gpu_btn.pack(side=tk.LEFT, padx=6)
        self.gpu_btn.bind("<Button-1>", lambda e: self.app.toggle_gpu())
        hover_glow(self.gpu_btn, T.BG, T.BG_LIGHT, T.TEXT2, T.TEXT)

        # Theme toggle
        self.theme_btn = tk.Label(
            right, text="🌙", font=("Segoe UI", 16),
            bg=T.BG, fg=T.AMBER, cursor="hand2", padx=8, pady=4
        )
        self.theme_btn.pack(side=tk.LEFT, padx=6)
        self.theme_btn.bind("<Button-1>", lambda e: self.app.toggle_theme())

    def apply_theme(self):
        gpu = self.app.gpu_enabled.get()

        # GPU button state
        if gpu:
            self.gpu_btn.config(text="  ⚡ GPU ON  ", bg=T.PURPLE, fg=T.TEXT)
            self.status_badge.config(text="  ⚡ CUDA Accelerated  ", fg=T.PURPLE)
            self.logo_icon.config(fg=T.PURPLE_GLOW)
            self._accent_line.config(bg=T.PURPLE_GLOW)
        else:
            self.gpu_btn.config(text="  🖥  GPU OFF  ", bg=T.BG, fg=T.TEXT2)
            hover_glow(self.gpu_btn, T.BG, T.BG_LIGHT, T.TEXT2, T.TEXT)
            self.status_badge.config(text="  🖥  CPU Mode  ", fg=T.TEXT3)
            self.logo_icon.config(fg=T.PURPLE)
            self._accent_line.config(bg=T.PURPLE)
