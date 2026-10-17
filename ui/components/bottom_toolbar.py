"""
bottom_toolbar.py — Quick Tools Bar with Glass Styling
========================================================
"""

import tkinter as tk
from theme import (
    FONT_SUBHEADING, FONT_BUTTON_SM, FONT_BODY,
    get_theme, GPU_OVERLAY, GLASS_BORDER_W,
)
from animations.glow_engine import add_hover_glow


class BottomToolbar:
    def __init__(self, parent: tk.Frame, app):
        self.app = app
        self.frame = tk.Frame(parent, height=70)
        self.frame.pack(fill=tk.X, padx=12, pady=(0, 8))
        self.frame.pack_propagate(False)
        self._build()

    def _build(self):
        t = get_theme(self.app.dark_mode.get())
        self.frame.config(
            bg=t["glass_bg"],
            highlightbackground=t["glass_border"],
            highlightthickness=GLASS_BORDER_W
        )

        # top highlight
        self.top_line = tk.Frame(self.frame, height=2, bg=t["glass_highlight"])
        self.top_line.pack(fill=tk.X)

        inner = tk.Frame(self.frame, bg=t["glass_bg"])
        inner.pack(fill=tk.BOTH, expand=True, padx=16)
        self._inner = inner

        self.tools_lbl = tk.Label(
            inner, text="🔧  Quick Tools:",
            font=FONT_SUBHEADING, bg=t["glass_bg"], fg=t["text"]
        )
        self.tools_lbl.pack(side=tk.LEFT, padx=(4, 16), pady=16)

        tools = [
            ("📐  Resizing",          self.app.open_resizing),
            ("✂️  Cropping",           self.app.open_cropping),
            ("🔄  Data Augmentation",  self.app.open_augmentation),
        ]
        self.tool_btns = []
        for text, cmd in tools:
            btn = tk.Button(
                inner, text=text, font=FONT_BUTTON_SM,
                bg=t["btn_bg"], fg=t["btn_fg"],
                activebackground=t["accent"], activeforeground="white",
                relief=tk.FLAT, padx=16, pady=8, cursor="hand2",
                bd=0, highlightthickness=0,
                command=cmd
            )
            btn.pack(side=tk.LEFT, padx=6, pady=14)
            add_hover_glow(btn, t["btn_bg"], t["accent_subtle"],
                           t["btn_fg"], t["text"])
            self.tool_btns.append(btn)

        # status
        sf = tk.Frame(inner, bg=t["glass_bg"])
        sf.pack(side=tk.RIGHT, padx=8, pady=16)
        self._sf = sf

        self.dot = tk.Canvas(
            sf, width=14, height=14, bg=t["glass_bg"], highlightthickness=0
        )
        self.dot.pack(side=tk.LEFT, padx=(0, 6))
        self.dot.create_oval(2, 2, 12, 12, fill=t["success"], outline="",
                             tags="dot")

        self.status_lbl = tk.Label(
            sf, text="Ready", font=FONT_BODY,
            bg=t["glass_bg"], fg=t["text_secondary"]
        )
        self.status_lbl.pack(side=tk.LEFT)

    def set_status(self, text, color=None):
        t = get_theme(self.app.dark_mode.get())
        self.status_lbl.config(text=text)
        dot_col = color or (
            GPU_OVERLAY["accent"] if self.app.gpu_enabled.get() else t["success"]
        )
        self.dot.itemconfig("dot", fill=dot_col)

    def apply_theme(self):
        t = get_theme(self.app.dark_mode.get())
        gpu = self.app.gpu_enabled.get()
        border = GPU_OVERLAY["glass_border"] if gpu else t["glass_border"]
        highlight = GPU_OVERLAY["glass_highlight"] if gpu else t["glass_highlight"]

        self.frame.config(bg=t["glass_bg"], highlightbackground=border)
        self.top_line.config(bg=highlight)
        self._inner.config(bg=t["glass_bg"])
        self.tools_lbl.config(bg=t["glass_bg"], fg=t["text"])
        for btn in self.tool_btns:
            btn.config(bg=t["btn_bg"], fg=t["btn_fg"])
            add_hover_glow(btn, t["btn_bg"], t["accent_subtle"],
                           t["btn_fg"], t["text"])
        self._sf.config(bg=t["glass_bg"])
        self.dot.config(bg=t["glass_bg"])
        self.status_lbl.config(bg=t["glass_bg"], fg=t["text_secondary"])
        dot_col = GPU_OVERLAY["accent"] if gpu else t["success"]
        self.dot.itemconfig("dot", fill=dot_col)
