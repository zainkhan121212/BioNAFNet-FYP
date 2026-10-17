"""
sidebar_left.py — Frosted Glass Upload & Save Panel
=====================================================
"""

import os
import tkinter as tk
from tkinter import filedialog
from theme import (
    FONT_HEADING, FONT_BODY, FONT_SMALL, FONT_TINY,
    FONT_BUTTON, FONT_BUTTON_SM,
    get_theme, GPU_OVERLAY, GLASS_BORDER_W,
)
from animations.glow_engine import add_hover_glow


def _make_glass_card(parent, t, **kw):
    """Create a frame styled as a frosted glass panel."""
    f = tk.Frame(
        parent,
        bg=t["glass_bg"],
        highlightbackground=t["glass_border"],
        highlightthickness=GLASS_BORDER_W,
        **kw
    )
    return f


class SidebarLeft:
    WIDTH = 280

    def __init__(self, parent: tk.Frame, app):
        self.app = app
        self.frame = tk.Frame(parent, width=self.WIDTH, bg="")
        self.frame.pack(side=tk.LEFT, fill=tk.Y, padx=(8, 4), pady=6)
        self.frame.pack_propagate(False)
        self._build()

    def _build(self):
        t = get_theme(self.app.dark_mode.get())
        self.frame.config(bg=t["bg"])

        # ── Upload Card ────────────────────────────────────────────
        self.upload_card = _make_glass_card(self.frame, t)
        self.upload_card.pack(fill=tk.X, padx=4, pady=(0, 6))

        # top highlight line
        tk.Frame(self.upload_card, height=2, bg=t["glass_highlight"]).pack(
            fill=tk.X
        )

        pad = tk.Frame(self.upload_card, bg=t["glass_bg"])
        pad.pack(fill=tk.X, padx=14, pady=14)
        self._upload_pad = pad

        self.upload_icon = tk.Label(
            pad, text="📁", font=("Segoe UI", 22),
            bg=t["glass_bg"], fg=t["accent"]
        )
        self.upload_icon.pack(anchor=tk.W)

        self.upload_title = tk.Label(
            pad, text="Upload Images", font=FONT_HEADING,
            bg=t["glass_bg"], fg=t["text"], anchor=tk.W
        )
        self.upload_title.pack(fill=tk.X, pady=(4, 2))

        self.upload_sub = tk.Label(
            pad, text="Select low-light images to enhance",
            font=FONT_TINY, bg=t["glass_bg"], fg=t["text_muted"], anchor=tk.W
        )
        self.upload_sub.pack(fill=tk.X, pady=(0, 10))

        self.upload_btn = tk.Button(
            pad, text="＋  Upload Images", font=FONT_BUTTON,
            bg=t["accent"], fg="white",
            activebackground=t["accent_hover"], activeforeground="white",
            relief=tk.FLAT, padx=14, pady=10, cursor="hand2",
            bd=0, highlightthickness=0,
            command=self.app.upload_images
        )
        self.upload_btn.pack(fill=tk.X, pady=(0, 6))

        self.counter = tk.Label(
            pad, text="0 images loaded", font=FONT_SMALL,
            bg=t["glass_bg"], fg=t["text_muted"], anchor=tk.W
        )
        self.counter.pack(fill=tk.X)

        # ── Save Card ─────────────────────────────────────────────
        self.save_card = _make_glass_card(self.frame, t)
        self.save_card.pack(fill=tk.X, padx=4, pady=(0, 6))

        tk.Frame(self.save_card, height=2, bg=t["glass_highlight"]).pack(fill=tk.X)

        spad = tk.Frame(self.save_card, bg=t["glass_bg"])
        spad.pack(fill=tk.X, padx=14, pady=14)
        self._save_pad = spad

        tk.Label(
            spad, text="💾", font=("Segoe UI", 22),
            bg=t["glass_bg"], fg=t["success"]
        ).pack(anchor=tk.W)

        tk.Label(
            spad, text="Save Results", font=FONT_HEADING,
            bg=t["glass_bg"], fg=t["text"], anchor=tk.W
        ).pack(fill=tk.X, pady=(4, 8))

        self.path_display = tk.Label(
            spad, text="No save location selected", font=FONT_TINY,
            bg=t["card"], fg=t["text_muted"],
            wraplength=220, padx=8, pady=6, anchor=tk.W
        )
        self.path_display.pack(fill=tk.X, pady=(0, 6))

        self.browse_btn = tk.Button(
            spad, text="📂  Choose Folder", font=FONT_BUTTON_SM,
            bg=t["btn_bg"], fg=t["btn_fg"],
            relief=tk.FLAT, padx=12, pady=7, cursor="hand2",
            bd=0, highlightthickness=0,
            command=self.app.choose_save_location
        )
        self.browse_btn.pack(fill=tk.X, pady=2)
        add_hover_glow(self.browse_btn, t["btn_bg"], t["btn_hover_bg"],
                       t["btn_fg"], t["btn_fg"])

        self.new_folder_btn = tk.Button(
            spad, text="📁  Create New Folder", font=FONT_BUTTON_SM,
            bg=t["btn_bg"], fg=t["btn_fg"],
            relief=tk.FLAT, padx=12, pady=7, cursor="hand2",
            bd=0, highlightthickness=0,
            command=self.app.create_new_folder
        )
        self.new_folder_btn.pack(fill=tk.X, pady=2)
        add_hover_glow(self.new_folder_btn, t["btn_bg"], t["btn_hover_bg"],
                       t["btn_fg"], t["btn_fg"])

        self.save_btn = tk.Button(
            spad, text="💾  Save Enhanced", font=FONT_BUTTON,
            bg=t["success"], fg="white",
            activebackground=t["success_hover"], activeforeground="white",
            relief=tk.FLAT, padx=12, pady=10, cursor="hand2",
            bd=0, highlightthickness=0,
            command=self.app.save_images
        )
        self.save_btn.pack(fill=tk.X, pady=(6, 0))

        # ── Image List Card ────────────────────────────────────────
        self.list_card = _make_glass_card(self.frame, t)
        self.list_card.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))

        tk.Frame(self.list_card, height=2, bg=t["glass_highlight"]).pack(fill=tk.X)

        lpad = tk.Frame(self.list_card, bg=t["glass_bg"])
        lpad.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)
        self._list_pad = lpad

        tk.Label(
            lpad, text="📋  Uploaded Files", font=FONT_HEADING,
            bg=t["glass_bg"], fg=t["text"], anchor=tk.W
        ).pack(fill=tk.X, pady=(0, 6))

        scroll = tk.Scrollbar(lpad, troughcolor=t["bg"])
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.list_canvas = tk.Canvas(
            lpad, bg=t["glass_bg"], highlightthickness=0,
            yscrollcommand=scroll.set
        )
        self.list_canvas.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self.list_canvas.yview)

        self.image_list_frame = tk.Frame(self.list_canvas, bg=t["glass_bg"])
        self.list_canvas.create_window(
            (0, 0), window=self.image_list_frame, anchor=tk.NW, width=220
        )
        self.image_list_frame.bind(
            "<Configure>",
            lambda e: self.list_canvas.configure(
                scrollregion=self.list_canvas.bbox("all")
            ),
        )

    def update_counter(self, n: int):
        self.counter.config(text=f"{n} image{'s' if n != 1 else ''} loaded")

    def add_item(self, filepath: str, remove_cb):
        t = get_theme(self.app.dark_mode.get())
        fname = os.path.basename(filepath)
        row = tk.Frame(
            self.image_list_frame, bg=t["card"],
            highlightbackground=t["border"], highlightthickness=1
        )
        row.pack(fill=tk.X, pady=2)

        short = fname if len(fname) <= 22 else fname[:19] + "..."
        tk.Label(
            row, text=f"📷  {short}", font=FONT_TINY,
            bg=t["card"], fg=t["text"], anchor=tk.W
        ).pack(side=tk.LEFT, padx=6, pady=4)

        tk.Button(
            row, text="✕", font=("Segoe UI", 8, "bold"),
            bg=t["card"], fg=t["danger"], relief=tk.FLAT, cursor="hand2",
            bd=0, highlightthickness=0,
            command=lambda: remove_cb(filepath, row)
        ).pack(side=tk.RIGHT, padx=4)

    def apply_theme(self):
        t = get_theme(self.app.dark_mode.get())
        gpu = self.app.gpu_enabled.get()
        border = GPU_OVERLAY["glass_border"] if gpu else t["glass_border"]
        highlight = GPU_OVERLAY["glass_highlight"] if gpu else t["glass_highlight"]

        self.frame.config(bg=t["bg"])
        for card in (self.upload_card, self.save_card, self.list_card):
            card.config(bg=t["glass_bg"], highlightbackground=border)
        # update all highlight lines (first child of each card)
        for card in (self.upload_card, self.save_card, self.list_card):
            children = card.winfo_children()
            if children:
                try:
                    children[0].config(bg=highlight)
                except tk.TclError:
                    pass
        # update pad backgrounds
        for pad in (self._upload_pad, self._save_pad, self._list_pad):
            pad.config(bg=t["glass_bg"])
            for w in pad.winfo_children():
                try:
                    w.config(bg=t["glass_bg"])
                except tk.TclError:
                    pass

        self.upload_btn.config(bg=GPU_OVERLAY["accent"] if gpu else t["accent"])
        self.counter.config(bg=t["glass_bg"], fg=t["text_muted"])
        self.path_display.config(bg=t["card"], fg=t["text_muted"])
        self.browse_btn.config(bg=t["btn_bg"], fg=t["btn_fg"])
        self.new_folder_btn.config(bg=t["btn_bg"], fg=t["btn_fg"])
        self.save_btn.config(bg=t["success"])
        self.list_canvas.config(bg=t["glass_bg"])
        self.image_list_frame.config(bg=t["glass_bg"])
